# SubDataRefine

## 项目简介

SubDataRefine是一个用于子域名资产数据处理的工具，为信息收集阶段数据处理设计。该工具可以处理多种格式的子域名数据文件，提取子域名，并支持httpx探活及结果处理。

项目采用Python 3.12编写，具有良好的扩展性和模块化结构。

## 功能特点

- **自动化处理**：首次运行时自动初始化项目结构
- **多格式支持**：可处理TXT、CSV等多种格式的子域名数据文件
- **数据去重**：提取的子域名具有唯一性
- **端口处理**：可选择性去除443端口信息（HTTPS默认端口）
- **探活集成**：支持集成httpx工具进行子域名探活
- **结果处理**：将探活结果处理为结构化CSV格式
- **灵活配置**：支持通过配置文件和命令行参数进行配置

## 项目结构

```
SubDataRefine/
├── SubDataRefine.py       # 主程序入口
├── config/                # 配置文件夹
│   └── config.ini        # 配置文件
├── domain/               # 各工具/网站收集的子域名数据文件夹
├── result/               # 处理后的数据文件夹
├── script/               # 脚本文件夹
│   ├── extract_domains.py # 子域名批处理脚本
│   └── process_results.py # 探活结果处理脚本
├── temp/                 # 临时文件夹
├── utils/                # 工具文件夹
│   ├── file_utils.py     # 文件工具
│   └── logging_utils.py  # 日志工具
└── logs/                 # 日志文件夹
```

## 使用方法

### 基本用法

1. 将收集的子域名数据文件放入`domain`目录
2. 运行主程序：
   ```
   python SubDataRefine.py
   ```

### 可选参数

- `-s, --skip-httpx`：跳过httpx探活步骤，只处理子域名数据
  ```
  python SubDataRefine.py -s
  ```
  
- `-o, --output`：指定子域名处理后的输出文件名
  ```
  python SubDataRefine.py -o custom_output.txt
  ```

- `-c, --config`：指定配置文件路径
  ```
  python SubDataRefine.py -c my_config.ini
  ```
  
- `-np, --no-process`：直接调用httpx程序而不捕获输出
  ```
  python SubDataRefine.py -np
  ```
  
- `-v, --version`：显示版本信息

### 子命令支持

- 初始化项目结构（通常不需要手动执行，程序会自动初始化）
  ```
  python SubDataRefine.py init
  ```

- 通过子命令明确运行完整流程
  ```
  python SubDataRefine.py run -s -o custom_output.txt
  ```

## 依赖项

- Python 3.12+
- 本地安装的httpx工具（可选，用于探活）

## httpx参数解析

httpx是一个快速且多功能的HTTP探测工具，本项目中使用了以下参数：

### 核心参数

- `-l, --list`：指定输入文件，包含要探测的主机列表（配置中的`input_file = domains.txt`）
- `-sc, --status-code`：显示响应状态码（配置中的`status_code = true`）
- `-title`：显示页面标题（配置中的`title = true`）
- `-o, --output`：指定输出文件（配置中的`output_file = result.txt`）

### 性能参数

- `-t, --threads`：指定线程数，控制并发请求数量（配置中的`threads = 20`）
- `-rl, --rate-limit`：每秒发送的最大请求数（配置中的`additional_args = -rl 60,-rlm 3000`）
- `-rlm, --rate-limit-minute`：每分钟发送的最大请求数（配置中的`additional_args = -rl 60,-rlm 3000`）
- `timeout`：请求超时时间，单位为秒（配置中的`timeout = 5`）

### 输出参数

- `-fr, --follow-redirects`：跟随重定向，可以发现真实目标网站（配置中的`follow_redirects = true`）

### 日志和输出捕获

- `capture_output`：是否捕获httpx的输出到日志文件（配置中的`capture_output = true`）
- `output_log_file`：指定httpx日志输出文件名（配置中的`output_log_file = httpx_output.log`）

### 其他配置

- `-pa, --probe-all-ips`：探测与同一主机关联的所有IP
- `-p, --ports`：指定要探测的端口
- `-path`：指定要探测的路径

### 使用示例

默认配置下的httpx命令相当于：

```
httpx -l domains.txt -sc -title -t 20 -rl 60 -rlm 3000 -fr -o result.txt
```

可以在配置文件中修改这些参数，或者通过SubDataRefine的命令行参数覆盖。

### 注意事项

- 过高的并发线程数和请求速率可能导致目标服务器拒绝服务或IP被封禁
- 使用httpx探活时请确保您已获得授权，避免未经许可的安全测试
- 探活结果保存在`result.txt`文件中，稍后会被处理脚本转换为结构化的CSV数据
