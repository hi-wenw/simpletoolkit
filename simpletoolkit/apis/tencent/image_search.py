from ...base.base_tool import BaseTool


class TencentImageSearchTool(BaseTool):
    """腾讯云图像搜索API工具"""

    def __init__(self, secret_id=None, secret_key=None, region=None):
        super().__init__()
        self._configure_tencent_cloud(secret_id, secret_key, region)

    def _configure_tencent_cloud(self, secret_id, secret_key, region):
        """配置腾讯云认证信息"""
        if secret_id and secret_key:
            self.configure(secret_id=secret_id, secret_key=secret_key, region=region)

    def search_by_image_url(self, image_url, group_ids=None, **options):
        """通过图片URL进行图像搜索"""
        pass

    def search_by_image_file(self, image_path, group_ids=None, **options):
        """通过本地图片文件进行图像搜索"""
        pass