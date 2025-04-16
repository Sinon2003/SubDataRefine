#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置工具模块

提供读取和解析配置文件的函数。
"""

import os
import configparser

def load_config(config_path, root_dir=None):
    """
    读取配置文件
    
    参数:
        config_path: 配置文件路径
        root_dir: 项目根目录，如果提供则路径相对于根目录计算
        
    返回:
        配置对象
    """
    config = configparser.ConfigParser()
    
    # 如果提供了根目录，将路径转换为相对于根目录的绝对路径
    if root_dir:
        config_path = os.path.join(root_dir, config_path)
    
    if not os.path.exists(config_path):
        print(f"警告: 找不到配置文件 {config_path}，将使用默认值")
        return None
    
    try:
        config.read(config_path, encoding='utf-8')
        return config
    except Exception as e:
        print(f"错误: 读取配置文件失败 {e}")
        return None

def get_domain_extract_config(config):
    """
    获取域名提取相关配置
    
    参数:
        config: 配置对象
        
    返回:
        包含域名提取配置的字典
    """
    if not config:
        return {
            "strip_443": True,
            "output_file": "domains.txt"
        }
    
    result = {}
    
    # 域名提取配置
    if config.has_section("domain_extract"):
        if config.has_option("domain_extract", "strip_443"):
            result["strip_443"] = config.getboolean("domain_extract", "strip_443")
        else:
            result["strip_443"] = True
            
        if config.has_option("domain_extract", "output_file"):
            result["output_file"] = config.get("domain_extract", "output_file")
        else:
            result["output_file"] = "domains.txt"
    else:
        result["strip_443"] = True
        result["output_file"] = "domains.txt"
        
    return result

def get_paths_config(config):
    """
    获取路径相关配置
    
    参数:
        config: 配置对象
        
    返回:
        包含路径配置的字典
    """
    if not config:
        return {
            "domain_dir": "domain",
            "result_dir": "result",
            "temp_dir": "temp"
        }
    
    result = {}
    
    # 路径配置
    if config.has_section("paths"):
        if config.has_option("paths", "domain_dir"):
            result["domain_dir"] = config.get("paths", "domain_dir")
        else:
            result["domain_dir"] = "domain"
            
        if config.has_option("paths", "result_dir"):
            result["result_dir"] = config.get("paths", "result_dir")
        else:
            result["result_dir"] = "result"
            
        if config.has_option("paths", "temp_dir"):
            result["temp_dir"] = config.get("paths", "temp_dir")
        else:
            result["temp_dir"] = "temp"
    else:
        result["domain_dir"] = "domain"
        result["result_dir"] = "result"
        result["temp_dir"] = "temp"
        
    return result

def get_httpx_config(config):
    """
    获取httpx相关配置
    
    参数:
        config: 配置对象
        
    返回:
        包含httpx配置的字典
    """
    if not config:
        return {
            "httpx_path": "httpx",
            "threads": 20,
            "timeout": 5,
            "follow_redirects": True,
            "status_code": True,
            "title": True,
            "output_file": "result.txt",
            "input_file": "domains.txt",
            "additional_args": "-rl 60,-rlm 3000",
            "capture_output": True,
            "output_log_file": "httpx_output.log"
        }
    
    result = {}
    
    # httpx配置
    if config.has_section("httpx"):
        if config.has_option("httpx", "httpx_path"):
            result["httpx_path"] = config.get("httpx", "httpx_path")
        else:
            result["httpx_path"] = "httpx"
            
        if config.has_option("httpx", "threads"):
            result["threads"] = config.getint("httpx", "threads")
        else:
            result["threads"] = 20
            
        if config.has_option("httpx", "timeout"):
            result["timeout"] = config.getint("httpx", "timeout")
        else:
            result["timeout"] = 5
            
        if config.has_option("httpx", "follow_redirects"):
            result["follow_redirects"] = config.getboolean("httpx", "follow_redirects")
        else:
            result["follow_redirects"] = True
            
        if config.has_option("httpx", "status_code"):
            result["status_code"] = config.getboolean("httpx", "status_code")
        else:
            result["status_code"] = True
            
        if config.has_option("httpx", "title"):
            result["title"] = config.getboolean("httpx", "title")
        else:
            result["title"] = True
            
        if config.has_option("httpx", "output_file"):
            result["output_file"] = config.get("httpx", "output_file")
        else:
            result["output_file"] = "result.txt"
            
        if config.has_option("httpx", "input_file"):
            result["input_file"] = config.get("httpx", "input_file")
        else:
            result["input_file"] = "domains.txt"
            
        if config.has_option("httpx", "additional_args"):
            result["additional_args"] = config.get("httpx", "additional_args")
        else:
            result["additional_args"] = "-rl 60,-rlm 3000"
            
        if config.has_option("httpx", "capture_output"):
            result["capture_output"] = config.getboolean("httpx", "capture_output")
        else:
            result["capture_output"] = True
            
        if config.has_option("httpx", "output_log_file"):
            result["output_log_file"] = config.get("httpx", "output_log_file")
        else:
            result["output_log_file"] = "httpx_output.log"
    else:
        # 默认配置
        result["httpx_path"] = "httpx"
        result["threads"] = 20
        result["timeout"] = 5
        result["follow_redirects"] = True
        result["status_code"] = True
        result["title"] = True
        result["output_file"] = "result.txt"
        result["input_file"] = "domains.txt"
        result["additional_args"] = "-rl 60,-rlm 3000"
        result["capture_output"] = True
        result["output_log_file"] = "httpx_output.log"
        
    return result
