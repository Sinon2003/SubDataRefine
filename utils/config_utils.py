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



    """
    获取数据筛选相关配置
    
    参数:
        config: 配置对象
        
    返回:
        包含筛选配置的字典
    """
    # 默认配置
    default_config = {
        "input_file": "result/result_processed.csv",
        "output_file": "result/filtered_results.csv",
        "status_codes": "200",
        "title_keywords": "登录,注册,系统,后台,admin,login,system",
        "logic_and": True,
        "include_redirect": True
    }
    
    # 如果配置对象为空或不包含filter部分，直接返回默认配置
    if not config or not config.has_section("filter"):
        return default_config.copy()
    
    # 配置项类型映射
    config_types = {
        "input_file": "str",
        "output_file": "str",
        "status_codes": "str",
        "title_keywords": "str",
        "logic_and": "bool",
        "include_redirect": "bool"
    }
    
    # 创建结果字典，初始值为默认配置
    result = default_config.copy()
    
    # 从配置对象中读取值，覆盖默认值
    for key, type_info in config_types.items():
        if config.has_option("filter", key):
            if type_info == "str":
                result[key] = config.get("filter", key)
            elif type_info == "int":
                result[key] = config.getint("filter", key)
            elif type_info == "bool":
                result[key] = config.getboolean("filter", key)
    
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


    """
    获取数据筛选相关配置
    
    参数:
        config: 配置对象
        
    返回:
        包含筛选配置的字典
    """
    # 默认配置
    default_config = {
        "input_file": "result/result_processed.csv",
        "output_file": "result/filtered_results.csv",
        "status_codes": "200",
        "title_keywords": "登录,注册,系统,后台,admin,login,system",
        "logic_and": True,
        "include_redirect": True
    }
    
    # 如果配置对象为空或不包含filter部分，直接返回默认配置
    if not config or not config.has_section("filter"):
        return default_config.copy()
    
    # 配置项类型映射
    config_types = {
        "input_file": "str",
        "output_file": "str",
        "status_codes": "str",
        "title_keywords": "str",
        "logic_and": "bool",
        "include_redirect": "bool"
    }
    
    # 创建结果字典，初始值为默认配置
    result = default_config.copy()
    
    # 从配置对象中读取值，覆盖默认值
    for key, type_info in config_types.items():
        if config.has_option("filter", key):
            if type_info == "str":
                result[key] = config.get("filter", key)
            elif type_info == "int":
                result[key] = config.getint("filter", key)
            elif type_info == "bool":
                result[key] = config.getboolean("filter", key)
    
    return result

def get_httpx_config(config):
    """
    获取httpx相关配置
    
    参数:
        config: 配置对象
        
    返回:
        包含httpx配置的字典
    """
    # 默认配置
    default_config = {
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
    
    # 如果配置对象为空或不包含httpx部分，直接返回默认配置
    if not config or not config.has_section("httpx"):
        return default_config.copy()
    
    # 配置项类型映射
    config_types = {
        "httpx_path": "str",
        "threads": "int",
        "timeout": "int",
        "follow_redirects": "bool",
        "status_code": "bool",
        "title": "bool",
        "output_file": "str",
        "input_file": "str",
        "additional_args": "str",
        "capture_output": "bool",
        "output_log_file": "str"
    }
    
    # 创建结果字典，初始值为默认配置
    result = default_config.copy()
    
    # 从配置对象中读取值，覆盖默认值
    for key, type_info in config_types.items():
        if config.has_option("httpx", key):
            if type_info == "str":
                result[key] = config.get("httpx", key)
            elif type_info == "int":
                result[key] = config.getint("httpx", key)
            elif type_info == "bool":
                result[key] = config.getboolean("httpx", key)
    
    return result

def get_filter_config(config):
    """
    获取数据筛选相关配置
    
    参数:
        config: 配置对象
        
    返回:
        包含筛选配置的字典
    """
    # 默认配置
    default_config = {
        "input_file": "result/result_processed.csv",
        "output_file": "result/filtered_results.csv",
        "status_codes": "200",
        "title_keywords": "登录,注册,系统,后台,admin,login,system",
        "logic_and": True,
        "include_redirect": True
    }
    
    # 如果配置对象为空或不包含filter部分，直接返回默认配置
    if not config or not config.has_section("filter"):
        return default_config.copy()
    
    # 配置项类型映射
    config_types = {
        "input_file": "str",
        "output_file": "str",
        "status_codes": "str",
        "title_keywords": "str",
        "logic_and": "bool",
        "include_redirect": "bool"
    }
    
    # 创建结果字典，初始值为默认配置
    result = default_config.copy()
    
    # 从配置对象中读取值，覆盖默认值
    for key, type_info in config_types.items():
        if config.has_option("filter", key):
            if type_info == "str":
                result[key] = config.get("filter", key)
            elif type_info == "int":
                result[key] = config.getint("filter", key)
            elif type_info == "bool":
                result[key] = config.getboolean("filter", key)
    return result