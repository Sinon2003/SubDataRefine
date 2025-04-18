#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
处理httpx探活结果，转换为CSV格式
"""

import os
import re
import csv
import logging

# 获取logger
logger = logging.getLogger("subdatarefine.process")

def process_result_file(input_file, output_file):
    """
    处理httpx探活结果文件，转换为CSV格式
    
    参数:
        input_file: 输入文件路径，包含探活结果
        output_file: 输出CSV文件路径
    
    返回:
        处理的记录数量
    """
    # 存储提取的数据
    data = []
    
    try:
        # 打开并读取输入文件
        with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                # 删除所有ANSI转义序列
                ansi_escape = re.compile(r'\x1b\[(?:\d+;)*\d+m')
                clean_line = ansi_escape.sub('', line)
                
                # 提取URL（第一个空格之前的部分）
                url_match = re.match(r'^(https?://[^\s]+)', clean_line)
                if not url_match:
                    logger.warning(f"无法提取URL: {line}")
                    continue
                    
                url = url_match.group(1)
                
                # 查找所有方括号内容
                brackets = re.findall(r'\[(.*?)\]', clean_line)
                
                # 初始化变量
                status_code = ""
                title = ""
                redirect_url = ""
                
                # 处理各种可能的情况
                if not brackets:
                    # 完全没有方括号，但仍然有URL，我们可以保留该记录
                    logger.warning(f"没有方括号内容: {url}")
                    status_code = "Unknown"
                    # 标题保持为空
                elif len(brackets) == 1:
                    # 只有一个方括号，通常是状态码
                    status_code_raw = brackets[0]
                    status_codes = re.findall(r'\d+', status_code_raw)
                    if status_codes:
                        status_code = ','.join(status_codes)
                        # 标题保持为空字符串
                    else:
                        # 如果方括号中没有数字，内容不明确，设置状态码为Unknown，标题保持为空
                        status_code = "Unknown"
                    logger.warning(f"方括号内容不足: {url} [{status_code}]")
                else:
                    # 正常情况或有更多方括号
                    # 提取状态码（第一个方括号）
                    status_code_raw = brackets[0]
                    
                    # 处理状态码，可能有多个状态码如 "302,200"
                    # 识别状态码中的数字
                    status_codes = re.findall(r'\d+', status_code_raw)
                    if status_codes:
                        # 使用所有状态码，用逗号连接
                        status_code = ','.join(status_codes)
                    else:
                        # 状态码为空，但继续处理
                        logger.warning(f"无法提取状态码: {url} [{status_code_raw}]")
                        status_code = "Unknown"
                    
                    # 提取标题（第二个方括号）
                    title = brackets[1] if len(brackets) > 1 else ""
                    
                    # 提取重定向URL（如果存在的话，第三个方括号）
                    redirect_url = brackets[2] if len(brackets) > 2 else ""
                
                # 构建数据记录
                record = [url, status_code, title]
                
                # 如果有重定向URL，添加到记录中
                if redirect_url:
                    record.append(redirect_url)
                
                data.append(record)
        
        # 确保输出目录存在
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 写入到CSV文件
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            
            # 构建表头
            headers = ["url", "状态码", "标题"]
            if any(len(record) > 3 for record in data):
                headers.append("重定向URL")
                
            # 写入表头
            writer.writerow(headers)
            
            # 写入数据
            writer.writerows(data)
        
        return len(data)
        
    except Exception as e:
        logger.error(f"处理结果文件出错: {e}")
        return 0

def main(input_file="result.txt", output_file="result_processed.csv"):
    """
    主函数
    
    参数:
        input_file: 输入文件路径，默认为result.txt
        output_file: 输出文件路径，默认为result_processed.csv
    """
    # 获取当前脚本所在目录
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # 构建完整路径
    input_file_path = os.path.join(script_dir, input_file)
    output_file_path = os.path.join(script_dir, output_file)
    
    # 处理结果文件
    count = process_result_file(input_file_path, output_file_path)
    
    logger.info(f"处理完成！共转换 {count} 条记录，已保存至 {output_file_path}")
    print(f"处理完成！共转换 {count} 条记录，已保存至 {output_file_path}")

if __name__ == "__main__":
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 直接调用主函数
    main()
