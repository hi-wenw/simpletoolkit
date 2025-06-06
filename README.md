# SimpleToolkit 工具包

SimpleToolkit 是一个集成了多种实用工具的 Python 工具包，涵盖文件系统操作、云服务交互、API 集成以及数据处理等功能，旨在帮助开发者更高效地完成各类任务。

## 特性

- **文件系统工具**：支持 CSV 和 Excel 文件的比较、合并、转换等操作。
- **API 集成工具**：集成腾讯云、华为云、飞书等多方的API，可简易方便的使用图搜、云上传、告警机器人等API。
- **数据处理工具**：包括文本处理和日期生成功能，可用于特殊字符转译、关键词提取以及各种日期范围的生成。



## 安装

### 1. 克隆仓库

```bash
git clone https://github.com/your-repo/simpletoolkit.git
cd simpletoolkit
```

### 2. 安装依赖

```
pip install -r requirements.txt
```

### 3. 构建和安装

```bash
# 安装打包工具
pip install setuptools wheel twine
# 生成源码包和二进制包
python setup.py sdist bdist_wheel
# 验证包内容
twine check dist/*
# 安装库
pip install dist/simpletoolkit-0.1.0-py3-none-any.whl
```

### 4. 配置环境变量（如果需要）

```bash
# 华为云AKSK
export HUAWEI_CLOUD_AK=<你的访问密钥 ID>
export HUAWEI_CLOUD_SK=<你的秘密访问密钥>
export HUAWEI_REGION=<华为云区域，如 cn-south-1>
# 腾讯云AKSK
export TENCENT_CLOUD_AK=<你的访问密钥 ID>
export TENCENT_CLOUD_SK=<你的秘密访问密钥>
export TENCENT_REGION=<腾讯云区域>
```



## 方法使用示例

### 一. 使用统一入口（SimpleToolkit）

```python
from simpletoolkit import create_toolkit

# 创建工具包实例
tk = create_toolkit()

# 配置全局参数
tk.configure_global(access_key='your_access_key', secret_key='your_secret_key', region='your_region')

# 使用文件系统工具
tk.filesystem.csv.compare_csv('file1.csv', 'file2.csv')
tk.filesystem.excel.split_excel_to_csv('file.xlsx')

# 使用API工具
tk.api.huawei.obs.upload_file('local_path', 'bucket_name', 'object_key')

# 使用数据处理工具
tk.data_processing.text.escape_text()
tk.data_processing.date_generator.get_today()
```

### 二. 使用具体类入口(部分示例)

#### 1. 华为云 OBS 工具（HuaweiOBSTool）

```python
from simpletoolkit.api.huawei.obs_tools import HuaweiOBSTool

# 初始化 OBS 工具
obs = HuaweiOBSTool(access_key='your_access_key', secret_key='your_secret_key', region='your_region')

# 上传文件到 OBS
local_path = 'path/to/local/file'
bucket_name = 'your_bucket_name'
object_key = 'your_object_key'
obs.upload_file(local_path, bucket_name, object_key)

# 从 OBS 下载文件
download_local_path = 'path/to/download/file'
obs.download_file(bucket_name, object_key, download_local_path)

# 列出 OBS 存储桶中的对象
object_list = obs.list_objects(bucket_name, prefix='your_prefix')
print(object_list)
```

#### 2. CSV 文件处理工具（CSVTool）

```python
from simpletoolkit.filesystems.csv_tools import CSVTool

# 初始化 CSV 工具
csv_tool = CSVTool()

# 比较两个 CSV 文件
file1 = 'path/to/csv/file1.csv'
file2 = 'path/to/csv/file2.csv'
diff_result = csv_tool.compare_csv(file1, file2, key_columns=['column1', 'column2'])
print(diff_result)

# 合并多个 CSV 文件
file_list = ['path/to/csv/file1.csv', 'path/to/csv/file2.csv']
output_file = 'path/to/output/merged.csv'
csv_tool.merge_csv_files(file_list, output_file, sort_by=['column1'])

# 将 CSV 文件转换为 Excel 文件
csv_file = 'path/to/csv/file.csv'
excel_file = 'path/to/output/file.xlsx'
csv_tool.csv_to_excel(csv_file, excel_file)
```

#### 3. 日期生成工具（DateGeneratorTool）

```python
from simpletoolkit.dataprocessing.date_generator import DateGeneratorTool

# 初始化日期生成器
date_generator = DateGeneratorTool(start_date='20250101', end_date='20250131')

# 生成从开始到结束的连续日期列表
date_range = date_generator.generate_date_range()
print(date_range)

# 生成按月划分的日期范围列表
monthly_ranges = date_generator.generate_monthly_ranges()
print(monthly_ranges)

# 生成按自定义间隔划分的日期范围列表
custom_ranges = date_generator.generate_custom_ranges(interval_days=7)
print(custom_ranges)
```



## 注意事项

- 在使用云服务工具和 API 集成工具时，需要提供相应的认证信息。

- 日期生成工具需要正确设置开始日期和结束日期，否则会抛出异常。



## 贡献

如果你有任何建议或发现了问题，请随时在 GitHub 上提交 issue 或 pull request。



## 许可证

本项目采用 [MIT 许可证](https://opensource.org/licenses/MIT)。