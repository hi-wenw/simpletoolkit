from .base.base_tool import BaseTool
from .filesystems.csv_tools import CSVTool
from .filesystems.excel_tools import ExcelTool
from .apis.tencent.image_search import TencentImageSearchTool
from .apis.huawei.obs_tools import HuaweiOBSTool
from .dataprocessing.text_processing import TextProcessingTool
from .dataprocessing.date_generator import DateGeneratorTool

__version__ = "0.1.0"


class SimpleToolkit:
    """SimpleToolkit主类，作为所有工具的统一入口"""

    def __init__(self):
        # 文件系统工具
        self.filesystem = FileSystemTools()

        # API集成工具
        self.apis = APITools()

        # 数据处理工具
        self.data_processing = DataProcessingTools()

    def configure_global(self, **kwargs):
        """配置所有工具的全局参数"""

        def _configure(obj):
            if isinstance(obj, BaseTool):
                obj.configure(**kwargs)
            else:
                for attr_name in dir(obj):
                    attr = getattr(obj, attr_name)
                    if isinstance(attr, (BaseTool, ToolContainer)):
                        _configure(attr)

        _configure(self)


# 工具容器基类 - 用于组织不同层级的工具
class ToolContainer:
    pass


# 文件系统工具容器
class FileSystemTools(ToolContainer):
    def __init__(self):
        self.csv = CSVTool()
        self.excel = ExcelTool()


# API工具容器
class APITools(ToolContainer):
    def __init__(self):
        self.tencent = TencentAPITools()
        self.huawei = HuaweiAPITools()


# 腾讯API工具容器
class TencentAPITools(ToolContainer):
    def __init__(self):
        self.image_search = TencentImageSearchTool()

# 华为API工具容器
class HuaweiAPITools(ToolContainer):
    def __init__(self):
        self.obs = HuaweiOBSTool()


# 数据处理工具容器
class DataProcessingTools(ToolContainer):
    def __init__(self):
        self.text = TextProcessingTool()
        self.date_generator = DateGeneratorTool()


# 创建工具包实例的工厂函数
def create_toolkit():
    return SimpleToolkit()