import json
import os
import subprocess
import sys
import time
from datetime import date

import requests
from bs4 import BeautifulSoup



class AuthServiceError(Exception):
    """当未登陆或登陆失败时引发此异常。"""

    pass


class VPNError(Exception):
    """当疑似未开启 VPN 时引发此异常。"""

    pass


def test_network(proxy_config, timeout: float = 0.5) -> bool:
    ip_addrs = [
        "http://10.50.2.206",
        "http://10.166.18.114",
        "http://10.166.19.26",
        "http://10.168.103.76",
    ]

    ok = 0
    for url in ip_addrs:
        try:
            requests.get(url, timeout=timeout, proxies= proxy_config)
            ok += 1
            time.sleep(0.5)
        except Exception:
            # print("can't connect to %s" % url)
            pass

    return ok / len(ip_addrs) >= 0.5


def semester_week() -> int:
    """获取当前教学周。

    特别地，`-1` 表示暑假，`-2` 表示寒假。
    """
    jwc_url = "https://jwc.shiep.edu.cn/"
    response = requests.get(jwc_url)
    response.raise_for_status()
    dom = BeautifulSoup(response.text, features="html.parser")

    semeter_start = date.fromisoformat(dom.select("div#semester_start")[0].text)
    semeter_end = date.fromisoformat(dom.select("div#semester_end")[0].text)
    if (date.today() - semeter_start).days < 0 or (date.today() - semeter_end).days > 0:
        return -1 if date.today().month > 5 else -2
    else:
        return (date.today() - semeter_start).days // 7

def get_resource_path(relative_path):
    """ 获取资源的绝对路径，兼容开发环境和打包后的环境 """
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller 会创建一个临时文件夹 _MEIPASS 来存放解压后的文件
        base_path = sys._MEIPASS
    else:
        # 开发环境或者未打包的情况
        base_path = os.path.abspath("..") # 或者 os.path.dirname(__file__)
    return os.path.join(base_path, relative_path)



def setup_global_proxy():
    # 返回 SOCKS5 代理配置，用于 requests Session
    # 不再全局 patch socket，避免影响 asyncio 等库
    proxy_config = {
        'http': 'socks5://127.0.0.1:1080',
        'https': 'socks5://127.0.0.1:1080'
    }
    print("✅ 代理配置已返回")
    return proxy_config

def ensure_docker_engine():
    """检查 Docker Engine 是否启动，若未启动则尝试唤醒 Docker Desktop"""
    try:
        # 尝试运行一个简单的 docker 命令
        subprocess.run(["docker", "info"], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️ 检测到 Docker 未启动，请先唤醒 Docker Desktop...")
        # 常见的 Docker Desktop 安装路径
        return False

def save_info(path, data):
    with open(path, "w") as f:
        json.dump(data, f)

def get_info(path):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return None

__all__ = (
    "AuthServiceError",
    "VPNError",
    "test_network",
    "semester_week",
    "get_resource_path",
    "setup_global_proxy",
    "ensure_docker_engine"
)