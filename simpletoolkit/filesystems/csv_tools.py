# simpletoolkit/filesystems/csv_tools.py
import csv
import pandas as pd
from ..base.base_tool import BaseTool


class CSVTool(BaseTool):
    """CSV文件处理工具"""

    def compare_csv(self, file1, file2, **options):
        """
        比较两个CSV文件的内容

        Args:
            file1: 第一个CSV文件路径
            file2: 第二个CSV文件路径
            **options: 可选参数
                key_columns: 用于匹配行的键列，列表类型
                ignore_columns: 忽略比较的列，列表类型
                delimiter: CSV分隔符，默认为逗号
                encoding: 文件编码，默认为utf-8

        Returns:
            包含差异信息的字典
        """
        key_columns = options.get('key_columns', [])
        ignore_columns = options.get('ignore_columns', [])
        delimiter = options.get('delimiter', ',')
        encoding = options.get('encoding', 'utf-8')

        self._logger.info(f"开始比较CSV文件: {file1} 和 {file2}")

        try:
            # 读取文件
            df1 = pd.read_csv(file1, delimiter=delimiter, encoding=encoding)
            df2 = pd.read_csv(file2, delimiter=delimiter, encoding=encoding)

            # 处理忽略列
            if ignore_columns:
                df1 = df1.drop(columns=[col for col in ignore_columns if col in df1.columns])
                df2 = df2.drop(columns=[col for col in ignore_columns if col in df2.columns])

            # 检查列是否一致
            if set(df1.columns) != set(df2.columns):
                self._logger.warning("两个CSV文件的列不一致")
                return {
                    'status': 'error',
                    'message': '列不一致',
                    'only_in_file1': list(set(df1.columns) - set(df2.columns)),
                    'only_in_file2': list(set(df2.columns) - set(df1.columns))
                }

            # 如果指定了键列，则按键列比较
            if key_columns and all(col in df1.columns for col in key_columns):
                # 设置索引进行比较
                df1 = df1.set_index(key_columns)
                df2 = df2.set_index(key_columns)

                # 对齐索引
                df1, df2 = df1.align(df2, join='outer', fill_value=None)

                # 比较差异
                diff = df1 != df2
                diff_count = diff.sum().sum()

                if diff_count == 0:
                    self._logger.info("两个CSV文件内容完全相同")
                    return {
                        'status': 'same',
                        'message': '文件内容完全相同',
                        'differences': []
                    }

                # 获取不同的值
                diff_rows = []
                for row_idx, row in diff.iterrows():
                    if row.any():
                        row_diff = {
                            'key': row_idx,
                            'differences': {}
                        }
                        for col in df1.columns:
                            if row[col]:
                                row_diff['differences'][col] = {
                                    'file1_value': df1.at[row_idx, col],
                                    'file2_value': df2.at[row_idx, col]
                                }
                        diff_rows.append(row_diff)

                self._logger.info(f"找到 {len(diff_rows)} 行差异")
                return {
                    'status': 'different',
                    'message': f'找到 {len(diff_rows)} 行差异',
                    'differences': diff_rows
                }

            # 未指定键列时，直接比较整个数据框
            else:
                # 重置索引以确保正确比较
                df1 = df1.reset_index(drop=True)
                df2 = df2.reset_index(drop=True)

                # 比较
                if df1.equals(df2):
                    self._logger.info("两个CSV文件内容完全相同")
                    return {
                        'status': 'same',
                        'message': '文件内容完全相同'
                    }

                # 查找不同的行
                ne_stacked = (df1 != df2).stack()
                changed = ne_stacked[ne_stacked]
                changed.index.names = ['id', 'col']

                difference_locations = [(id_, col) for id_, col in changed.index]
                diff_values = []

                for id_, col in difference_locations:
                    diff_values.append({
                        'row': id_,
                        'column': col,
                        'file1_value': df1.iloc[id_][col],
                        'file2_value': df2.iloc[id_][col]
                    })

                self._logger.info(f"找到 {len(diff_values)} 处差异")
                return {
                    'status': 'different',
                    'message': f'找到 {len(diff_values)} 处差异',
                    'differences': diff_values
                }

        except Exception as e:
            self._logger.error(f"CSV比较失败: {str(e)}")
            raise

    def merge_csv_files(self, file_list, output_file, **options):
        """
        合并多个CSV文件

        Args:
            file_list: CSV文件路径列表
            output_file: 输出文件路径
            **options: 可选参数
                header: 是否包含表头，默认为True
                delimiter: CSV分隔符，默认为逗号
                encoding: 文件编码，默认为utf-8
                sort_by: 按指定列排序，列表类型
                ascending: 排序方向，布尔值列表
        """
        header = options.get('header', True)
        delimiter = options.get('delimiter', ',')
        encoding = options.get('encoding', 'utf-8')
        sort_by = options.get('sort_by', None)
        ascending = options.get('ascending', True)

        self._logger.info(f"开始合并 {len(file_list)} 个CSV文件到: {output_file}")

        try:
            # 创建输出文件并写入表头（如果需要）
            with open(output_file, 'w', newline='', encoding=encoding) as outfile:
                writer = None

                for file_path in file_list:
                    self._logger.debug(f"处理文件: {file_path}")

                    with open(file_path, 'r', encoding=encoding) as infile:
                        reader = csv.reader(infile, delimiter=delimiter)

                        # 获取表头
                        if writer is None:
                            headers = next(reader)
                            writer = csv.writer(outfile, delimiter=delimiter)

                            if header:
                                writer.writerow(headers)
                        else:
                            # 跳过后续文件的表头
                            next(reader, None)

                        # 写入数据行
                        for row in reader:
                            writer.writerow(row)

            # 如果指定了排序，读取并排序
            if sort_by:
                df = pd.read_csv(output_file, delimiter=delimiter, encoding=encoding)
                df = df.sort_values(by=sort_by, ascending=ascending)
                df.to_csv(output_file, index=False, sep=delimiter, encoding=encoding)
                self._logger.info(f"已按 {sort_by} 排序合并后的文件")

            self._logger.success(f"CSV文件合并成功")
            return True

        except Exception as e:
            self._logger.error(f"CSV合并失败: {str(e)}")
            raise
            return False

    def csv_to_excel(self, csv_file, excel_file, **options):
        """
        将CSV文件转换为Excel文件

        Args:
            csv_file: 输入CSV文件路径
            excel_file: 输出Excel文件路径
            **options: 可选参数
                delimiter: CSV分隔符，默认为逗号
                encoding: 文件编码，默认为utf-8
                sheet_name: Excel表名，默认为'Sheet1'
                na_rep: 缺失值表示，默认为nan
        """
        delimiter = options.get('delimiter', ',')
        encoding = options.get('encoding', 'utf-8')
        sheet_name = options.get('sheet_name', 'Sheet1')
        na_rep = options.get('na_rep', 'nan')

        self._logger.info(f"开始将CSV文件转换为Excel: {csv_file} -> {excel_file}")

        try:
            # 读取CSV文件
            df = pd.read_csv(csv_file, delimiter=delimiter, encoding=encoding)

            # 写入Excel文件
            with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name=sheet_name, index=False, na_rep=na_rep)

            self._logger.success(f"CSV转Excel成功")
            return True

        except Exception as e:
            self._logger.error(f"CSV转Excel失败: {str(e)}")
            raise
            return False