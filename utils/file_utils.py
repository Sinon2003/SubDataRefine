#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件处理工具模块
"""

import os

def ensure_dir_exists(dir_path):
    """
    确保目录存在，如不存在则创建
    """
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        print(f"已创建目录: {dir_path}")
    return dir_path
