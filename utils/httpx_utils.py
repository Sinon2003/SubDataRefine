#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
httpx工具函数

提供httpx命令构建和执行的函数。
"""

import os
import subprocess
import logging

# 获取logger
logger = logging.getLogger("subdatarefine.httpx")

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

def run_httpx(cmd, capture_output=True, output_log_file=None):
    """
    执行httpx命令
    
    参数:
        cmd: httpx命令列表
        capture_output: 是否捕获httpx的输出
        output_log_file: 用于保存httpx输出的日志文件路径
        
    返回:
        (exitcode, stdout, stderr)
    """
    try:
        # 生成完整的命令行字符串
        cmd_str = ' '.join(cmd)
        logger.info(f"执行命令: {cmd_str}")
        print(f"执行命令: {cmd_str}")

        # Windows下的命令执行(使用shell=True)
        process = subprocess.Popen(
            cmd_str,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,    # 将shell设置为True可以确保完整的命令行被执行
            text=True,
            encoding="utf-8",
            errors="ignore"
        )
        
        print(f"正在运行httpx，正在等待程序完成...")
        
        # 获取输出，这会阻塞直到程序完成
        stdout, stderr = process.communicate()
        exitcode = process.returncode
        
        # 如果要求捕获输出并提供了日志文件路径
        if capture_output and output_log_file:
            try:
                # 确保日志文件的目录存在
                output_dir = os.path.dirname(output_log_file)
                if output_dir and not os.path.exists(output_dir):
                    os.makedirs(output_dir, exist_ok=True)
                    
                # 将httpx的输出写入日志文件
                with open(output_log_file, 'w', encoding='utf-8') as f:
                    if stdout:
                        f.write("===== HTTPX STDOUT =====\n")
                        f.write(stdout)
                        f.write("\n\n")
                    if stderr:
                        f.write("===== HTTPX STDERR =====\n")
                        f.write(stderr)
                
                logger.info(f"httpx输出已捕获到文件: {output_log_file}")
                print(f"httpx输出已捕获到文件: {output_log_file}")
            except Exception as e:
                logger.error(f"写入httpx输出日志时出错: {e}")
                print(f"写入httpx输出日志时出错: {e}")
        
        # 检查输出文件是否存在来判断是否成功
        # 从命令列表中查找-o参数后面的输出文件路径
        output_file = None
        try:
            # 在命令列表中找到-o参数的位置
            output_file_index = cmd.index('-o') + 1
            if output_file_index < len(cmd):
                output_file = cmd[output_file_index]
        except (ValueError, IndexError):
            logger.warning("\u5728命令中未找到输出文件参数")
            
        if output_file:
            if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                logger.info("httpx命令执行成功，输出文件已生成")
                print("httpx命令执行成功，输出文件已生成")
                exitcode = 0  # 即使返回码不是0，但文件存在则认为成功
            elif exitcode == 0:
                logger.info("httpx命令返回成功，但未发现输出文件或文件为空")
                print("httpx命令返回成功，但未发现输出文件或文件为空")
            else:
                logger.error(f"httpx命令执行失败: {stderr}")
                print(f"httpx命令执行失败: {stderr}")
        else:
            if exitcode == 0:
                logger.info("httpx命令执行成功")
                print("httpx命令执行成功")
            else:
                logger.error(f"httpx命令执行失败: {stderr}")
                print(f"httpx命令执行失败: {stderr}")
        
        return exitcode, stdout, stderr
    
    except Exception as e:
        logger.error(f"执行httpx命令时发生错误: {e}")
        print(f"执行httpx命令时发生错误: {e}")
        return -1, "", str(e)
