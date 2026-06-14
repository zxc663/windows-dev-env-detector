# Windows 开发环境检测工具

<p align="center">
  <img src="48x48.ico" width="48" height="48" alt="logo">
</p>

<p align="center">
  <strong>一键扫描 · 智能检测 · 开源免费</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/版本-v1.9.1-blue.svg">
  <img src="https://img.shields.io/badge/平台-Windows-lightgrey.svg">
  <img src="https://img.shields.io/badge/Python-3.8%2B-green.svg">
</p>

---

## 概述

Windows 开发环境检测工具是一款专为开发者设计的本地环境扫描器，无需联网即可快速识别系统中已安装的开发工具、运行时、数据库、包管理器等依赖环境，帮助你在新机器上快速排查环境缺失。

> 十三希诺定制 · 纯 Windows 专属

---

## 功能特性

- 快速扫描 30+ 常见开发工具与运行时
- 支持三种检测模式（宽松 / 专业 / 严格）
- 实时检测日志与分组结果展示
- 搜索与状态筛选（已安装 / 未安装）
- 右键复制软件信息、打开文件路径、百度搜索
- 导出检测报告与日志文件
- 检测缓存机制，重复检测更快

---

## 检测范围

| 类别 | 涵盖工具 |
|------|---------|
| 基础工具 | Python, Git, VS Code, Curl, Wget |
| 编程语言 | Java (JDK), Node.js, Go, PHP, Ruby, Rust, GCC/G++, .NET |
| 包管理器 | npm, yarn, pnpm |
| 数据库 | MySQL, PostgreSQL, SQL Server, Redis, MongoDB |
| 中间件 | RabbitMQ, Nacos |
| 容器云原生 | Docker, Docker Compose, kubectl, VMware, VirtualBox |
| Web 服务 | Nginx, Apache, Tomcat, Maven, Gradle |
| 接口工具 | Postman, Apifox, Xshell, Telnet, SSH |
| Windows 专属 | VC++ 运行库, DirectX, Windows Terminal, Cmder |
| 文档工具 | Typora |

---

## 检测模式说明

| 模式 | 说明 |
|------|------|
| 宽松模式 | 只要检测到任意证据即判定为已安装 |
| 专业模式（默认） | 综合多维度检测，智能判断 |
| 严格模式 | 必须验证到具体版本号才算已安装 |

---

## 安装使用

### 直接下载

从 [Releases](../../releases) 下载最新版 开发环境检测v1.9.1.exe 直接运行，无需安装 Python。

### 源码运行

`ash
# 克隆仓库
git clone https://github.com/zxc663/windows-dev-env-detector.git
cd windows-dev-env-detector

# 运行（Python 3.8+）
python dev_env_detector.py
`

---

## 技术栈

- **Python 3.8+** — 核心语言
- **Tkinter** — 原生 GUI 框架（无需额外依赖）
- **PyInstaller** — 打包为单文件 exe
- **Windows Registry / Environment / CMD** — 多维度检测

---

## 项目结构

`
windows-dev-env-detector/
├── dev_env_detector.py    # 主程序（单文件）
├── 48x48.ico              # 程序图标
├── config.json            # 配置文件
├── version_info.py        # 版本信息（PyInstaller 用）
└── .gitignore             # Git 忽略规则
`

---

## 构建打包

`ash
pip install pyinstaller
pyinstaller --noconfirm --clean --onefile --windowed 
  --name "开发环境检测v1.9.1" 
  --icon "48x48.ico" 
  --add-data "48x48.ico;." 
  dev_env_detector.py
`

---

## 更新日志

详见 [更新日志](dev_env_detector.py#L34-L80)

---

## 许可

本项目仅供个人学习与使用。