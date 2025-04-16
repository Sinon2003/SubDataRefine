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
    
    # 正则表达式模式匹配 URL [状态码] [标题] 格式
    # 修改正则表达式以处理ANSI颜色代码
    pattern = r'^(https?://[^\s]+)\s+\[(?:\x1b\[[\d;]+m)?(\d+)(?:\x1b\[0m)?\]\s+\[(?:\x1b\[[\d;]+m)?(.+?)(?:\x1b\[0m)?\]'
    
    try:
        # 打开并读取输入文件
        with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                # 使用正则表达式提取数据
                match = re.match(pattern, line)
                if match:
                    url = match.group(1)
                    status_code = match.group(2)
                    title = match.group(3)
                    data.append([url, status_code, title])
                else:
                    # 尝试删除所有ANSI转义序列后再匹配
                    # ANSI转义序列通常是\x1b[...m格式
                    ansi_escape = re.compile(r'\x1b\[(?:\d+;)*\d+m')
                    clean_line = ansi_escape.sub('', line)
                    
                    # 清除后尝试使用简化的正则表达式匹配
                    simple_pattern = r'^(https?://[^\s]+)\s+\[(\d+)\]\s+\[(.+?)\]'
                    simple_match = re.match(simple_pattern, clean_line)
                    
                    if simple_match:
                        url = simple_match.group(1)
                        status_code = simple_match.group(2)
                        title = simple_match.group(3)
                        data.append([url, status_code, title])
                    else:
                        # 仍然失败，尝试更简单的方法
                        # 直接提取URL和方括号内的内容
                        url_pattern = r'^(https?://[^\s]+)'
                        url_match = re.match(url_pattern, clean_line)
                        
                        # 处理多状态码的情况，如[[33m302[0m,[32m200[0m]
                        # 首先尝试提取所有状态码
                        status_codes = []
                        status_pattern = r'\[(\d+)\]|,(\d+)'
                        for status_match in re.finditer(status_pattern, clean_line):
                            code = status_match.group(1) or status_match.group(2)
                            if code:
                                status_codes.append(code)
                        
                        # 使用最后一个状态码（通常是最终状态）
                        status_code = status_codes[-1] if status_codes else None
                        
                        # 提取标题
                        title_pattern = r'\]\s+\[(.+?)\]|\[\s*(.+?)\s*\]$'
                        title_match = re.search(title_pattern, clean_line)
                        
                        if url_match and status_code and title_match:
                            url = url_match.group(1)
                            # 使用正则表达式中获取的第一个或第二个捕获组（哪个不为None）
                            title = title_match.group(1) if title_match.group(1) else title_match.group(2)
                            # 结合所有状态码，使用逗号分隔
                            all_status_codes = ','.join(status_codes)
                            data.append([url, all_status_codes, title])
                        else:
                            logger.warning(f"无法解析行: {line}")
        
        # 确保输出目录存在
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 写入到CSV文件
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            # 写入表头
            writer.writerow(["url", "状态码", "标题"])
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
