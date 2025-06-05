# from simpletoolkit.cloud.huawei.obs_tools import HuaweiOBSTool
#
# obs = HuaweiOBSTool()
#
# obs.upload_csv_with_override("yishou-data",r"D:\gitData\simpletoolkit\README.md",r"hewenbao/readme.md")

from simpletoolkit import create_toolkit

tk = create_toolkit()

tk.filesystem.excel.split_excel_to_csv(r"F:\document\2025-05\高德_v2.xlsx")

tk.cloud.huawei.obs.upload_csv("yishou-data",r"D:\gitData\simpletoolkit\README.md",r"hewenbao/readme.md")


tk.data_processing.datetime.configure(
    start_date='20250501'
    ,end_date='20250604'
)

print(tk.data_processing.datetime.generate_date_range())
print(tk.data_processing.datetime.generate_custom_ranges(30))
print(tk.data_processing.datetime.generate_monthly_ranges(three_part=True))