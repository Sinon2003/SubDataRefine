#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
httpx工具函数

提供httpx命令构建和执行的函数。
"""

import os
import subprocess

def build_httpx_command(httpx_config, input_file, output_file, root_dir):
    """
    构建httpx命令
    
    参数:
        httpx_config: httpx配置字典
        input_file: 输入文件路径
        output_file: 输出文件路径
        root_dir: 项目根目录
        
    返回:
        构建的httpx命令
    """
    # 确保输入输出文件是绝对路径
    input_file_abs = os.path.join(root_dir, input_file) if not os.path.isabs(input_file) else input_file
    output_file_abs = os.path.join(root_dir, output_file) if not os.path.isabs(output_file) else output_file
    
    # 获取httpx可执行文件路径
    httpx_path = httpx_config.get("httpx_path", "httpx")
    
    # 基本命令
    cmd = [httpx_path, "-l", input_file_abs, "-o", output_file_abs]
    
    # 添加其他配置参数
    if httpx_config.get("threads"):
        cmd.extend(["-t", str(httpx_config.get("threads"))])
    
    if httpx_config.get("timeout"):
        cmd.extend(["-timeout", str(httpx_config.get("timeout"))])
    
    if httpx_config.get("follow_redirects", False):
        cmd.append("-fr")
    
    if httpx_config.get("status_code", False):
        cmd.append("-sc")
    
    if httpx_config.get("title", False):
        cmd.append("-title")
    
    # 处理additional_args
    additional_args = httpx_config.get("additional_args", "")
    if additional_args:
        for arg in additional_args.split(","):
            arg = arg.strip()
            if arg:
                cmd.append(arg)
    
    return cmd

def run_httpx(cmd, no_process=False):
    """
    执行httpx命令
    
    参数:
        cmd: httpx命令列表
        no_process: 当为True时，直接调用httpx程序而不捕获输出
        
    返回:
        (exitcode, stdout, stderr)
    """
    try:
        # 生成完整的命令行字符串
        cmd_str = ' '.join(cmd)
        
        if no_process:
            # -np 模式: 完全隐藏所有输出
            # 将命令的标准输出和错误输出重定向到空设备
            with open(os.devnull, 'w') as devnull:
                process = subprocess.Popen(cmd_str, shell=True, stdout=devnull, stderr=devnull)
                process.wait()  # 等待命令执行完成
                exitcode = process.returncode
            stdout = ""
            stderr = ""
        else:
            # 正常模式: 输出探活命令信息并捕获输出
            print(f"执行命令: {cmd_str}")
            
            # 使用 subprocess.call 执行命令
            exitcode = subprocess.call(cmd_str, shell=True)
            stdout = ""  # 由于使用call，我们没有捕获到标准输出
            stderr = ""  # 由于使用call，我们没有捕获到标准错误

        
        # 检查输出文件是否存在来判断是否成功
        # 从命令列表中查找-o参数后面的输出文件路径
        output_file = None
        try:
            # 在命令列表中找到-o参数的位置
            output_file_index = cmd.index('-o') + 1
            if output_file_index < len(cmd):
                output_file = cmd[output_file_index]
        except (ValueError, IndexError):
            print("在命令中未找到输出文件参数")
            
        if output_file:
            if os.path.exists(output_file) and os.path.getsize(output_file) > 0:

                print("httpx命令执行成功，输出文件已生成")
                exitcode = 0  # 即使返回码不是0，但文件存在则认为成功
            elif exitcode == 0:

                print("httpx命令返回成功，但未发现输出文件或文件为空")
            else:
                print(f"httpx命令执行失败: {stderr}")
        else:
            if exitcode == 0:

                print("httpx命令执行成功")
            else:
                print(f"httpx命令执行失败: {stderr}")
        
        return exitcode, stdout, stderr
    
    except Exception as e:

        print(f"执行httpx命令时发生错误: {e}")
        return -1, "", str(e)
