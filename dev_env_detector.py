# -*- coding: utf-8 -*-
"""
Windows 开发环境检测工具 v1.9.1
十三希诺定制｜纯Windows专属，仅做环境检测
"""

import os
import sys
import subprocess
import threading
import time
import winreg
import ctypes

# 启用高DPI支持
if sys.platform == 'win32':
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import re
from typing import List, Tuple, Dict, Any
from dataclasses import dataclass, field
from enum import Enum

APP_VERSION = "v1.9.1"

CHANGE_LOG = """更新日志

v1.9.1 (2026-06-12)
- 修复筛选/搜索后列表内容无法正常显示的问题（canvas scrollregion 未刷新）
- 修复下拉框"已安装/未安装"筛选结果空白的问题
- 优化 UI 重建流程，确保筛选后滚动区域同步更新

v1.9.0 (2026-06-12)
- 界面布局优化，状态栏信息补充
- 去除冗余代码，提升启动速度
- 文本对齐优化，修正偏移显示问题

v1.8.0 (2026-06-11)
- 注册表检测方法全面修复，确保检测准确
- 严格模式通配符过滤逻辑修正
- 检测时按钮状态管理优化，避免误操作

v1.7.0 (2026-06-10)
- 新增三种检测模式：宽松模式、专业模式、严格模式
- 专业模式为默认模式，检测更智能
- 修复弹窗滚轮事件影响主页面滑动

v1.6.0 (2026-06-09)
- 按钮文字渲染优化，修正居中偏移
- 简化布局结构，移除不必要的可拖拽分割

v1.5.0 (2026-06-08)
- 筛选下拉框事件绑定优化，确保响应可靠
- 日志输出异步刷新，提升检测流畅度

v1.4.0 (2026-06-07)
- 悬浮提示交互优化，鼠标停留保持显示

v1.3.0 (2026-06-06)
- 检测结果展示优化，多版本信息清晰呈现

v1.2.0 (2026-06-05)
- 环境变量路径解析逻辑优化

v1.1.0 (2026-06-04)
- 命令行检测输出解析增强

v1.0.1 (2026-06-02)
- 基础功能修复与稳定性提升

v1.0.0 (2026-06-01)
- 首版发布，Windows 开发环境检测"""

class SoftwareStatus(Enum):
    INSTALLED = "已安装"
    NOT_INSTALLED = "未安装"
    UNKNOWN = "未知"

class DetectionMode(Enum):
    LOOSE = "宽松模式"
    PROFESSIONAL = "专业模式"
    STRICT = "严格模式"

@dataclass
class Software:
    name: str
    check_methods: List[Tuple[str, str, str]] = field(default_factory=list)
    dll_files: List[str] = field(default_factory=list)
    status: SoftwareStatus = SoftwareStatus.NOT_INSTALLED
    version: str = ""
    source: str = ""
    path: str = ""
    all_versions: List[Tuple[str, str, str]] = field(default_factory=list)
    enabled: bool = True

@dataclass
class SoftwareGroup:
    name: str
    items: List[Software] = field(default_factory=list)

def get_all_groups() -> List[SoftwareGroup]:
    return [
        SoftwareGroup("基础通用工具", [
            Software("Python", [("cmd", "python --version", r"Python ([\d.]+)"), ("env", "PYTHON_HOME", None), ("registry", r"SOFTWARE\Python\PythonCore", None)]),
            Software("Git", [("cmd", "git --version", r"git version ([\d.]+)"), ("env", "GIT_HOME", None), ("registry", r"SOFTWARE\GitForWindows", None)]),
            Software("VS Code", [("cmd", "code --version", r"([\d.]+)"), ("env", "VSCODE_HOME", None), ("registry", r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{FD0FA333-5239-4D98-93F2-A51DCF95D2DA*}", None)]),
            Software("Curl", [("cmd", "curl --version", r"curl ([\d.]+)"), ("env", "CURL_HOME", None)]),
            Software("Wget", [("cmd", "wget --version", r"Wget ([\d.]+)"), ("env", "WGET_HOME", None)]),
        ]),
        SoftwareGroup("主流编程语言 & 编译环境", [
            Software("Java (JDK)", [("cmd", "java -version 2>&1", r"version \"([\d._]+)\""), ("env", "JAVA_HOME", None), ("registry", r"SOFTWARE\JavaSoft\Java Development Kit", None)]),
            Software("Node.js", [("cmd", "node --version", "v([\\d.]+)"), ("env", "NODE_HOME", None), ("registry", r"SOFTWARE\nodejs", None)]),
            Software("Go", [("cmd", "go version", "go([\\d.]+)"), ("env", "GOROOT", None), ("registry", r"SOFTWARE\Go", None)]),
            Software("PHP", [("cmd", "php --version", "PHP ([\\d.]+)"), ("env", "PHPRC", None), ("registry", r"SOFTWARE\PHP", None)]),
            Software("Ruby", [("cmd", "ruby --version", "ruby ([\\d.]+)"), ("env", "RUBY_HOME", None)]),
            Software("Rust", [("cmd", "rustc --version", "rustc ([\\d.]+)"), ("env", "RUSTUP_HOME", None)]),
            Software("GCC/G++", [("cmd", "gcc --version", "gcc.* ([\\d.]+)"), ("env", "MINGW_ROOT", None)]),
            Software(".NET 运行时 & SDK", [("cmd", "dotnet --version", "([\\d.]+)"), ("env", "DOTNET_ROOT", None)]),
        ]),
        SoftwareGroup("包管理器 & 前端工具", [
            Software("npm", [("cmd", "npm --version", "([\\d.]+)")]),
            Software("yarn", [("cmd", "yarn --version", "([\\d.]+)")]),
            Software("pnpm", [("cmd", "pnpm --version", "([\\d.]+)")]),
        ]),
        SoftwareGroup("数据库 & 中间件", [
            Software("MySQL/MariaDB", [("cmd", "mysql --version", "Ver ([\\d.]+)"), ("env", "MYSQL_HOME", None), ("registry", r"SOFTWARE\MySQL AB", None)]),
            Software("PostgreSQL", [("cmd", "psql --version", "psql \\(PostgreSQL\\) ([\\d.]+)"), ("env", "PGHOME", None)]),
            Software("SQL Server", [("cmd", "sqlcmd -? 2>&1", ""), ("env", "SQLSERVER_HOME", None)]),
            Software("Redis", [("cmd", "redis-cli --version", "redis-cli ([\\d.]+)"), ("env", "REDIS_HOME", None)]),
            Software("MongoDB", [("cmd", "mongod --version", "db version ([\\d.]+)"), ("env", "MONGODB_HOME", None)]),
            Software("RabbitMQ", [("cmd", "rabbitmqctl status 2>&1", ""), ("env", "RABBITMQ_HOME", None)]),
            Software("Nacos", [("env", "NACOS_HOME", None)]),
        ]),
        SoftwareGroup("容器 & 虚拟化 & 云原生", [
            Software("Docker", [("cmd", "docker --version", "Docker version ([\\d.]+)"), ("env", "DOCKER_HOME", None)]),
            Software("Docker Compose", [("cmd", "docker-compose --version", "docker-compose ([\\d.]+)")]),
            Software("kubectl (K8s)", [("cmd", "kubectl version --client 2>&1", "Client Version: v([\\d.]+)")]),
            Software("VMware Workstation", [("cmd", "vmrun -v 2>&1", "([\\d.]+)"), ("registry", r"SOFTWARE\VMware, Inc.\VMware Workstation", None)]),
            Software("VirtualBox", [("cmd", "vboxmanage --version", "([\\d.]+)"), ("env", "VBOX_MSI_INSTALL_PATH", None)]),
        ]),
        SoftwareGroup("Web 服务 & 项目构建工具", [
            Software("Nginx", [("cmd", "nginx -v 2>&1", "nginx/([\\d.]+)"), ("env", "NGINX_HOME", None)]),
            Software("Apache", [("cmd", "httpd -v 2>&1", "Apache/([\\d.]+)"), ("env", "APACHE_HOME", None)]),
            Software("Tomcat", [("env", "CATALINA_HOME", None)]),
            Software("Maven", [("cmd", "mvn --version", "Apache Maven ([\\d.]+)"), ("env", "MAVEN_HOME", None)]),
            Software("Gradle", [("cmd", "gradle --version", "Gradle ([\\d.]+)"), ("env", "GRADLE_HOME", None)]),
        ]),
        SoftwareGroup("接口 & 运维调试工具", [
            Software("Postman", [("cmd", "where postman 2>NUL", ""), ("env", "POSTMAN_HOME", None)]),
            Software("Apifox", [("cmd", "where apifox 2>NUL", ""), ("env", "APIFOX_HOME", None)]),
            Software("Xshell/FinalShell", [("env", "XSHELL_HOME", None)]),
            Software("Telnet", [("cmd", "where telnet 2>NUL", "")]),
            Software("SSH", [("cmd", "ssh -v 2>&1", "OpenSSH_([\\d.]+)")]),
        ]),
        SoftwareGroup("Windows 专属运行库 & 系统工具", [
            Software("VC++ 运行库", [("registry", r"SOFTWARE\Microsoft\VisualStudio\*\VC Components", None)]),
            Software("DirectX", [("cmd", "where dxdiag 2>NUL", ""), ("registry", r"SOFTWARE\Microsoft\DirectX", None)]),
            Software("Windows Terminal", [("cmd", "where wt 2>NUL", ""), ("env", "WT_PROFILE_ID", None)]),
            Software("Cmder", [("env", "CMDER_ROOT", None)]),
        ]),
        SoftwareGroup("文档辅助工具", [
            Software("Typora", [("cmd", "where typora 2>NUL", ""), ("cmd", "dir /b \"%LOCALAPPDATA%\\Typora\" 2>&1", ""), ("env", "TYPORA_HOME", None), ("registry", r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{*Typora*}", None)]),
        ]),
    ]

class Detector:
    @classmethod
    def detect_software(cls, software: Software, mode: DetectionMode = DetectionMode.PROFESSIONAL) -> Tuple[SoftwareStatus, str, str, str, List[Tuple[str, str, str]]]:
        all_found = []
        method_count = 0

        for method_type, method_value, pattern in software.check_methods:
            method_found = False
            if method_type == "cmd":
                cmd_name = method_value.split()[0]
                all_paths = cls.find_all_executable_paths(cmd_name)
                for exe_path in all_paths:
                    if not exe_path or not os.path.isfile(exe_path):
                        continue
                    version = cls.get_version_from_executable(exe_path, pattern)
                    has_version = bool(version) and version != "-"
                    if mode == DetectionMode.STRICT:
                        if not has_version and pattern:
                            continue
                    if version or True:
                        all_found.append((version or "-", exe_path, f"命令行({cmd_name})"))
                        method_found = True

            elif method_type == "env":
                var_name = method_value
                value = os.environ.get(var_name)
                if value and os.path.exists(value):
                    ver = cls._get_version_from_dir(value)
                    if mode == DetectionMode.STRICT:
                        if not ver:
                            continue
                    all_found.append((ver or "-", value, f"环境变量({var_name})"))
                    method_found = True

            elif method_type == "registry":
                if "*" in method_value:
                    all_reg_values = cls._check_registry_all_with_wildcard(method_value, software.name)
                    if mode == DetectionMode.STRICT:
                        all_reg_values = [rv for rv in all_reg_values if rv[0] and rv[0] != "-"]
                    if all_reg_values:
                        all_found.extend(all_reg_values)
                        method_found = True
                else:
                    found, value = cls.check_registry(method_value)
                    if found:
                        ver = cls._get_registry_version(method_value)
                        if mode == DetectionMode.STRICT and (not ver):
                            pass
                        else:
                            all_found.append((ver or "-", value, f"注册表({method_value})"))
                            method_found = True

            if method_found:
                method_count += 1

        if not all_found:
            return SoftwareStatus.NOT_INSTALLED, "", "", "", []

        if mode == DetectionMode.STRICT and method_count < 2:
            return SoftwareStatus.NOT_INSTALLED, "", "", "", []

        seen = set()
        unique_found = []
        for v, p, s in all_found:
            key = (v, p)
            if key not in seen:
                seen.add(key)
                unique_found.append((v, p, s))

        primary = unique_found[0]
        return SoftwareStatus.INSTALLED, primary[0], primary[2], primary[1], unique_found

    @staticmethod
    def find_all_executable_paths(exe_name: str) -> List[str]:
        paths = []
        try:
            result = subprocess.run(f"where {exe_name} 2>NUL", shell=True, capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    line = line.strip()
                    if line and os.path.isfile(line):
                        paths.append(line)
        except Exception:
            pass
        return paths

    @staticmethod
    def get_version_from_executable(exe_path: str, pattern: str) -> str:
        try:
            result = subprocess.run(f'"{exe_path}" --version 2>&1', shell=True, capture_output=True, text=True, timeout=5)
            output = result.stdout + result.stderr
            if pattern:
                match = re.search(pattern, output)
                if match:
                    return match.group(1)
            return output.strip()[:50] if output.strip() else ""
        except Exception:
            return ""

    @staticmethod
    def _get_version_from_dir(dir_path: str) -> str:
        if not dir_path or not os.path.isdir(dir_path):
            return ""
        dir_name = os.path.basename(dir_path)
        match = re.match(r"[\d.]+", dir_name)
        if match:
            return match.group(0)
        return ""

    @staticmethod
    def check_registry(path: str) -> Tuple[bool, str]:
        hives = [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]
        for hive in hives:
            try:
                key = winreg.OpenKey(hive, path, 0, winreg.KEY_READ | winreg.KEY_WOW64_32KEY)
                try:
                    num_values = winreg.QueryInfoKey(key)[1]
                    for i in range(num_values):
                        try:
                            name, data, _ = winreg.EnumValue(key, i)
                            if name in ("InstallLocation", "Path", "DisplayIcon"):
                                if data and os.path.exists(data):
                                    return True, data
                        except Exception:
                            pass
                finally:
                    key.Close()
                return True, path
            except FileNotFoundError:
                continue
            except Exception:
                continue
        return False, ""

    @staticmethod
    def _get_registry_version(path: str) -> str:
        hives = [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]
        for hive in hives:
            try:
                key = winreg.OpenKey(hive, path, 0, winreg.KEY_READ | winreg.KEY_WOW64_32KEY)
                try:
                    num_values = winreg.QueryInfoKey(key)[1]
                    for i in range(num_values):
                        try:
                            name, data, _ = winreg.EnumValue(key, i)
                            if name in ("DisplayVersion", "Version", "ProductVersion"):
                                return str(data)
                        except Exception:
                            pass
                finally:
                    key.Close()
            except Exception:
                continue
        return ""

    @staticmethod
    def _check_registry_all_with_wildcard(path_pattern: str, software_name: str) -> List[Tuple[str, str, str]]:
        results = []
        try:
            base_path = path_pattern.split('\\{')[0]
            hives = [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]
            for hive in hives:
                try:
                    parent_key = winreg.OpenKey(hive, base_path, 0, winreg.KEY_READ | winreg.KEY_WOW64_32KEY)
                    try:
                        num_subkeys = winreg.QueryInfoKey(parent_key)[0]
                        for i in range(num_subkeys):
                            try:
                                name = winreg.EnumKey(parent_key, i)
                                is_guid = name.startswith("{")
                                contains_name = software_name.lower() in name.lower()
                                if is_guid and contains_name:
                                    full_path = f"{base_path}\\{name}"
                                    try:
                                        sub_key = winreg.OpenKey(hive, full_path, 0, winreg.KEY_READ | winreg.KEY_WOW64_32KEY)
                                        try:
                                            path_val = ""
                                            version_val = ""
                                            num_vals = winreg.QueryInfoKey(sub_key)[1]
                                            for j in range(num_vals):
                                                try:
                                                    vname, vdata, _ = winreg.EnumValue(sub_key, j)
                                                    if vname == "InstallLocation":
                                                        path_val = vdata
                                                    elif vname in ("DisplayVersion", "Version"):
                                                        version_val = str(vdata)
                                                except Exception:
                                                    pass
                                            if path_val and os.path.exists(path_val):
                                                results.append((version_val or "-", path_val, f"注册表({full_path})"))
                                        finally:
                                            sub_key.Close()
                                    except Exception:
                                        pass
                            except Exception:
                                pass
                    finally:
                        parent_key.Close()
                except FileNotFoundError:
                    continue
        except Exception:
            pass
        return results

class DevEnvDetectorApp:
    COLORS = {
        'primary': '#667eea',
        'primary_dark': '#5a6fc7',
        'success': '#10b981',
        'warning': '#f59e0b',
        'danger': '#ef4444',
        'bg_main': '#f1f5f9',
        'bg_sidebar': '#1e293b',
        'bg_card': '#ffffff',
        'bg_header': '#334155',
        'text_primary': '#1e293b',
        'text_header': '#ffffff',
        'text_secondary': '#64748b',
        'text_sidebar': '#94a3b8',
        'installed': '#10b981',
        'not_installed': '#94a3b8',
        'border': '#e2e8f0',
    }

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Windows 开发环境检测工具  十三希诺定制")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        self.root.configure(bg=self.COLORS['bg_main'])

        # 尝试加载图标
        if getattr(sys, 'frozen', False):
            # PyInstaller onefile 打包模式
            bundle_dir = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
            icon_path = os.path.join(bundle_dir, "48x48.ico")
            if not os.path.exists(icon_path):
                icon_path = os.path.join(os.path.dirname(sys.executable), "48x48.ico")
        else:
            # 开发模式
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "48x48.ico")
        try:
            self.root.iconbitmap(icon_path)
            try:
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("dev.env.detector.190")
            except Exception:
                pass
        except Exception:
            pass

        self.full_groups = get_all_groups()
        self.groups = self.full_groups
        self.is_detecting = False
        self.stats = {"total": 0, "installed": 0, "not_installed": 0}
        self.filter_status = tk.StringVar(value="全部")
        self.detection_mode = DetectionMode.PROFESSIONAL

        self.detection_cache = {}
        self.error_logs = []
        self.log_entries = []

        self.search_var = tk.StringVar()
        self.tooltip_window = None
        self._tooltip_after_id = None
        self._log_pending = []
        self._log_lock = threading.Lock()
        self._log_flush_scheduled = False
        self._canvas_scroll_scheduled = False

        self._setup_ui()

    def _setup_ui(self):
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 底部状态栏 - 最先pack(side=BOTTOM)，确保优先占据空间，不会被挤出
        status_frame = tk.Frame(main_frame, relief=tk.SOLID, bd=1, bg="#e8e8e8")
        status_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(5, 0))

        # 右侧信息 - 先pack(side=RIGHT)，从右向左排列，优先分配空间，小窗口下不会被裁剪
        self.custom_label = tk.Label(status_frame, text="十三希诺定制", bg="#e8e8e8",
                                      fg="#8e44ad", font=("Microsoft YaHei", 9, "bold"))
        self.custom_label.pack(side=tk.RIGHT, padx=(0, 8), pady=4)

        tk.Label(status_frame, text="|", bg="#e8e8e8", fg="#bbbbbb", font=("Microsoft YaHei", 9)).pack(side=tk.RIGHT, pady=4)

        self.version_label = tk.Label(status_frame, text=APP_VERSION, bg="#e8e8e8",
                                       fg="#555555", font=("Microsoft YaHei", 9))
        self.version_label.pack(side=tk.RIGHT, padx=(8, 0), pady=4)

        # 左侧信息 - 后pack(side=LEFT)，占据左侧剩余空间，窗口缩小只裁剪左侧
        self.status_label = tk.Label(status_frame, text="总计: 0 项 | 已安装: 0 项 | 未安装: 0 项",
                                      anchor=tk.W, bg="#e8e8e8", fg="#333333", font=("Microsoft YaHei", 9))
        self.status_label.pack(side=tk.LEFT, padx=8, pady=4)

        self.time_label = tk.Label(status_frame, text="", bg="#e8e8e8",
                                    fg="#666666", font=("Microsoft YaHei", 9))
        self.time_label.pack(side=tk.LEFT, padx=(0, 16), pady=4)

        self.mode_label = tk.Label(status_frame, text="专业模式", bg="#e8e8e8",
                                    fg="#667eea", font=("Microsoft YaHei", 9, "bold"))
        self.mode_label.pack(side=tk.LEFT, pady=4)

        # 搜索区域
        search_frame = tk.Frame(main_frame, bg="#f0f0f0")
        search_frame.pack(fill=tk.X, pady=(0, 4))

        tk.Label(search_frame, text="搜索:", bg="#f0f0f0", fg="#333333",
                 font=("Microsoft YaHei", 9)).pack(side=tk.LEFT, padx=(8, 5), pady=6)
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var,
                                      font=("Microsoft YaHei", 9), bg="white", fg="#333333",
                                      relief=tk.FLAT, bd=0, highlightthickness=1, highlightbackground="#e2e8f0", highlightcolor="#667eea")
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=6)
        self.search_entry.bind("<KeyRelease>", lambda e: self.on_search_or_filter_changed())
        self.search_entry.bind("<<Paste>>", lambda e: self.root.after(50, self.on_search_or_filter_changed))

        clear_btn = tk.Button(search_frame, text="清空", command=self.clear_search,
                              bg="#7f8c8d", fg="white", font=("Microsoft YaHei", 9),
                              relief=tk.FLAT, padx=10, pady=2, cursor="hand2")
        clear_btn.pack(side=tk.LEFT, padx=5, pady=6)
        clear_btn.bind("<Enter>", lambda e: clear_btn.config(bg="#95a5a6"))
        clear_btn.bind("<Leave>", lambda e: clear_btn.config(bg="#7f8c8d"))

        tk.Label(search_frame, text="状态:", bg="#f0f0f0", fg="#333333",
                 font=("Microsoft YaHei", 9)).pack(side=tk.LEFT, padx=(10, 5), pady=6)
        self.status_combo = ttk.Combobox(search_frame, textvariable=self.filter_status,
                                    values=["全部", "已安装", "未安装"],
                                    width=8, font=("Microsoft YaHei", 9))
        self.status_combo.pack(side=tk.LEFT, pady=6, padx=(0, 8))
        self.status_combo.configure(state=['readonly'])
        self.status_combo.bind("<<ComboboxSelected>>", self.on_search_or_filter_changed)
        self.status_combo.bind("<Key>", lambda e: "break")
        self.status_combo.bind("<Button-1>", lambda e: self.status_combo.selection_clear())
        self.status_combo.bind("<FocusIn>", lambda e: self.root.after_idle(self.status_combo.selection_clear))
        self.status_combo.bind("<B1-Motion>", lambda e: self.status_combo.selection_clear())
        self.status_combo['exportselection'] = 0

        # 功能按钮区域
        btn_frame = tk.Frame(main_frame, bg="#f5f5f5")
        btn_frame.pack(fill=tk.X, pady=(0, 5))

        self.start_btn = tk.Button(btn_frame, text="开始检测", command=self.start_detection,
                                    bg="#3498db", fg="white", font=("Microsoft YaHei", 9),
                                    relief=tk.FLAT, padx=12, pady=3, cursor="hand2")
        self.start_btn.pack(side=tk.LEFT, padx=5, pady=6)
        self.start_btn.bind("<Enter>", lambda e: self.start_btn.config(bg="#2980b9"))
        self.start_btn.bind("<Leave>", lambda e: self.start_btn.config(bg="#3498db"))

        self.refresh_btn = tk.Button(btn_frame, text="刷新检测", command=self.start_detection,
                                      state=tk.DISABLED, bg="#95a5a6", fg="white",
                                      font=("Microsoft YaHei", 9), relief=tk.FLAT, padx=12, pady=3, cursor="hand2")
        self.refresh_btn.pack(side=tk.LEFT, padx=5, pady=6)

        self.clear_log_btn = tk.Button(btn_frame, text="清空日志", command=self.clear_log,
                                        bg="#e74c3c", fg="white", font=("Microsoft YaHei", 9),
                                        relief=tk.FLAT, padx=12, pady=3, cursor="hand2")
        self.clear_log_btn.pack(side=tk.LEFT, padx=5, pady=6)
        self.clear_log_btn.bind("<Enter>", lambda e: self.clear_log_btn.config(bg="#c0392b"))
        self.clear_log_btn.bind("<Leave>", lambda e: self.clear_log_btn.config(bg="#e74c3c"))

        self.export_log_btn = tk.Button(btn_frame, text="导出日志", command=self._export_log_to_file,
                                         bg="#27ae60", fg="white", font=("Microsoft YaHei", 9),
                                         relief=tk.FLAT, padx=12, pady=3, cursor="hand2")
        self.export_log_btn.pack(side=tk.LEFT, padx=5, pady=6)
        self.export_log_btn.bind("<Enter>", lambda e: self.export_log_btn.config(bg="#219a52"))
        self.export_log_btn.bind("<Leave>", lambda e: self.export_log_btn.config(bg="#27ae60"))

        self.clear_cache_btn = tk.Button(btn_frame, text="清除缓存", command=self._clear_cache,
                                          bg="#e67e22", fg="white", font=("Microsoft YaHei", 9),
                                          relief=tk.FLAT, padx=12, pady=3, cursor="hand2")
        self.clear_cache_btn.pack(side=tk.LEFT, padx=5, pady=6)
        self.clear_cache_btn.bind("<Enter>", lambda e: self.clear_cache_btn.config(bg="#d35400"))
        self.clear_cache_btn.bind("<Leave>", lambda e: self.clear_cache_btn.config(bg="#e67e22"))

        # 检测模式切换
        mode_frame = tk.Frame(btn_frame, bg="#f5f5f5")
        mode_frame.pack(side=tk.RIGHT, padx=(5, 5), pady=6)
        tk.Label(mode_frame, text="检测模式:", bg="#f5f5f5", fg="#333333",
                 font=("Microsoft YaHei", 9)).pack(side=tk.LEFT, padx=(0, 5))
        self.mode_combo = ttk.Combobox(mode_frame, values=[m.value for m in DetectionMode],
                                       width=8, font=("Microsoft YaHei", 9))
        self.mode_combo.pack(side=tk.LEFT)
        self.mode_combo.configure(state=['readonly'])
        self.mode_combo.set(DetectionMode.PROFESSIONAL.value)
        self.mode_combo.bind("<<ComboboxSelected>>", self._on_mode_changed)
        self.mode_combo.bind("<Key>", lambda e: "break")
        self.mode_combo.bind("<Button-1>", lambda e: self.mode_combo.selection_clear())
        self.mode_combo.bind("<FocusIn>", lambda e: self.root.after_idle(self.mode_combo.selection_clear))
        self.mode_combo.bind("<B1-Motion>", lambda e: self.mode_combo.selection_clear())
        self.mode_combo['exportselection'] = 0

        # 更新日志按钮
        self.changelog_btn = tk.Button(btn_frame, text="更新日志", command=self._show_changelog_popup,
                                        bg="#8e44ad", fg="white", font=("Microsoft YaHei", 9),
                                        relief=tk.FLAT, padx=12, pady=3, cursor="hand2")
        self.changelog_btn.pack(side=tk.RIGHT, padx=5, pady=6)
        self.changelog_btn.bind("<Enter>", lambda e: self.changelog_btn.config(bg="#7d3c98"))
        self.changelog_btn.bind("<Leave>", lambda e: self.changelog_btn.config(bg="#8e44ad"))

        # 主体列表区域
        list_frame = tk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

        self.canvas = tk.Canvas(list_frame, bg="#fafafa")
        scrollbar_y = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        scrollbar_x = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.groups_frame = tk.Frame(self.canvas, bg="#fafafa")
        self._canvas_window_id = self.canvas.create_window((0, 0), window=self.groups_frame, anchor=tk.NW)

        self.groups_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self._bind_scroll_events()
        self._build_groups_ui()

        # 日志区域
        log_frame = tk.Frame(main_frame)
        log_frame.pack(fill=tk.X, pady=(5, 0))

        log_header = tk.Frame(log_frame)
        log_header.pack(fill=tk.X)
        tk.Label(log_header, text="检测日志:", anchor=tk.W,
                 font=("Microsoft YaHei", 9)).pack(side=tk.LEFT)

        self.copy_log_btn = tk.Button(log_header, text="复制日志", command=self._copy_log_to_clipboard,
                                       bg="#7f8c8d", fg="white", font=("Microsoft YaHei", 9),
                                       relief=tk.FLAT, padx=10, pady=1, cursor="hand2")
        self.copy_log_btn.pack(side=tk.RIGHT, padx=(5, 0))
        self.copy_log_btn.bind("<Enter>", lambda e: self.copy_log_btn.config(bg="#95a5a6"))
        self.copy_log_btn.bind("<Leave>", lambda e: self.copy_log_btn.config(bg="#7f8c8d"))

        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, wrap=tk.WORD,
                                                   font=("Consolas", 9), bg="white", fg="#333333",
                                                   relief=tk.SOLID, bd=1)
        self.log_text.pack(fill=tk.X, pady=(5, 0))

    def _show_changelog_popup(self):
        popup = tk.Toplevel(self.root)
        popup.title("更新日志")
        popup.geometry("550x500")
        popup.minsize(450, 350)
        popup.transient(self.root)
        popup.grab_set()
        popup.configure(bg=self.COLORS['bg_main'])

        header = tk.Frame(popup, bg=self.COLORS['primary'])
        header.pack(fill=tk.X)
        tk.Label(header, text="📋 更新日志", bg=self.COLORS['primary'], fg="white",
                 font=("Microsoft YaHei", 14, "bold"), padx=20, pady=12).pack(side=tk.LEFT)
        tk.Label(header, text=APP_VERSION, bg=self.COLORS['primary'], fg="#b3b3b3",
                 font=("Microsoft YaHei", 9), padx=15).pack(side=tk.RIGHT, pady=10)

        body = tk.Frame(popup, bg=self.COLORS['bg_main'], padx=15, pady=10)
        body.pack(fill=tk.BOTH, expand=True)

        text_widget = tk.Text(body, wrap=tk.WORD, font=("Microsoft YaHei", 10),
                               bg=self.COLORS['bg_card'], fg=self.COLORS['text_primary'],
                               bd=1, padx=12, pady=10, relief=tk.SOLID)
        text_widget.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(body, orient=tk.VERTICAL, command=text_widget.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.configure(yscrollcommand=scrollbar.set)

        text_widget.insert(tk.END, CHANGE_LOG)
        text_widget.configure(state=tk.DISABLED)

        btn_frame = tk.Frame(popup, bg=self.COLORS['bg_main'], pady=10)
        btn_frame.pack(fill=tk.X)

        close_btn = tk.Button(btn_frame, text="关闭", command=popup.destroy,
                               bg=self.COLORS['danger'], fg="white", font=("Microsoft YaHei", 10),
                               relief=tk.FLAT, padx=25, pady=5, cursor="hand2")
        close_btn.pack(side=tk.RIGHT, padx=(0, 15))
        close_btn.bind("<Enter>", lambda e: close_btn.config(bg="#dc2626"))
        close_btn.bind("<Leave>", lambda e: close_btn.config(bg=self.COLORS['danger']))

    def _bind_scroll_events(self):
        def _on_mousewheel(event):
            if event.widget.winfo_toplevel() is not self.root:
                return
            x1 = self.canvas.winfo_rootx()
            y1 = self.canvas.winfo_rooty()
            x2 = x1 + self.canvas.winfo_width()
            y2 = y1 + self.canvas.winfo_height()
            ex, ey = event.x_root, event.y_root
            if x1 <= ex <= x2 and y1 <= ey <= y2:
                if event.delta > 0:
                    self.canvas.yview_scroll(-1, "units")
                else:
                    self.canvas.yview_scroll(1, "units")
                return "break"
        self.root.bind_all("<MouseWheel>", _on_mousewheel, add="+")

    def _on_frame_configure(self, event):
        # 节流：避免窗口连续缩放时频繁更新滚动区域导致卡顿
        if hasattr(self, '_canvas_scroll_scheduled') and self._canvas_scroll_scheduled:
            return
        self._canvas_scroll_scheduled = True
        self.root.after_idle(self._do_canvas_scroll_update)

    def _do_canvas_scroll_update(self):
        self._canvas_scroll_scheduled = False
        if hasattr(self, 'canvas') and self.canvas.winfo_exists():
            bbox = self.canvas.bbox("all")
            if bbox:
                self.canvas.configure(scrollregion=bbox)

    def _on_canvas_configure(self, event):
        self.canvas.itemconfigure(self._canvas_window_id, width=event.width)

    def _build_groups_ui(self):
        for widget in self.groups_frame.winfo_children():
            widget.destroy()

        self.group_widgets = []

        for group in self.groups:
            installed_count = sum(1 for sw in group.items if sw.status == SoftwareStatus.INSTALLED)
            total_count = len(group.items)
            stat_text = f"{installed_count}/{total_count}"

            ratio = installed_count / total_count if total_count > 0 else 0
            if ratio == 1:
                status_color = self.COLORS['success']
            elif ratio > 0:
                status_color = self.COLORS['warning']
            else:
                status_color = self.COLORS['not_installed']

            group_card = tk.Frame(self.groups_frame, bg=self.COLORS['bg_card'])
            group_card.pack(fill=tk.X, padx=5, pady=(8, 4))

            header_gradient = tk.Frame(group_card, bg=self.COLORS['primary'])
            header_gradient.pack(fill=tk.X, ipady=6)

            name_label = tk.Label(header_gradient, text=f"  {group.name}", bg=self.COLORS['primary'],
                                   fg="white", font=("Microsoft YaHei", 10, "bold"), anchor=tk.W)
            name_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

            stat_label = tk.Label(header_gradient, text=f"{stat_text} ", bg=self.COLORS['primary'],
                                   fg="#e6e6e6", font=("Microsoft YaHei", 9, "bold"))
            stat_label.pack(side=tk.RIGHT, padx=10)

            content_frame = tk.Frame(group_card, bg=self.COLORS['bg_card'], padx=10, pady=8)
            content_frame.pack(fill=tk.X)

            col_header = tk.Frame(content_frame, bg=self.COLORS['bg_card'])
            col_header.pack(fill=tk.X, pady=(0, 6))

            tk.Label(col_header, text="📋 软件名称", width=18, anchor=tk.W,
                     font=("Microsoft YaHei", 9, "bold"), bg=self.COLORS['bg_card'],
                     fg=self.COLORS['text_secondary']).pack(side=tk.LEFT, padx=(0, 8))
            tk.Label(col_header, text="✅ 状态", width=10, anchor=tk.CENTER,
                     font=("Microsoft YaHei", 9, "bold"), bg=self.COLORS['bg_card'],
                     fg=self.COLORS['text_secondary']).pack(side=tk.LEFT, padx=(0, 8))
            tk.Label(col_header, text="📌 版本", width=14, anchor=tk.W,
                     font=("Microsoft YaHei", 9, "bold"), bg=self.COLORS['bg_card'],
                     fg=self.COLORS['text_secondary']).pack(side=tk.LEFT, padx=(0, 8))
            tk.Label(col_header, text="🔗 检测来源", width=20, anchor=tk.W,
                     font=("Microsoft YaHei", 9, "bold"), bg=self.COLORS['bg_card'],
                     fg=self.COLORS['text_secondary']).pack(side=tk.LEFT, padx=(0, 8))
            tk.Label(col_header, text="📁 安装路径", anchor=tk.W,
                     font=("Microsoft YaHei", 9, "bold"), bg=self.COLORS['bg_card'],
                     fg=self.COLORS['text_secondary']).pack(side=tk.LEFT)

            separator = tk.Frame(content_frame, bg=self.COLORS['border'], height=1)
            separator.pack(fill=tk.X, pady=(0, 6))

            self.group_widgets.append({"frame": group_card, "content": content_frame, "group": group, "stat_label": stat_label})

            for software in group.items:
                self._fill_software_item(content_frame, software)

        if not self.groups:
            empty_label = tk.Label(self.groups_frame, text="没有匹配的检测项，请更改搜索条件或筛选状态",
                                    font=("Microsoft YaHei", 11), bg="#fafafa", fg="#94a3b8",
                                    anchor=tk.CENTER, pady=40)
            empty_label.pack(fill=tk.X)

        # 重建后强制刷新 groups_frame 的几何尺寸，触发 canvas 的 scrollregion 更新
        # 确保筛选/搜索后的内容高度能被 canvas 正确计算，避免内容"看不见"
        if hasattr(self, 'groups_frame') and self.groups_frame.winfo_exists():
            self.root.update_idletasks()
            self.groups_frame.event_generate("<Configure>")
            if hasattr(self, 'canvas') and self.canvas.winfo_exists():
                bbox = self.canvas.bbox("all")
                if bbox:
                    self.canvas.configure(scrollregion=bbox)

    def _fill_software_item(self, parent_frame, software: Software):
        item_frame = tk.Frame(parent_frame, bg=self.COLORS['bg_card'])
        item_frame.pack(fill=tk.X, pady=2)

        item_frame.name_label = tk.Label(item_frame, text=software.name, width=18, anchor=tk.W,
                                          bg=self.COLORS['bg_card'], fg=self.COLORS['text_primary'],
                                          font=("Microsoft YaHei", 9))
        item_frame.name_label.pack(side=tk.LEFT, padx=(0, 8))

        status_text = software.status.value
        bg_color = self.COLORS['installed'] if software.status == SoftwareStatus.INSTALLED else self.COLORS['not_installed']
        item_frame.status_label = tk.Label(item_frame, text=status_text, width=10, anchor=tk.CENTER,
                                             fg="white", bg=bg_color, font=("Microsoft YaHei", 8, "bold"))
        item_frame.status_label.pack(side=tk.LEFT, padx=(0, 8))

        version_text = software.version if software.version else "-"
        version_full = software.version if software.version else "-"
        if len(version_text) > 18:
            version_text = version_text[:15] + "..."
        item_frame.version_label = tk.Label(item_frame, text=version_text, width=14, anchor=tk.W,
                                              bg=self.COLORS['bg_card'], fg=self.COLORS['text_primary'],
                                              font=("Microsoft YaHei", 9))
        item_frame.version_label.pack(side=tk.LEFT, padx=(0, 8))
        item_frame.version_label.bind("<Enter>", lambda e, t=version_full: self._tooltip(e, t))
        item_frame.version_label.bind("<Leave>", self._schedule_hide_tooltip)

        source_text = software.source if software.source else "-"
        source_full = software.source if software.source else "-"
        if len(source_text) > 22:
            source_text = source_text[:19] + "..."
        item_frame.source_label = tk.Label(item_frame, text=source_text, width=20, anchor=tk.W,
                                            bg=self.COLORS['bg_card'], fg=self.COLORS['text_secondary'],
                                            font=("Microsoft YaHei", 8))
        item_frame.source_label.pack(side=tk.LEFT, padx=(0, 8))
        item_frame.source_label.bind("<Enter>", lambda e, t=source_full: self._tooltip(e, t))
        item_frame.source_label.bind("<Leave>", self._schedule_hide_tooltip)

        path_text = software.path[:42] + "..." if len(software.path) > 42 else software.path if software.path else "-"
        path_full = software.path if software.path else "-"
        item_frame.path_label = tk.Label(item_frame, text=path_text, anchor=tk.W, bg=self.COLORS['bg_card'],
                                          fg="#667eea", font=("Microsoft YaHei", 8))
        item_frame.path_label.pack(side=tk.LEFT)
        item_frame.path_label.bind("<Enter>", lambda e, t=path_full: self._tooltip(e, t))
        item_frame.path_label.bind("<Leave>", self._schedule_hide_tooltip)

        item_frame.bind("<Button-1>", lambda e, sw=software: self._copy_to_clipboard(sw.name))
        item_frame.bind("<Button-3>", lambda e, sw=software: self._show_context_menu(e, sw))
        item_frame.name_label.bind("<Button-3>", lambda e, sw=software: self._show_context_menu(e, sw))
        item_frame.status_label.bind("<Button-1>", lambda e, sw=software: self._copy_to_clipboard(sw.status.value))
        item_frame.status_label.bind("<Button-3>", lambda e, sw=software: self._show_context_menu(e, sw))
        item_frame.version_label.bind("<Button-1>", lambda e, sw=software: self._copy_to_clipboard(sw.version))
        item_frame.version_label.bind("<Button-3>", lambda e, sw=software: self._show_context_menu(e, sw))
        item_frame.source_label.bind("<Button-1>", lambda e, sw=software: self._copy_to_clipboard(sw.source))
        item_frame.source_label.bind("<Button-3>", lambda e, sw=software: self._show_context_menu(e, sw))
        item_frame.path_label.bind("<Button-1>", lambda e, sw=software: self._copy_to_clipboard(sw.path))
        item_frame.path_label.bind("<Button-3>", lambda e, sw=software: self._show_context_menu(e, sw))

        software.item_frame = item_frame

    def _show_context_menu(self, event, software):
        menu = tk.Menu(self.root, tearoff=0, bg=self.COLORS['bg_card'], fg=self.COLORS['text_primary'],
                       font=("Microsoft YaHei", 9))
        menu.add_command(label="📋 复制名称", command=lambda: self._copy_to_clipboard(software.name))
        menu.add_command(label="📌 复制版本", command=lambda: self._copy_to_clipboard(software.version))
        menu.add_command(label="🔗 复制来源", command=lambda: self._copy_to_clipboard(software.source))
        menu.add_command(label="📁 复制路径", command=lambda: self._copy_to_clipboard(software.path))

        if software.all_versions and len(software.all_versions) > 1:
            all_text = "\n".join([f"{v} | {p} | {s}" for v, p, s in software.all_versions])
        else:
            all_text = f"{software.name} | {software.version} | {software.source} | {software.path}"
        menu.add_command(label="📄 复制全部信息", command=lambda: self._copy_to_clipboard(all_text))

        menu.add_separator()
        menu.add_command(label="📂 打开文件路径", command=lambda: self._open_file_path(software.path))
        menu.add_command(label="🔍 百度搜索", command=lambda: self._search_baidu(software.name))
        menu.post(event.x_root, event.y_root)

    def _tooltip(self, event, text):
        if not text or text == "-":
            return
        if self._tooltip_after_id:
            self.root.after_cancel(self._tooltip_after_id)
            self._tooltip_after_id = None
        if self.tooltip_window:
            try:
                self.tooltip_window.destroy()
            except Exception:
                pass
        x = event.x_root + 10
        y = event.y_root + 10
        self.tooltip_window = tk.Toplevel(self.root)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        self.tooltip_window.attributes("-topmost", True)
        frame = tk.Frame(self.tooltip_window, bg="#1e293b", relief=tk.SOLID, bd=1)
        frame.pack()
        tk.Label(frame, text=text, bg="#1e293b", fg="white",
                 font=("Microsoft YaHei", 9), wraplength=450, justify=tk.LEFT,
                 padx=10, pady=6).pack()
        frame.bind("<Enter>", self._on_tooltip_enter)
        frame.bind("<Leave>", self._hide_tooltip)
        self.tooltip_window.bind("<Enter>", self._on_tooltip_enter)
        self.tooltip_window.bind("<Leave>", self._hide_tooltip)

    def _on_tooltip_enter(self, event=None):
        if self._tooltip_after_id:
            self.root.after_cancel(self._tooltip_after_id)
            self._tooltip_after_id = None

    def _schedule_hide_tooltip(self, event=None):
        if self._tooltip_after_id:
            self.root.after_cancel(self._tooltip_after_id)
        self._tooltip_after_id = self.root.after(300, self._hide_tooltip)

    def _hide_tooltip(self, event=None):
        self._tooltip_after_id = None
        if hasattr(self, 'tooltip_window') and self.tooltip_window:
            try:
                self.tooltip_window.destroy()
            except Exception:
                pass
            self.tooltip_window = None

    def _copy_to_clipboard(self, text):
        if text:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            self.root.update()

    def _copy_log_to_clipboard(self):
        log_content = self.log_text.get("1.0", tk.END) if hasattr(self, 'log_text') else ""
        self._copy_to_clipboard(log_content)
        self.log_message("📋 日志已复制到剪贴板")

    def _export_log_to_file(self):
        try:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            log_dir = os.path.join(os.path.dirname(sys.executable), "logs") if getattr(sys, 'frozen', False) else "logs"

            if not os.path.exists(log_dir):
                os.makedirs(log_dir)

            log_content = self.log_text.get("1.0", tk.END) if hasattr(self, 'log_text') else ""
            log_file = os.path.join(log_dir, f"detection_{timestamp}.log")
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write(f"=== Windows 开发环境检测工具 {APP_VERSION} ===\n")
                f.write(f"检测模式: {self.detection_mode.value}\n")
                f.write(f"检测时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 50 + "\n")
                f.write(log_content)

            if self.error_logs:
                error_file = os.path.join(log_dir, f"errors_{timestamp}.log")
                with open(error_file, 'w', encoding='utf-8') as f:
                    for error in self.error_logs:
                        f.write(f"[{error['time']}] [{error['level']}] {error['message']}\n")

            summary_file = os.path.join(log_dir, f"summary_{timestamp}.txt")
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(f"=== 开发环境检测结果报告 ===\n")
                f.write(f"版本: {APP_VERSION}\n")
                f.write(f"检测模式: {self.detection_mode.value}\n")
                f.write(f"检测时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"检测耗时: {self.stats.get('elapsed', 0):.1f}秒\n")
                f.write("=" * 50 + "\n\n")

                for group in self.full_groups:
                    f.write(f"【{group.name}】\n")
                    for sw in group.items:
                        status = "✓" if sw.status == SoftwareStatus.INSTALLED else "✗"
                        f.write(f"  {status} {sw.name}: {sw.version if sw.version else '未安装'}\n")
                        if sw.path:
                            f.write(f"     路径: {sw.path}\n")
                    f.write("\n")

            messagebox.showinfo("导出成功", f"日志已导出到:\n{log_dir}")
            self.log_message(f"📥 日志已导出到 {log_dir}")
        except Exception as e:
            self._log_error(f"导出日志失败: {str(e)}")
            messagebox.showerror("导出失败", f"导出日志时发生错误: {e}")

    def _log_error(self, message, traceback=None):
        error_entry = {'time': time.strftime('%Y-%m-%d %H:%M:%S'), 'level': 'ERROR', 'message': message, 'traceback': traceback}
        self.error_logs.append(error_entry)
        self.log_message(f"❌ [错误] {message}")

    def _log_warning(self, message):
        error_entry = {'time': time.strftime('%Y-%m-%d %H:%M:%S'), 'level': 'WARNING', 'message': message}
        self.error_logs.append(error_entry)
        self.log_message(f"⚠️ [警告] {message}")

    def _get_cached_result(self, software_name):
        cached = self.detection_cache.get(software_name)
        if not cached:
            return None
        status, version, source, path, timestamp = cached
        if time.time() - timestamp < 3600:
            return (status, version, source, path)
        else:
            del self.detection_cache[software_name]
            return None

    def _cache_result(self, software_name, status, version, source, path):
        self.detection_cache[software_name] = (status, version, source, path, time.time())

    def _clear_cache(self):
        self.detection_cache.clear()
        self.log_message("✅ 检测缓存已清除")
        messagebox.showinfo("清除成功", "检测缓存已清除")

    def _open_file_path(self, file_path):
        if not file_path:
            return
        try:
            if os.path.isfile(file_path):
                dir_path = os.path.dirname(file_path)
            else:
                dir_path = file_path
            subprocess.run(f'explorer "{dir_path}"', shell=True)
        except Exception as e:
            self.log_message(f"打开路径失败: {e}")

    def _search_baidu(self, keyword):
        import webbrowser
        url = f"https://www.baidu.com/s?wd={keyword}"
        webbrowser.open(url)

    def on_search_or_filter_changed(self, *args):
        if not hasattr(self, 'groups_frame') or not self.groups_frame.winfo_exists():
            return
        search_text = self.search_var.get().lower()
        filter_val = self.filter_status.get()

        filtered_groups = []
        for group in self.full_groups:
            filtered_items = []
            for software in group.items:
                match_search = not search_text or search_text in software.name.lower()
                match_filter = filter_val == "全部" or \
                    (filter_val == "已安装" and software.status == SoftwareStatus.INSTALLED) or \
                    (filter_val == "未安装" and software.status == SoftwareStatus.NOT_INSTALLED)

                if match_search and match_filter:
                    filtered_items.append(software)

            if filtered_items:
                filtered_groups.append(SoftwareGroup(group.name, filtered_items))

        self.groups = filtered_groups
        self._build_groups_ui()
        self._update_group_titles()

    def clear_search(self):
        self.search_var.set("")
        self.filter_status.set("全部")
        self.groups = self.full_groups
        self._build_groups_ui()
        self._update_group_titles()

    def _on_mode_changed(self, event=None):
        selected = self.mode_combo.get()
        for mode in DetectionMode:
            if mode.value == selected:
                self.detection_mode = mode
                self.mode_label.config(text=mode.value)
                self.log_message(f"🔄 检测模式已切换为: {mode.value}")
                self._clear_cache()
                # 切换模式后重置筛选状态并刷新列表，避免显示旧模式的筛选结果
                self.search_var.set("")
                self.filter_status.set("全部")
                self.status_combo.set("全部")
                self.groups = self.full_groups
                self._build_groups_ui()
                self._update_group_titles()
                break

    def log_message(self, msg: str):
        timestamp = time.strftime("%H:%M:%S")
        entry = f"[{timestamp}] {msg}"
        self.log_entries.append(entry)
        if len(self.log_entries) > 10000:
            self.log_entries = self.log_entries[-5000:]
        if threading.current_thread() is not threading.main_thread():
            with self._log_lock:
                self._log_pending.append(entry)
                if not self._log_flush_scheduled:
                    self._log_flush_scheduled = True
                    self.root.after(0, self._flush_log)
        else:
            if hasattr(self, 'log_text') and self.log_text.winfo_exists():
                self.log_text.insert(tk.END, f"{entry}\n")
                self.log_text.see(tk.END)

    def _flush_log(self):
        self._log_flush_scheduled = False
        if hasattr(self, 'log_text') and self.log_text.winfo_exists():
            with self._log_lock:
                pending = self._log_pending[:]
                self._log_pending.clear()
            if pending:
                for entry in pending:
                    self.log_text.insert(tk.END, f"{entry}\n")
                self.log_text.see(tk.END)

    def clear_log(self):
        if hasattr(self, 'log_text') and self.log_text.winfo_exists():
            self.log_text.delete(1.0, tk.END)
        self.log_entries.clear()
        if hasattr(self, '_log_pending'):
            self._log_pending.clear()
        self.log_message("🗑️ 日志已清空")

    def set_controls_state(self, enabled: bool):
        state = tk.NORMAL if enabled else tk.DISABLED
        self.search_entry.configure(state=state)
        self.start_btn.configure(state=state)
        self.refresh_btn.configure(state=tk.DISABLED if not enabled else tk.NORMAL)
        self.clear_log_btn.configure(state=state)
        self.export_log_btn.configure(state=state)
        self.copy_log_btn.configure(state=state)
        if enabled:
            self.mode_combo.configure(state=['readonly'])
        else:
            self.mode_combo.configure(state=['disabled'])
        self.is_detecting = not enabled

    def _update_ui_item(self, software: Software):
        if hasattr(software, 'item_frame') and software.item_frame.winfo_exists():
            status_text = software.status.value
            version_text = software.version if software.version else "-"
            version_full = version_text
            if len(version_text) > 18:
                version_text = version_text[:15] + "..."
            source_text = software.source if software.source else "-"
            source_full = source_text
            if len(source_text) > 22:
                source_text = source_text[:19] + "..."
            path_text = software.path[:42] + "..." if len(software.path) > 42 else software.path if software.path else "-"
            path_full = software.path if software.path else "-"

            bg_color = self.COLORS['installed'] if software.status == SoftwareStatus.INSTALLED else self.COLORS['not_installed']

            software.item_frame.status_label.config(text=status_text, bg=bg_color)
            software.item_frame.version_label.config(text=version_text)
            software.item_frame.source_label.config(text=source_text)
            software.item_frame.path_label.config(text=path_text)

            software.item_frame.version_label.unbind("<Enter>")
            software.item_frame.version_label.unbind("<Leave>")
            software.item_frame.version_label.bind("<Enter>", lambda e, t=version_full: self._tooltip(e, t))
            software.item_frame.version_label.bind("<Leave>", self._schedule_hide_tooltip)

            software.item_frame.source_label.unbind("<Enter>")
            software.item_frame.source_label.unbind("<Leave>")
            software.item_frame.source_label.bind("<Enter>", lambda e, t=source_full: self._tooltip(e, t))
            software.item_frame.source_label.bind("<Leave>", self._schedule_hide_tooltip)

            software.item_frame.path_label.unbind("<Enter>")
            software.item_frame.path_label.unbind("<Leave>")
            software.item_frame.path_label.bind("<Enter>", lambda e, t=path_full: self._tooltip(e, t))
            software.item_frame.path_label.bind("<Leave>", self._schedule_hide_tooltip)

    def _update_group_titles(self):
        for group_widget in self.group_widgets:
            group = group_widget["group"]
            installed_count = sum(1 for sw in group.items if sw.status == SoftwareStatus.INSTALLED)
            total_count = len(group.items)
            stat_text = f"{installed_count}/{total_count}"
            group_widget["stat_label"].config(text=stat_text)

    def _update_status_bar(self):
        total = self.stats.get("total", 0)
        installed = self.stats.get("installed", 0)
        not_installed = self.stats.get("not_installed", 0)
        elapsed = self.stats.get("elapsed", 0)

        self.status_label.config(text=f"总计: {total} 项 | 已安装: {installed} 项 | 未安装: {not_installed} 项")
        self.time_label.config(text=f"耗时: {elapsed:.1f}秒")
        self.mode_label.config(text=self.detection_mode.value)

    def start_detection(self):
        if self.is_detecting:
            return

        self._detect_start_time = time.time()
        self.log_message("=" * 50)
        self.log_message(f"🔍 开始检测... 模式: {self.detection_mode.value}")
        self.set_controls_state(False)

        for group in self.full_groups:
            for software in group.items:
                software.status = SoftwareStatus.NOT_INSTALLED
                software.version = ""
                software.source = ""
                software.path = ""
                software.all_versions = []

        detection_thread = threading.Thread(target=self._detection_worker, daemon=True)
        detection_thread.start()

    def _detection_worker(self):
        total = sum(len(group.items) for group in self.full_groups)
        installed = 0
        cache_hits = 0
        current = 0

        for group in self.full_groups:
            self.root.after(0, self.log_message, f"\n📂 检测分组: {group.name}")
            self.root.after(0, self.log_message, "-" * 30)

            for software in group.items:
                current += 1
                self.root.after(0, self.log_message, f"🔎 检测 {software.name}...")

                cached_result = self._get_cached_result(software.name)
                if cached_result:
                    status, version, source, path = cached_result
                    all_versions = [(version, path, source)]
                    cache_hits += 1
                    self.root.after(0, self.log_message, f"  ⚡ 使用缓存 - {version}")
                else:
                    try:
                        status, version, source, path, all_versions = Detector.detect_software(software, self.detection_mode)
                        self._cache_result(software.name, status, version, source, path)
                    except Exception as e:
                        self.root.after(0, self._log_error, f"检测 {software.name} 时发生错误: {str(e)}")
                        status = SoftwareStatus.NOT_INSTALLED
                        version = ""
                        source = ""
                        path = ""
                        all_versions = []

                software.status = status
                software.version = version
                software.source = source
                software.path = path
                software.all_versions = all_versions

                if status == SoftwareStatus.INSTALLED:
                    installed += 1
                    ver_count = len(all_versions)
                    extra_note = f" [+{ver_count - 1}个其他版本]" if ver_count > 1 else ""
                    msg = f"  ✅ {software.name} 已安装{extra_note}"
                    if version:
                        msg += f" - {version}"
                    if source:
                        msg += f" [{source}]"
                    if path:
                        msg += f" (路径: {path})"
                    if ver_count > 1:
                        for v, p, s in all_versions[1:]:
                            short_p = p if len(p) < 50 else "..." + p[-47:]
                            msg += f"\n    另: {v} @ {short_p}"
                    self.root.after(0, self.log_message, msg)
                else:
                    self.root.after(0, self.log_message, f"  ❌ {software.name} 未安装")

                self.root.after(0, self._update_ui_item, software)

        elapsed = time.time() - self._detect_start_time
        self.stats = {
            "total": total,
            "installed": installed,
            "not_installed": total - installed,
            "elapsed": elapsed,
            "cache_hits": cache_hits
        }

        self.root.after(0, self.log_message, "\n" + "=" * 50)
        self.root.after(0, self.log_message, f"🎉 全部检测完成! 模式: {self.detection_mode.value} | 耗时: {elapsed:.1f}秒")
        if cache_hits > 0:
            self.root.after(0, self.log_message, f"⚡ 缓存命中: {cache_hits} 项")

        self.root.after(0, self._update_status_bar)
        self.root.after(0, self.set_controls_state, True)
        self.root.after(0, self.on_search_or_filter_changed)

def main():
    root = tk.Tk()
    app = DevEnvDetectorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
