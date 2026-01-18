import socket
import threading
import tkinter as tk
from tkinter import messagebox, ttk

import socks
from bs4 import BeautifulSoup
from requests import HTTPError
from toolkit.electricity import RechargeInfo
from toolkit import auth, electricity
from toolkit.util import  get_resource_path, AuthServiceError
import subprocess
import time
import os
import sys
from dotenv import load_dotenv


buildings_dict = {
    "一号学生公寓":"C1",
    "二号学生公寓":"C2",
    "三号学生公寓":"C3",
    "四号学生公寓":"C4",
    "五号学生公寓":"C5",
    "六号学生公寓":"C6",
    "七号学生公寓":"C7",
    "八号学生公寓":"C8",
    "九号学生公寓":"C9",
    "留学生及教师公寓":"B6",
}

# 加载根目录下的 .env 文件
load_dotenv()

VPN_CONTAINER_NAME = os.getenv("VPN_CONTAINER_NAME", "easyconnect_vpn")

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


def is_vpn_running() -> bool:
    try:
        # 使用 inspect 检查容器状态更准确
        out = subprocess.check_output(
            ["docker", "inspect", "-f", "{{.State.Running}}", VPN_CONTAINER_NAME],
            text=True, stderr=subprocess.DEVNULL
        )
        return "true" in out.lower()
    except Exception:
        return False

def login_vpn():

    if not ensure_docker_engine():
        sys.exit(1)

    if is_vpn_running():
        print("🔗 VPN 已在后台运行。")
        return

    # 检查是否存在已停止的同名容器，如果有则先删除（防止 --name 冲突）
    subprocess.run(["docker", "rm", "-f", VPN_CONTAINER_NAME], capture_output=True)

    print("🚀 启动 EasyConnect VPN（Docker 静默模式）...")

    # 1. 从环境变量获取数据
    server = os.getenv("EC_SERVER_URL")
    user = os.getenv("EC_USERNAME")
    pwd = os.getenv("EC_PASSWORD")
    ver = os.getenv("EC_VER", "7.6.3")

    # 2. 构建镜像要求的 CLI_OPTS 字符串
    # 格式必须严格对应：-d [地址] -u [账号] -p [密码]
    cli_opts = f"-d {server} -u {user} -p {pwd}"

    # 3. 构建完整的 docker run 指令
    cmd = [
        "docker", "run", "-d",
        "--name", VPN_CONTAINER_NAME,
        "--rm",
        "--device", "/dev/net/tun",
        "--cap-add", "NET_ADMIN",
        "-p", "127.0.0.1:1080:1080",
        "-p", "127.0.0.1:8888:8888",
        "-e", f"EC_VER={ver}",
        "-e", f"CLI_OPTS={cli_opts}",
        "hagb/docker-easyconnect:cli"
    ]

    print(f"🚀 正在为用户 {user} 启动 VPN 容器...")
    try:
        # 使用 subprocess 运行
        subprocess.check_call(cmd)
        print("✅ 容器启动指令发送成功。")
    except subprocess.CalledProcessError as e:
        print(f"❌ 启动失败，请检查 Docker 是否运行或容器名是否冲突: {e}")


def stop_vpn():
    """任务结束后调用此函数"""
    print("🔌 充电任务完成，正在关闭并清理 VPN 容器...")
    # 只要执行 stop，因为启动时加了 --rm，容器会自动被删除
    subprocess.run(["docker", "stop", VPN_CONTAINER_NAME], capture_output=True)


def login(username, password, site = "http://10.50.2.206:80/"):
    # service 必须与下面一行所展示的精确相符，都为 22 个字符！
    service = auth.AuthService(username, password, service=site, renew="true")
    # 是否需要输入验证码？
    if service.need_captcha():
        print("有？")
        # 获取并保存验证码:
        with open("captcha.jpg", "wb") as captcha_image:
            captcha_image.write(service.get_captcha_image())
        # 填写验证码:
        service.set_captcha_code("验证码")
    # 登陆:
    try:
        service.login()
    except HTTPError as e:
        print(e)
    return service

def pay_electricity(building_code, fee_site, site_user, site_pass, room, amount, delay)->RechargeInfo:

    service = login(site_user, site_pass, site=fee_site)
    time.sleep(delay)

    em = electricity.ElectricityManagement(service.session)
    # 充值电费
    em.recharge(building_code, room, amount)
    # 获取历次的电表充值账单：
    all_payments = list(em.recharge_info)
    service.logout()
    return all_payments[0]

def setup_global_proxy():
    # 强制所有底层 socket 走 SOCKS5 代理
    socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 1080)
    socket.socket = socks.socksocket
    print("✅ 全局 Socket 代理已配置")

# === GUI 界面 ===
class App:
    def __init__(self, root):
        self.root = root
        root.title("自动电费缴纳工具")

        # 读取默认配置
        self.user = os.getenv('FEE_USER', '')
        self.pwd = os.getenv('FEE_PASSWORD', '')
        self.fee_site = os.getenv('FEE_SITE', '')
        self.delay = os.getenv('FEE_DELAY', '5')
        self.room = os.getenv('FEE_ROOM', '')
        self.building_code = os.getenv('FEE_BUILDING', '')
        self.amount = os.getenv('FEE_AMOUNT', '1')

        # 宿舍楼选择下拉框
        tk.Label(root, text="宿舍楼号：").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.building_combobox = ttk.Combobox(root, values=list(buildings_dict.keys()), state="readonly")
        self.building_combobox.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        # 设置默认选中第一个选项
        if buildings_dict and self.building_code:
            # print(self.building_code)
            select = int(self.building_code[1]) - 1
            self.building_combobox.current(0)

        # Input fields
        tk.Label(root, text="充值房间号：").grid(row=1, column=0)
        self.entry_room = tk.Entry(root)
        self.entry_room.insert(0, self.room)
        self.entry_room.grid(row=1, column=1)

        tk.Label(root, text="充值金额：").grid(row=2, column=0)
        self.entry_amount = tk.Entry(root)
        self.entry_amount.insert(0, self.amount)
        self.entry_amount.grid(row=2, column=1)

        tk.Label(root, text="VPN 用户：").grid(row=3, column=0)
        self.entry_vpn_user = tk.Entry(root)
        self.entry_vpn_user.insert(0, self.user)
        self.entry_vpn_user.grid(row=3, column=1)

        tk.Label(root, text="VPN 密码：").grid(row=4, column=0)
        self.entry_vpn_pass = tk.Entry(root, show="*")
        self.entry_vpn_pass.insert(0, self.pwd)
        self.entry_vpn_pass.grid(row=4, column=1)

        # Start按钮
        self.btn_start = tk.Button(root, text="开始缴费", command=self.start)
        self.btn_start.grid(row=6, column=0, columnspan=2, pady=10)

    def start(self):
        room = self.entry_room.get().strip() or self.room.strip()
        amount = self.entry_amount.get().strip() or self.amount.strip()
        user = self.entry_vpn_user.get().strip() or self.user.strip()
        pwd = self.entry_vpn_pass.get().strip() or self.pwd.strip()

        # 获取选中的宿舍楼
        selected_building = self.building_combobox.get()
        # 获取对应的建筑代码
        building_code = buildings_dict.get(selected_building, "")

        if not room or not amount:
            messagebox.showwarning("输入错误", "请填写充值房间号和金额！")
            return

        self.btn_start.config(state=tk.DISABLED)
        messagebox.showinfo("提示", "开始执行自动缴费，请勿操作鼠标键盘。")

        # main.py 中修改 task() 内部逻辑
        def task():
            try:
                login_vpn()

                # 关键：给容器内的 EasyConnect 留出启动和拨号时间
                print("⏳ 等待隧道建立...")
                time.sleep(10)
                setup_global_proxy()

                get = pay_electricity(building_code, self.fee_site, user, pwd, room, amount, int(self.delay.strip()))
                messagebox.showinfo("完成",
                                    "自动缴费流程已完成！\n时间：" + str(get.time) + "\n 充值金额：" + str(get.money))
            except Exception as e:
                messagebox.showerror("错误", f"发生异常: {e}")
            finally:
                stop_vpn()
                self.btn_start.config(state=tk.NORMAL)

        threading.Thread(target=task, daemon=True).start()

if __name__ == '__main__':
    root = tk.Tk()
    App(root)
    root.mainloop()