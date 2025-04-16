#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SubDataRefine - 子域名数据处理工具

用于对收集的子域名资产进行整理和分析。
项目采用 python 3.12 编写。

主要功能：
1. 从多种格式文件中提取子域名
2. 子域名统一格式处理
3. 子域名存活性检测
4. 结果处理与导出

作者：Rorochan
"""

import os
import sys
import argparse
import importlib.util
from pathlib import Path

# 设置项目根目录
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
# 添加项目根目录到Python路径
sys.path.append(ROOT_DIR)

# 导入工具模块
from utils.logging_utils import setup_logger
from utils.file_utils import ensure_dir_exists
from utils.config_utils import load_config, get_domain_extract_config, get_paths_config, get_httpx_config
from utils.httpx_utils import build_httpx_command, run_httpx

def load_script(script_name):
    """
    动态加载script目录下的脚本
    """
    script_path = os.path.join(ROOT_DIR, "script", f"{script_name}.py")
    
    if not os.path.exists(script_path):
        print(f"错误: 找不到脚本文件 {script_path}")
        return None
    
    spec = importlib.util.spec_from_file_location(script_name, script_path)
    if spec is None:
        print(f"错误: 无法加载脚本 {script_path}")
        return None
    
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def init_project_structure():
    """
    初始化项目目录结构
    """
    dirs = ["config", "domain", "result", "script", "temp", "utils", "logs"]
    for dir_name in dirs:
        dir_path = os.path.join(ROOT_DIR, dir_name)
        ensure_dir_exists(dir_path)
    
    print("项目目录结构已初始化")

def parse_args():
    """
    解析命令行参数
    """
    parser = argparse.ArgumentParser(description="子域名数据整理工具")
    
    # 添加主命令参数
    parser.add_argument("-c", "--config", default="config/config.ini", 
                        help="指定配置文件路径，默认为config/config.ini")
    parser.add_argument("-o", "--output", 
                        help="指定子域名处理后的输出文件名，默认使用配置文件中的值")
    parser.add_argument("-s", "--skip-httpx", action="store_true", 
                        help="跳过httpx探活步骤，只处理子域名数据")
    parser.add_argument("-i", "--init", action="store_true", 
                        help="初始化必要的目录结构")
    parser.add_argument("-nc", "--no-capture", action="store_true", 
                        help="不捕获httpx输出到日志文件")
    parser.add_argument("-v", "--version", action="version", 
                        version="SubDataRefine v1.0.0")
    
    return parser.parse_args()

def run_workflow(config_path, skip_httpx=False, output_file=None, capture_output=None):
    """
    运行完整工作流程
    
    参数:
        config_path: 配置文件路径
        skip_httpx: 是否跳过httpx探活步骤
        output_file: 子域名处理后的输出文件名，如果为None则使用配置文件中的值
    """
    print("=== 开始处理子域名数据 ===")
    
    # 读取配置文件
    config = load_config(config_path, ROOT_DIR)
    
    # 获取域名提取配置
    domain_extract_config = get_domain_extract_config(config)
    
    # 获取路径配置
    paths_config = get_paths_config(config)
    
    # 如果命令行参数未指定输出文件，使用配置文件中的值
    default_output_file = domain_extract_config.get("output_file")
    default_domain_dir = paths_config.get("domain_dir")
    default_strip_443 = domain_extract_config.get("strip_443")
    
    if output_file is None:
        output_file = default_output_file
    
    # 步骤1: 提取子域名
    extract_script = load_script("extract_domains")
    if extract_script:
        print("\n[1/3] 正在提取子域名...")
        
        # 确保结果目录存在
        if os.path.dirname(output_file) and not os.path.exists(os.path.dirname(os.path.join(ROOT_DIR, output_file))):
            print(f"创建输出目录: {os.path.dirname(os.path.join(ROOT_DIR, output_file))}")
            os.makedirs(os.path.dirname(os.path.join(ROOT_DIR, output_file)), exist_ok=True)
        
        domains_file = os.path.join(ROOT_DIR, output_file)
        extract_script.main(
            dir_path=default_domain_dir,
            output_file=domains_file,
            strip_443=default_strip_443
        )
    else:
        print("错误: 无法加载提取子域名脚本")
        return
    
    # 步骤2: 使用httpx进行子域名探活
    if skip_httpx:
        print("\n[2/3] 跳过子域名探活步骤...")
        print("提示: 由于指定了--skip-httpx参数，仅处理子域名数据，不进行探活")
    else:
        print("\n[2/3] 正在进行子域名探活...")
        
        # 获取httpx配置
        httpx_config = get_httpx_config(config)
        
        # 验证httpx路径是否有效
        httpx_path = httpx_config.get("httpx_path")
        if not os.path.exists(httpx_path):
            print(f"\n错误: httpx可执行文件不存在: {httpx_path}")
            print("请在config.ini中设置正确的httpx_path")
            skip_httpx = True
        else:
            # 使用域名提取过程中生成的文件作为httpx输入
            input_file = domains_file
            # 将httpx的原始输出结果保存到temp目录
            temp_dir = os.path.join(ROOT_DIR, paths_config.get("temp_dir"))
            # 确保temp目录存在
            ensure_dir_exists(temp_dir)
            # 生成httpx的输出文件路径
            output_file = os.path.join(temp_dir, httpx_config.get("output_file"))
            
            # 检查输入文件是否存在
            if not os.path.exists(input_file) or os.path.getsize(input_file) == 0:
                print(f"\n错误: 输入文件不存在或为空: {input_file}")
                skip_httpx = True
            else:
                # 确保输出目录存在
                output_dir = os.path.dirname(output_file)
                if output_dir and not os.path.exists(output_dir):
                    os.makedirs(output_dir, exist_ok=True)
                
                # 构建httpx命令
                cmd = build_httpx_command(httpx_config, input_file, output_file, ROOT_DIR)
                
                print(f"\n正在构建探活命令...")
                print("正在进行探活，这可能需要一些时间...")
                
                # 准备日志文件路径
                output_log_file = None
                if capture_output is not None:
                    # 使用命令行传入的设置覆盖配置文件的设置
                    use_capture = capture_output
                else:
                    # 使用配置文件的设置
                    use_capture = httpx_config.get("capture_output", True)
                
                if use_capture:
                    # 生成日志文件路径
                    log_file_name = httpx_config.get("output_log_file", "httpx_output.log")
                    output_log_file = os.path.join(temp_dir, log_file_name)
                    print(f"将捕获httpx输出到文件: {output_log_file}")
                else:
                    print("不捕获httpx的输出到日志文件")
                
                # 执行httpx命令
                exitcode, stdout, stderr = run_httpx(cmd, use_capture, output_log_file)
                
                # 检查输出文件并确定是否成功
                if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                    print(f"httpx探活完成，原始结果保存在 {output_file}")
                elif exitcode == 0:
                    print(f"httpx命令返回成功，但未生成输出文件或文件为空")
                    print("可能没有可探活的域名或所有探活都失败")
                    skip_httpx = True
                else:
                    print(f"httpx探活失败: {stderr if stderr else '\u672a知错误'}")
                    print("将跳过探活结果处理步骤")
                    skip_httpx = True  # 如果httpx执行失败，跳过结果处理
    
    # 步骤3: 处理探活结果
    if skip_httpx:
        print("\n[3/3] 跳过探活结果处理步骤...")
        print("提示: 由于跳过了探活步骤，不需要处理探活结果")
    else:
        process_script = load_script("process_results")
        if process_script:
            print("\n[3/3] 正在处理探活结果...")
            # 使用temp目录中的原始结果文件
            result_file = os.path.join(temp_dir, httpx_config.get("output_file"))
            output_file = os.path.join(ROOT_DIR, "result", "result_processed.csv")
            
            # 检查result.txt是否存在
            if os.path.exists(result_file):
                process_script.main(
                    input_file=result_file,
                    output_file=output_file
                )
            else:
                print(f"警告: 找不到结果文件 {result_file}，跳过处理步骤")
        else:
            print("警告: 无法加载结果处理脚本，跳过处理步骤")
    
    print("\n=== 子域名数据处理完成 ===")

def check_and_init_directories():
    """
    检查并初始化必要的项目目录
    """
    # 初始化目录列表
    core_dirs = ["config", "domain", "result", "temp", "utils", "script", "logs"]
    
    # 检查所有目录是否存在
    missing_dirs = []
    for dir_name in core_dirs:
        dir_path = os.path.join(ROOT_DIR, dir_name)
        if not os.path.exists(dir_path):
            missing_dirs.append(dir_name)
    
    # 如果有缺失的目录，初始化项目结构
    if missing_dirs:
        print(f"检测到项目结构不完整，缺失目录: {', '.join(missing_dirs)}")
        print("正在自动初始化项目结构...")
        for dir_name in core_dirs:
            ensure_dir_exists(os.path.join(ROOT_DIR, dir_name))
        print("项目结构初始化完成\n")

def main():
    """
    主函数，程序入口
    """
    # 解析命令行参数
    args = parse_args()
    
    # 如果指定了--init参数，则初始化必要的目录结构
    if args.init:
        check_and_init_directories()
        print("\n项目结构初始化完成")
    else:
        # 自动检查并初始化项目结构
        check_and_init_directories()
        
        # 如果指定了--no-capture参数，则设置capture_output为False
        capture_output = False if args.no_capture else None
        
        # 运行工作流程
        run_workflow(args.config, args.skip_httpx, args.output, capture_output)
    


if __name__ == "__main__":
    main()
