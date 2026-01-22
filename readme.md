# SUEP一键充值电费程序

## 项目简介

本项目提高了充电费的效率，可实现一键充值。并且自动登陆VPN，使用Docker-EasyConnect实现静默登陆VPN，无需打开EasyConnect软件。


## 使用方法

1. 基础准备
- uv 
- docker

2. 安装依赖
```bash
   uv sync
```
3. 运行，注意必须在终端执行
```bash
   uv run main.py
```

> 注意：
    本方法目前需要使用Docker-easyconnetc来进行EasyConnect的静默登录。**所以使用之前必须确保已经正确安装Docker**

## 项目技术
| 相关技术资源       | 作用          |
|--------------|-------------|
| uv           | python包管理工具 |
| request      | 发送web请求     |
| BeautifulSoup | 解析网页内容      |
| questionary  |实现控制台询问|
|docker| 实现vpn的静默登录|
|socket| 实现代理设置|


## 鸣谢

使用了[docker-easyconnect](https://github.com/docker-easyconnect/docker-easyconnect)实现静默登录EasyConnect   
使用了[SUEP-TOOKIT](https://github.com/zhengxyz123/suep-toolkit)的开源代码,在此基础上增加了一些功能，
原项目采用MIT-LICENSE，本项目继承并遵循原项目的许可证。

## 声明

**由于涉及充值花费，请使用者慎用。**
由于使用本程序造成的损失，由使用者本人负责。
