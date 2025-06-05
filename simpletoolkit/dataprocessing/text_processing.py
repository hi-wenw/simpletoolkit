from ..base.base_tool import BaseTool


class TextProcessingTool(BaseTool):
    """文本处理工具"""

    def escape_text(self, text):
        _escape_table = [chr(x) for x in range(128)]
        _escape_table[0] = "\\0"
        _escape_table[ord("\\")] = "\\\\"
        _escape_table[ord("\n")] = "\\n"
        _escape_table[ord("\r")] = "\\r"
        _escape_table[ord("\032")] = "\\Z"
        _escape_table[ord('"')] = '\\"'
        _escape_table[ord("'")] = "\\'"
        return text.translate(_escape_table)