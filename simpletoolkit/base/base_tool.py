from loguru import logger as loguru_logger

# 定义敏感信息关键字
SENSITIVE_KEYWORDS = ['access_key', 'secret_key', 'secret_id']

class BaseTool:
    """所有工具类的基类，提供通用功能"""

    def __init__(self):
        self._config = {}
        self._logger = self._setup_logger()

    def configure(self, **kwargs):
        """配置工具参数"""
        self._config.update(kwargs)
        # 如果配置中包含日志相关参数，可以在这里更新日志设置

    def _setup_logger(self):
        """设置 loguru 日志记录器"""
        # 创建一个绑定了工具类名称的 logger 实例
        # 这样每个子类的日志都会显示其类名，便于追踪
        logger = loguru_logger.bind(tool=self.__class__.__name__)

        # 添加过滤器，过滤敏感信息
        def filter_sensitive(record):
            for keyword in SENSITIVE_KEYWORDS:
                if keyword in str(record["message"]):
                    return False
            return True

        logger.add(lambda record: None, filter=filter_sensitive)

        return logger

    def _validate_params(self, required_params, provided_params):
        """验证参数完整性"""
        for param in required_params:
            if param not in provided_params:
                self._logger.error(f"缺少必要参数: {param}")
                raise ValueError(f"缺少必要参数: {param}")