#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
提取所有文件中的裸主机名（保留端口号）并确保唯一性
"""

import os
import re
import csv
from urllib.parse import urlparse

# 设置目录路径
DIR_PATH = r"domain"
OUTPUT_FILE = r"domains.txt"

def extract_domain_from_url(url):
    """从URL中提取裸主机名（保留端口号，但去除443端口）"""
    if not url:
        return None
    
    # 确保URL有协议前缀
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url
    
    try:
        parsed = urlparse(url)
        # 如果端口是443（HTTPS默认端口），则不包含端口
        if parsed.port == 443:
            # 返回不带端口的主机名
            return parsed.hostname
        # 返回主机名+端口（如果有其他端口）
        elif parsed.port:
            return f"{parsed.netloc}"
        else:
            return parsed.netloc
    except Exception as e:
        print(f"解析URL错误: {url}, 错误信息: {e}")
        return None

def process_txt_file(file_path):
    """处理纯文本文件，提取域名"""
    domains = set()
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.strip()
            if not line or line == "子域名":  # 跳过空行和表头
                continue
            
            # 提取域名（处理可能存在的URL）
            domain = extract_domain_from_url(line)
            if domain:
                domains.add(domain)
            else:
                # 可能是裸域名，直接添加
                domains.add(line)
    
    return domains

def process_csv_file(file_path):
    """处理CSV文件，从不同列中提取域名"""
    domains = set()
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            # 尝试读取CSV
            reader = csv.reader(f)
            header = next(reader, None)
            
            if not header:
                return domains
            
            # 确定包含域名的列索引
            domain_indices = []
            url_indices = []
            host_indices = []
            
            for i, col in enumerate(header):
                if col.lower() in ['域名', 'domain']:
                    domain_indices.append(i)
                elif col.lower() in ['url', 'link']:
                    url_indices.append(i)
                elif col.lower() in ['host']:
                    host_indices.append(i)
            
            # 从每行数据中提取域名
            for row in reader:
                # 从域名列提取
                for idx in domain_indices:
                    if idx < len(row) and row[idx]:
                        domains.add(row[idx])
                
                # 从URL列提取
                for idx in url_indices:
                    if idx < len(row) and row[idx]:
                        domain = extract_domain_from_url(row[idx])
                        if domain:
                            domains.add(domain)
                
                # 从Host列提取
                for idx in host_indices:
                    if idx < len(row) and row[idx]:
                        domain = extract_domain_from_url(row[idx])
                        if domain:
                            domains.add(domain)
                        
                # 特殊处理：如果有IP和端口列，但没有域名
                if len(domain_indices) == 0 and len(url_indices) == 0 and len(host_indices) == 0:
                    # 寻找IP和端口列
                    ip_idx = -1
                    port_idx = -1
                    for i, col in enumerate(header):
                        if col.lower() == 'ip':
                            ip_idx = i
                        elif col.lower() == '端口' or col.lower() == 'port':
                            port_idx = i
                    
                    # 如果找到IP和端口列，组合成域名格式
                    if ip_idx >= 0 and port_idx >= 0 and ip_idx < len(row) and port_idx < len(row):
                        if row[ip_idx] and row[port_idx]:
                            domain = f"{row[ip_idx]}:{row[port_idx]}"
                            domains.add(domain)
    
    except Exception as e:
        print(f"处理CSV文件错误: {file_path}, 错误信息: {e}")
    
    return domains

def main():
    """主函数"""
    all_domains = set()
    
    # 处理目录下所有文件
    for filename in os.listdir(DIR_PATH):
        file_path = os.path.join(DIR_PATH, filename)
        
        # 只处理文本和CSV文件
        if not os.path.isfile(file_path):
            continue
        
        print(f"处理文件: {filename}")
        
        # 根据文件扩展名选择处理方法
        if filename.endswith('.csv'):
            domains = process_csv_file(file_path)
        else:  # 默认作为文本文件处理
            domains = process_txt_file(file_path)
        
        # 添加到总集合
        all_domains.update(domains)
    
    # 保存唯一域名到输出文件
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        for domain in sorted(all_domains):
            f.write(domain + '\n')
    
    print(f"提取完成！共找到 {len(all_domains)} 个唯一域名，已保存至 {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
