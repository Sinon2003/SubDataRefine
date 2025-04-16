#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志工具模块
"""

import logging
import os
from datetime import datetime

def setup_logger(name, log_file=None, level=logging.INFO):
    """
    配置日志记录器
    
    参数:
        name: 日志记录器名称
        log_file: 日志文件路径，如不指定则只输出到控制台
        level: 日志级别，默认为INFO
    """
    # 创建日志记录器
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    
    # 创建格式器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    # 添加处理器到日志记录器
    logger.addHandler(console_handler)
    
    # 如果指定了日志文件，创建文件处理器
    if log_file:
        # 确保日志目录存在
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger
