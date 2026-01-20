# SUEP一键充值电费程序

## 项目简介

本项目提高了充电费的效率，可实现一键充值。并且自动登陆VPN，使用Docker-EasyConnect实现静默登陆VPN，无需打开EasyConnect软件。

## 使用方法
所需条件
- uv
- docker

1. 请先仿照`.env_example`创建并修改`.env`，填写对应信息。
2. 使用`uv`运行 `main.py`
```bash
  uv run main.py
```
也可使用`pyinstaller`进行打包，获得可执行程序后直接使用。

> 注意：
    本方法目前需要使用Docker-easyconnetc来进行EasyConnect的静默登录。**所以使用之前必须确保已经正确安装Docker**

## 鸣谢

使用了[docker-easyconnect](https://github.com/docker-easyconnect/docker-easyconnect)实现静默登录EasyConnect
使用了[SUEP-TOOKIT](https://github.com/zhengxyz123/suep-toolkit)的开源代码,在此基础上增加了一些功能，
原项目采用MIT-LICENSE，本项目继承并遵循原项目的许可证。

## 声明

**由于涉及充值花费，请使用者慎用。**
由于使用本程序造成的损失，由使用者本人负责。
