#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
筛选过滤httpx探活结果，根据状态码和标题关键词提取有价值的目标
"""

import os
import csv
import logging
import re
from pathlib import Path

# 获取logger
logger = logging.getLogger("subdatarefine.filter")

def filter_results(input_file, output_file, filter_config):
    """
    根据配置筛选数据
    
    参数:
        input_file: 输入CSV文件路径
        output_file: 输出CSV文件路径
        filter_config: 过滤配置字典
        
    返回:
        筛选后的记录数量
    """
    filtered_data = []
    total_count = 0
    
    # 解析过滤条件
    status_codes = [code.strip() for code in filter_config.get("status_codes", "").split(",") if code.strip()]
    title_keywords = [keyword.strip() for keyword in filter_config.get("title_keywords", "").split(",") if keyword.strip()]
    logic_and = filter_config.get("logic_and", True)
    include_redirect = filter_config.get("include_redirect", True)
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            # 使用csv模块读取数据
            reader = csv.reader(f)
            headers = next(reader)  # 读取表头
            
            # 找到各列的索引
            url_idx = headers.index("url") if "url" in headers else 0
            status_idx = headers.index("状态码") if "状态码" in headers else 1
            title_idx = headers.index("标题") if "标题" in headers else 2
            redirect_idx = headers.index("重定向URL") if "重定向URL" in headers else -1
            
            # 处理每一行数据
            for row in reader:
                total_count += 1
                
                if len(row) <= title_idx:
                    logger.warning(f"行数据不完整: {row}")
                    continue
                
                # 获取字段值
                url = row[url_idx]
                status = row[status_idx]
                title = row[title_idx]
                redirect = row[redirect_idx] if redirect_idx >= 0 and redirect_idx < len(row) else ""
                
                # 应用过滤条件
                status_match = not status_codes or any(code in status for code in status_codes)
                title_match = not title_keywords or any(keyword.lower() in title.lower() for keyword in title_keywords)
                
                # 基于逻辑条件决定是否保留
                if logic_and:
                    # 如果逻辑为"与"，需要同时满足状态码和标题条件
                    if status_match and title_match:
                        filtered_row = [url, status, title]
                        if include_redirect and redirect:
                            filtered_row.append(redirect)
                        filtered_data.append(filtered_row)
                else:
                    # 如果逻辑为"或"，满足任一条件即可
                    if status_match or title_match:
                        filtered_row = [url, status, title]
                        if include_redirect and redirect:
                            filtered_row.append(redirect)
                        filtered_data.append(filtered_row)
        
        # 确保输出目录存在
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        # 写入筛选后的数据
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            
            # 构建表头
            output_headers = ["url", "状态码", "标题"]
            if include_redirect and any(len(row) > 3 for row in filtered_data):
                output_headers.append("重定向URL")
            
            # 写入表头和数据
            writer.writerow(output_headers)
            writer.writerows(filtered_data)
        
        logger.info(f"筛选完成: 从 {total_count} 条记录中筛选出 {len(filtered_data)} 条")
        return len(filtered_data)
    
    except Exception as e:
        logger.error(f"筛选数据时出错: {e}")
        return 0

def main(input_file=None, output_file=None, filter_config=None):
    """
    主函数
    
    参数:
        input_file: 输入文件路径，默认从配置中读取
        output_file: 输出文件路径，默认从配置中读取
        filter_config: 过滤配置字典，默认为None
    """
    try:
        # 获取当前脚本所在目录
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # 如果没有提供配置，尝试从config.ini加载
        if filter_config is None:
            try:
                from configparser import ConfigParser
                config_path = os.path.join(script_dir, "config", "config.ini")
                config = ConfigParser()
                config.read(config_path, encoding='utf-8')
                
                filter_config = {}
                if config.has_section("filter"):
                    # 读取过滤配置
                    for key in ["status_codes", "title_keywords", "include_redirect"]:
                        if config.has_option("filter", key):
                            filter_config[key] = config.get("filter", key)
                    
                    # 读取布尔值
                    if config.has_option("filter", "logic_and"):
                        filter_config["logic_and"] = config.getboolean("filter", "logic_and")
                    
                    # 获取默认的输入输出文件路径
                    if input_file is None and config.has_option("filter", "input_file"):
                        input_file = config.get("filter", "input_file")
                    
                    if output_file is None and config.has_option("filter", "output_file"):
                        output_file = config.get("filter", "output_file")
            except Exception as e:
                logger.error(f"读取配置文件时出错: {e}")
                return
        
        # 如果仍然没有输入输出文件，使用默认值
        if input_file is None:
            input_file = "result/result_processed.csv"
        
        if output_file is None:
            output_file = "result/filtered_results.csv"
        
        if filter_config is None:
            filter_config = {
                "status_codes": "200",
                "title_keywords": "登录,注册,系统,后台,admin,login,system",
                "logic_and": True,
                "include_redirect": True
            }
        
        # 构建完整路径
        input_file_path = os.path.join(script_dir, input_file)
        output_file_path = os.path.join(script_dir, output_file)
        
        # 执行筛选
        count = filter_results(input_file_path, output_file_path, filter_config)
        
        logger.info(f"处理完成！共筛选出 {count} 条记录，已保存至 {output_file_path}")
        print(f"处理完成！共筛选出 {count} 条记录，已保存至 {output_file_path}")
    
    except Exception as e:
        logger.error(f"执行筛选时出错: {e}")

if __name__ == "__main__":
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 直接调用主函数
    main()
