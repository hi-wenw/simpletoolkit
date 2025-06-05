# simpletoolkit/filesystems/excel_tools.py
import os

import pandas as pd
from ..base.base_tool import BaseTool


class ExcelTool(BaseTool):
    """Excel文件处理工具"""

    def merge_excel_sheets(self, excel_file, output_file, **options):
        """
        合并Excel文件中的多个sheet

        Args:
            excel_file: 输入Excel文件路径
            output_file: 输出文件路径
            **options: 可选参数
                sheet_names: 指定要合并的sheet名称列表，默认为全部
                ignore_index: 是否忽略原索引，默认为True
                header: 是否包含表头，默认为True
                sort_by: 按指定列排序，列表类型
                ascending: 排序方向，布尔值列表
        """
        sheet_names = options.get('sheet_names')
        ignore_index = options.get('ignore_index', True)
        header = options.get('header', True)
        sort_by = options.get('sort_by', None)
        ascending = options.get('ascending', True)

        self._logger.info(f"开始合并Excel文件 {excel_file} 中的多个sheet")

        try:
            # 读取Excel文件
            xls = pd.ExcelFile(excel_file)

            # 获取所有sheet名称
            if not sheet_names:
                sheet_names = xls.sheet_names
                self._logger.info(f"未指定sheet，将处理所有sheet: {sheet_names}")

            # 合并sheet
            dfs = []
            for sheet_name in sheet_names:
                try:
                    df = xls.parse(sheet_name)
                    if not df.empty:
                        df['sheet_name'] = sheet_name  # 添加sheet名称列
                        dfs.append(df)
                        self._logger.debug(f"已读取sheet: {sheet_name}，行数: {len(df)}")
                    else:
                        self._logger.warning(f"sheet {sheet_name} 为空，跳过")
                except Exception as e:
                    self._logger.error(f"读取sheet {sheet_name} 失败: {str(e)}")

            if not dfs:
                self._logger.error("没有可合并的有效数据")
                return False

            # 合并所有DataFrame
            merged_df = pd.concat(dfs, ignore_index=ignore_index)

            # 如果指定了排序
            if sort_by:
                merged_df = merged_df.sort_values(by=sort_by, ascending=ascending)
                self._logger.info(f"已按 {sort_by} 排序合并后的数据")

            # 根据输出文件扩展名选择保存方式
            if output_file.lower().endswith('.csv'):
                merged_df.to_csv(output_file, index=False, header=header)
                self._logger.success(f"已将合并结果保存为CSV: {output_file}")
            elif output_file.lower().endswith(('.xlsx', '.xls')):
                with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                    merged_df.to_excel(writer, sheet_name='Merged', index=False)
                self._logger.success(f"已将合并结果保存为Excel: {output_file}")
            else:
                self._logger.error(f"不支持的输出文件格式: {output_file}")
                return False

            return True

        except Exception as e:
            self._logger.error(f"合并Excel sheets失败: {str(e)}")
            raise
            return False

    def split_excel_to_csv(self, excel_file, output_dir='.', **options):
        """
        将Excel文件的多个sheet拆分为单独的CSV文件

        Args:
            excel_file: 输入Excel文件路径
            output_dir: 输出目录，默认为当前目录
            **options: 可选参数
                sheet_names: 指定要拆分的sheet名称列表，默认为全部
                prefix: 输出文件名前缀
                suffix: 输出文件名后缀
                na_rep: 缺失值表示，默认为nan
        """
        sheet_names = options.get('sheet_names')
        prefix = options.get('prefix', '')
        suffix = options.get('suffix', '')
        na_rep = options.get('na_rep', 'nan')

        self._logger.info(f"开始将Excel文件 {excel_file} 拆分为多个CSV文件")

        try:
            # 读取Excel文件
            xls = pd.ExcelFile(excel_file)

            # 获取所有sheet名称
            if not sheet_names:
                sheet_names = xls.sheet_names
                self._logger.info(f"未指定sheet，将处理所有sheet: {sheet_names}")

            # 获取Excel文件名（不包含路径和扩展名）
            excel_basename = os.path.basename(excel_file)
            excel_name = os.path.splitext(excel_basename)[0]

            # 为每个sheet创建CSV文件
            for sheet_name in sheet_names:
                try:
                    df = xls.parse(sheet_name)
                    if not df.empty:
                        # 构建安全的sheet名称，只保留字母数字和特定字符
                        safe_sheet_name = "".join([c for c in sheet_name if c.isalnum() or c in ('_', '-')])
                        # 构建输出文件名：excel表名__sheet名.csv
                        output_file = f"{output_dir}/{excel_name}__{safe_sheet_name}.csv"

                        # 保存为CSV
                        df.to_csv(output_file, index=False, na_rep=na_rep)
                        self._logger.info(f"已将sheet {sheet_name} 保存为CSV: {output_file}，行数: {len(df)}")
                    else:
                        self._logger.warning(f"sheet {sheet_name} 为空，跳过")
                except Exception as e:
                    self._logger.error(f"处理sheet {sheet_name} 失败: {str(e)}")

            return True

        except Exception as e:
            self._logger.error(f"拆分Excel为CSV失败: {str(e)}")
            raise


    def compare_excel(self, excel1, excel2, sheet1, sheet2, **options):
        """
        比较两个Excel文件的指定sheet

        Args:
            excel1: 第一个Excel文件路径
            excel2: 第二个Excel文件路径
            sheet1: 第一个Excel的sheet名称或索引
            sheet2: 第二个Excel的sheet名称或索引
            **options: 可选参数
                key_columns: 用于匹配行的键列，列表类型
                ignore_columns: 忽略比较的列，列表类型
                na_rep: 缺失值表示，默认为nan
        """
        key_columns = options.get('key_columns', [])
        ignore_columns = options.get('ignore_columns', [])
        na_rep = options.get('na_rep', 'nan')

        self._logger.info(f"开始比较Excel文件: {excel1} (sheet: {sheet1}) 和 {excel2} (sheet: {sheet2})")

        try:
            # 读取第一个Excel文件
            xls1 = pd.ExcelFile(excel1)
            df1 = xls1.parse(sheet1)
            self._logger.info(f"已读取第一个Excel的sheet {sheet1}，行数: {len(df1)}")

            # 读取第二个Excel文件
            xls2 = pd.ExcelFile(excel2)
            df2 = xls2.parse(sheet2)
            self._logger.info(f"已读取第二个Excel的sheet {sheet2}，行数: {len(df2)}")

            # 处理忽略列
            if ignore_columns:
                df1 = df1.drop(columns=[col for col in ignore_columns if col in df1.columns])
                df2 = df2.drop(columns=[col for col in ignore_columns if col in df2.columns])

            # 检查列是否一致
            if set(df1.columns) != set(df2.columns):
                self._logger.warning("两个sheet的列不一致")
                return {
                    'status': 'error',
                    'message': '列不一致',
                    'only_in_excel1': list(set(df1.columns) - set(df2.columns)),
                    'only_in_excel2': list(set(df2.columns) - set(df1.columns))
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
                    self._logger.info("两个sheet内容完全相同")
                    return {
                        'status': 'same',
                        'message': '内容完全相同',
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
                                    'excel1_value': df1.at[row_idx, col],
                                    'excel2_value': df2.at[row_idx, col]
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
                    self._logger.info("两个sheet内容完全相同")
                    return {
                        'status': 'same',
                        'message': '内容完全相同'
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
                        'excel1_value': df1.iloc[id_][col],
                        'excel2_value': df2.iloc[id_][col]
                    })

                self._logger.info(f"找到 {len(diff_values)} 处差异")
                return {
                    'status': 'different',
                    'message': f'找到 {len(diff_values)} 处差异',
                    'differences': diff_values
                }

        except Exception as e:
            self._logger.error(f"Excel比较失败: {str(e)}")
            raise