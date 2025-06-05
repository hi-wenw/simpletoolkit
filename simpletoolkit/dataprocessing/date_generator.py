# -*-coding: Utf-8 -*-
# @File : date_generator.py
# 作者: ShanFeng
# 时间：2024/3/28

from datetime import datetime, timedelta
from ..base.base_tool import BaseTool


class DateGeneratorTool(BaseTool):
    """日期生成工具，用于生成各种日期范围和格式"""

    def __init__(self, start_date=None, end_date=None, date_format='%Y%m%d', enable_log=True):
        """
        初始化日期生成器

        Args:
            start_date: 开始日期，格式需符合 date_format
            end_date: 结束日期，格式需符合 date_format
            date_format: 日期格式字符串，默认为 '%Y%m%d'
            enable_log: 是否启用日志记录
        """
        super().__init__()
        self._date_format = date_format
        self._start_date = str(start_date) if start_date else None
        self._end_date = str(end_date) if end_date else None
        self._start_date_obj = None
        self._end_date_obj = None
        self._enable_log = enable_log

        if start_date and end_date:
            self._init_date_objects()

        if self._enable_log:
            self._logger.info(
                f"日期生成器初始化完成 - 开始日期: {start_date}, 结束日期: {end_date}, 格式: {date_format}"
            )

    def configure(self, start_date=None, end_date=None, date_format=None, enable_log=None):
        """配置日期生成器参数"""
        if date_format is not None:
            self._date_format = date_format

        if start_date is not None:
            self._start_date = str(start_date)

        if end_date is not None:
            self._end_date = str(end_date)

        if enable_log is not None:
            self._enable_log = enable_log

        if self._start_date and self._end_date:
            self._init_date_objects()

        super().configure(
            start_date=self._start_date,
            end_date=self._end_date,
            date_format=self._date_format,
            enable_log=self._enable_log
        )

    def _init_date_objects(self):
        """初始化日期对象"""
        try:
            self._start_date_obj = datetime.strptime(self._start_date, self._date_format)
            self._end_date_obj = datetime.strptime(self._end_date, self._date_format)
        except ValueError as e:
            self._logger.error(f"日期格式错误: {e}")
            raise

    def generate_date_range(self):
        """生成从开始到结束的连续日期列表"""
        if not self._start_date_obj or not self._end_date_obj:
            raise ValueError("请先设置开始日期和结束日期")

        if self._enable_log:
            self._logger.info("生成连续日期列表")

        date_list = []
        current_date = self._start_date_obj

        while current_date <= self._end_date_obj:
            date_list.append(current_date.strftime(self._date_format))
            current_date += timedelta(days=1)

        return date_list

    def generate_monthly_ranges(self, include_next_month=True, three_part=False):
        """
        生成按月划分的日期范围列表

        Args:
            include_next_month: 是否包含下个月第一天作为结束
            three_part: 是否生成三元组格式 [开始, 当月最后一天, 下月第一天]

        Returns:
            日期范围列表，每个元素为 [开始日期, 结束日期] 或 [开始, 当月最后, 下月第一]
        """
        if not self._start_date_obj or not self._end_date_obj:
            raise ValueError("请先设置开始日期和结束日期")

        if self._enable_log:
            mode = "三元组" if three_part else "二元组"
            self._logger.info(f"生成按月划分的日期范围列表 ({mode}格式)")

        date_list = []
        current_date = self._start_date_obj

        while current_date <= self._end_date_obj:
            next_month_start = current_date.replace(day=1) + timedelta(days=32)
            next_month_start = next_month_start.replace(day=1)  # 获取下个月的第一天

            if next_month_start > self._end_date_obj:
                next_month_start = self._end_date_obj + timedelta(days=1)

            month_end = next_month_start - timedelta(days=1)  # 获取当月最后一天

            if three_part:
                date_list.append([
                    current_date.strftime(self._date_format),
                    month_end.strftime(self._date_format),
                    next_month_start.strftime(self._date_format)
                ])
            else:
                end_date = next_month_start if include_next_month else month_end
                date_list.append([
                    current_date.strftime(self._date_format),
                    end_date.strftime(self._date_format)
                ])

            current_date = next_month_start

        return date_list

    def generate_custom_ranges(self, interval_days, include_next_day=True, three_part=False):
        """
        生成按自定义间隔划分的日期范围列表

        Args:
            interval_days: 间隔天数
            include_next_day: 是否包含下一个周期的第一天作为结束
            three_part: 是否生成三元组格式 [开始, 周期最后一天, 下一周期第一天]

        Returns:
            日期范围列表
        """
        if not self._start_date_obj or not self._end_date_obj:
            raise ValueError("请先设置开始日期和结束日期")

        if interval_days <= 0:
            raise ValueError("间隔天数必须为正整数")

        if self._enable_log:
            mode = "三元组" if three_part else "二元组"
            self._logger.info(f"生成按{interval_days}天划分的日期范围列表 ({mode}格式)")

        date_list = []
        current_date = self._start_date_obj

        while current_date <= self._end_date_obj:
            next_date = current_date + timedelta(days=interval_days)

            if next_date > self._end_date_obj:
                next_date = self._end_date_obj + timedelta(days=1)

            period_end = next_date - timedelta(days=1)  # 周期的最后一天

            if three_part:
                date_list.append([
                    current_date.strftime(self._date_format),
                    period_end.strftime(self._date_format),
                    next_date.strftime(self._date_format)
                ])
            else:
                end_date = next_date if include_next_day else period_end
                date_list.append([
                    current_date.strftime(self._date_format),
                    end_date.strftime(self._date_format)
                ])

            current_date = next_date

        return date_list

    def generate_hourly_range(self):
        """生成按小时划分的时间范围列表"""
        if not self._start_date_obj or not self._end_date_obj:
            raise ValueError("请先设置开始日期和结束日期")

        if self._enable_log:
            self._logger.info("生成按小时划分的时间范围列表")

        date_list = []
        current_date = self._start_date_obj

        while current_date <= self._end_date_obj:
            date_list.append(current_date.strftime(self._date_format))
            current_date += timedelta(hours=1)

        return date_list

    @staticmethod
    def get_today(date_format='%Y%m%d'):
        """获取今天的日期"""
        return datetime.now().strftime(date_format)

    @staticmethod
    def get_yesterday(date_format='%Y%m%d'):
        """获取昨天的日期"""
        return (datetime.now() - timedelta(days=1)).strftime(date_format)

    @staticmethod
    def get_now(date_format='%Y%m%d%H%M%S'):
        """获取当前时间"""
        return datetime.now().strftime(date_format)

    @staticmethod
    def get_interval_days(interval, date_format='%Y%m%d'):
        """获取相对于今天间隔指定天数的日期"""
        return (datetime.now() + timedelta(days=interval)).strftime(date_format)