from ..base.base_tool import BaseTool


class TextProcessingTool(BaseTool):
    """文本处理工具"""

    def translate_special_chars(self, text, translation_map=None):
        """转译特殊字符"""
        pass

    def clean_text(self, text, remove_stopwords=True, **options):
        """清理文本数据"""
        pass

    def extract_keywords(self, text, top_n=10, **options):
        """从文本中提取关键词"""
        pass