import os
from typing import Optional

from ...base.base_tool import BaseTool
from obs import ObsClient

# 环境变量提示信息
ENV_VARIABLE_HINT = "请确保已正确配置环境变量 'CLOUD_SDK_AK', 'CLOUD_SDK_SK' 和 'HUAWEI_REGION'。"


class HuaweiOBSTool(BaseTool):
    """华为云OBS存储服务工具（单例模式实现）"""

    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, access_key: Optional[str] = None,
                 secret_key: Optional[str] = None,
                 region: Optional[str] = None):
        if self._initialized:
            return  # 避免重复初始化

        super().__init__()
        self._access_key = None
        self._secret_key = None
        self._region = None
        self._server = None
        self._obs_client = None

        # 初始配置加载
        self.configure(access_key, secret_key, region)
        self._initialized = True

    @classmethod
    def get_instance(cls):
        """获取单例实例"""
        if not cls._instance:
            cls._instance = cls()
        return cls._instance

    def configure(self, access_key: Optional[str] = None,
                  secret_key: Optional[str] = None,
                  region: Optional[str] = None) -> 'HuaweiOBSTool':
        """配置华为云认证信息（支持链式调用）"""
        # 按优先级设置配置：参数 > 已有配置 > 环境变量 > 默认值
        self._access_key = access_key or self._access_key or os.getenv('CLOUD_SDK_AK')
        self._secret_key = secret_key or self._secret_key or os.getenv('CLOUD_SDK_SK')
        self._region = region or self._region or os.getenv('HUAWEI_REGION', 'cn-south-1')

        # 更新服务器地址
        if self._region:
            self._server = f'https://obs.{self._region}.myhuaweicloud.com'
        else:
            self._server = None
            self._logger.warning("未设置区域，服务器地址无法确定")

        # 验证配置完整性
        if not all([self._access_key, self._secret_key, self._region]):
            self._logger.warning(ENV_VARIABLE_HINT)

        # 重置客户端（下次使用时重新初始化）
        self._obs_client = None

        # 调用基类配置
        super().configure(
            access_key=self._access_key,
            secret_key=self._secret_key,
            region=self._region
        )

        return self  # 支持链式调用

    def _init_obs_client(self):
        """初始化OBS客户端（懒加载）"""
        if not all([self._access_key, self._secret_key, self._server]):
            raise ValueError("缺少必要的认证信息，无法初始化OBS客户端")

        try:
            self._obs_client = ObsClient(
                access_key_id=self._access_key,
                secret_access_key=self._secret_key,
                server=self._server
            )
            self._logger.info(f"OBS客户端初始化成功 - 区域: {self._region}")
        except Exception as e:
            self._logger.error(f"OBS客户端初始化失败: {str(e)}")
            self._obs_client = None
            raise

    @property
    def obs_client(self):
        """获取OBS客户端（懒加载）"""
        if self._obs_client is None:
            self._init_obs_client()
        return self._obs_client

    @staticmethod
    def upload_csv(bucket_name: str, file_path: str, object_key: str, delete_existing: bool = True) -> bool:
        """
        上传CSV文件到OBS，可选择是否删除已存在的同名文件

        Args:
            bucket_name: OBS存储桶名称
            file_path: 本地CSV文件路径
            object_key: OBS对象键
            delete_existing: 是否删除已存在的文件，默认为True
        """
        # 获取单例实例并执行上传
        instance = HuaweiOBSTool.get_instance()

        try:
            # 删除已存在的文件（如果需要）
            if delete_existing:
                delete_resp = instance.obs_client.deleteObject(bucket_name, object_key)
                if delete_resp.status < 300:
                    instance._logger.info(f"已删除现有文件: {object_key}")
                else:
                    instance._logger.warning(f"删除现有文件失败或文件不存在: {object_key}")

            # 上传新文件
            up_resp = instance.obs_client.putFile(bucket_name, object_key, file_path)

            # 检查上传结果
            if up_resp.status < 300:
                instance._logger.info(f"CSV文件上传成功 - 对象键: {object_key}")
                return True
            else:
                instance._logger.error(f"CSV文件上传失败 - 状态码: {up_resp.status}")
                return False

        except Exception as e:
            instance._logger.error(f"CSV文件上传异常: {str(e)}")
            raise

    def upload_file(self, local_path: str, bucket_name: str, object_key: str, **options) -> bool:
        """上传文件到OBS"""
        try:
            response = self.obs_client.putFile(bucket_name, object_key, local_path)
            if response.status < 300:
                self._logger.info(f"文件上传成功 - 桶: {bucket_name}, 对象: {object_key}")
                return True
            else:
                self._logger.error(f"文件上传失败 - 状态码: {response.status}")
                return False
        except Exception as e:
            self._logger.error(f"文件上传异常: {str(e)}")
            raise

    def download_file(self, bucket_name: str, object_key: str, local_path: str, **options) -> bool:
        """从OBS下载文件"""
        try:
            response = self.obs_client.getObject(bucket_name, object_key, downloadPath=local_path)
            if response.status < 300:
                self._logger.info(f"文件下载成功 - 桶: {bucket_name}, 对象: {object_key}")
                return True
            else:
                self._logger.error(f"文件下载失败 - 状态码: {response.status}")
                return False
        except Exception as e:
            self._logger.error(f"文件下载异常: {str(e)}")
            raise

    def list_objects(self, bucket_name: str, prefix: Optional[str] = None, **options) -> list:
        """列出OBS存储桶中的对象"""
        try:
            response = self.obs_client.listObjects(bucket_name, prefix=prefix)
            if response.status < 300 and hasattr(response.body, 'contents'):
                return [obj.key for obj in response.body.contents]
            else:
                self._logger.warning(f"列出对象失败或无内容 - 状态码: {response.status}")
                return []
        except Exception as e:
            self._logger.error(f"列出对象异常: {str(e)}")
            raise    