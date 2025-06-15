import os
import csv
import configparser
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText
import subprocess
import time

class ADBUninstallerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ADB 软件卸载工具 v2.3")  # 更新版本号
        
        # 变量
        self.file_path = ""
        self.packages = []
        self.use_root = tk.BooleanVar(value=False)
        self.show_confirmation = tk.BooleanVar(value=True)
        self.log_content = tk.StringVar()
        
        # 创建界面
        self.create_widgets()
        
    def create_widgets(self):
        # 顶部按钮区域
        top_frame = ttk.Frame(self.root)
        top_frame.pack(padx=10, pady=5, fill="x")
        
        test_btn = ttk.Button(top_frame, text="测试ADB连接", command=self.test_adb_connection)
        test_btn.pack(side="left", padx=5)
        
        test_root_btn = ttk.Button(top_frame, text="测试Root权限", command=self.test_root_permission)
        test_root_btn.pack(side="left", padx=5)
        
        # 文件选择部分
        file_frame = ttk.LabelFrame(self.root, text="软件列表文件")
        file_frame.pack(padx=10, pady=5, fill="x")
        
        self.file_entry = ttk.Entry(file_frame)
        self.file_entry.pack(side="left", padx=5, pady=5, expand=True, fill="x")
        
        browse_btn = ttk.Button(file_frame, text="浏览...", command=self.browse_file)
        browse_btn.pack(side="left", padx=5, pady=5)
        
        # 选项部分
        option_frame = ttk.LabelFrame(self.root, text="选项")
        option_frame.pack(padx=10, pady=5, fill="x")
        
        ttk.Checkbutton(option_frame, text="使用 Root 权限", variable=self.use_root).pack(padx=5, pady=2, anchor="w")
        ttk.Checkbutton(option_frame, text="卸载前确认", variable=self.show_confirmation).pack(padx=5, pady=2, anchor="w")
        
        # 软件列表显示
        list_frame = ttk.LabelFrame(self.root, text="待卸载软件列表")
        list_frame.pack(padx=10, pady=5, expand=True, fill="both")
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.tree = ttk.Treeview(list_frame, columns=("package", "note"), show="headings",
                                yscrollcommand=scrollbar.set)
        self.tree.heading("package", text="包名")
        self.tree.heading("note", text="备注")
        self.tree.column("package", width=200)
        self.tree.column("note", width=300)
        self.tree.pack(expand=True, fill="both", padx=5, pady=5)
        
        scrollbar.config(command=self.tree.yview)
        
        # 操作按钮
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(padx=10, pady=5, fill="x")
        
        ttk.Button(btn_frame, text="加载列表", command=self.load_list).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="开始卸载", command=self.uninstall_packages).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="添加项目", command=self.add_item).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="删除选中", command=self.delete_selected).pack(side="left", padx=5)
        
        # 新增排序按钮
        sort_btn = ttk.Button(btn_frame, text="排序列表", command=self.sort_packages)
        sort_btn.pack(side="left", padx=5)
        
        # 保存按钮放在右侧
        save_btn = ttk.Button(btn_frame, text="保存列表", command=self.save_list)
        save_btn.pack(side="right", padx=5)
        
        # 进度条
        self.progress = ttk.Progressbar(self.root, orient="horizontal", length=100, mode="determinate")
        self.progress.pack(padx=10, pady=5, fill="x")
        
        # 日志区域
        log_frame = ttk.LabelFrame(self.root, text="操作日志")
        log_frame.pack(padx=10, pady=5, expand=True, fill="both")
        
        self.log_text = ScrolledText(log_frame, wrap=tk.WORD, height=10)
        self.log_text.pack(expand=True, fill="both", padx=5, pady=5)
        
        # 右键菜单
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="复制", command=self.copy_log)
        self.log_text.bind("<Button-3>", self.show_context_menu)
        
        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        ttk.Label(self.root, textvariable=self.status_var, relief="sunken").pack(padx=10, pady=5, fill="x")
    
    def show_context_menu(self, event):
        self.context_menu.tk_popup(event.x_root, event.y_root)
    
    def copy_log(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.log_text.get("1.0", tk.END))
    
    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.status_var.set(message)
        self.root.update()
    
    def test_adb_connection(self):
        try:
            self.log("正在测试ADB连接...")
            # 使用 subprocess 获取更可靠的输出
            result = subprocess.run(['adb', 'devices'], capture_output=True, text=True, timeout=10)
            output = result.stdout
            
            if "device" in output:
                device_list = [line for line in output.split('\n') if "device" in line and "List" not in line]
                if device_list:
                    devices = "\n".join(device_list)
                    self.log(f"ADB设备已连接:\n{devices}")
                    messagebox.showinfo("ADB连接测试", f"设备已连接:\n{devices}")
                else:
                    self.log("没有检测到设备")
                    messagebox.showerror("ADB连接测试", "没有检测到设备")
            else:
                self.log("ADB连接失败，请检查ADB服务")
                messagebox.showerror("ADB连接测试", "ADB连接失败，请检查ADB服务")
        except Exception as e:
            self.log(f"执行ADB命令出错: {str(e)}")
            messagebox.showerror("错误", f"执行ADB命令出错: {str(e)}")
    
    def test_root_permission(self):
        """改进的Root权限测试方法，使用多种检测方式"""
        try:
            self.log("正在测试Root权限...")
            
            # 方法1: 使用 su -c id 命令测试
            try:
                result = subprocess.run(
                    ['adb', 'shell', 'su', '-c', 'id'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if 'uid=0(root)' in result.stdout:
                    self.log("设备已获取Root权限 (通过su命令)")
                    messagebox.showinfo("Root测试", "设备已获取Root权限")
                    return
            except Exception as e:
                self.log(f"su命令测试失败: {str(e)}")
            
            # 方法2: 检查 /system/bin/su 文件是否存在
            try:
                result = subprocess.run(
                    ['adb', 'shell', 'test', '-e', '/system/bin/su'],
                    capture_output=True,
                    timeout=5
                )
                if result.returncode == 0:
                    self.log("设备已获取Root权限 (检测到su文件)")
                    messagebox.showinfo("Root测试", "设备已获取Root权限")
                    return
            except Exception as e:
                self.log(f"su文件检测失败: {str(e)}")
            
            # 方法3: 检查Magisk/MagiskSU
            try:
                result = subprocess.run(
                    ['adb', 'shell', 'getprop', 'ro.build.tags'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if 'test-keys' in result.stdout.lower():
                    self.log("设备已获取Root权限 (检测到test-keys)")
                    messagebox.showinfo("Root测试", "设备已获取Root权限")
                    return
            except Exception as e:
                self.log(f"系统属性检测失败: {str(e)}")
            
            # 方法4: 尝试执行需要root权限的命令
            try:
                result = subprocess.run(
                    ['adb', 'shell', 'su', '-c', 'ls', '/data'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    self.log("设备已获取Root权限 (成功访问/data目录)")
                    messagebox.showinfo("Root测试", "设备已获取Root权限")
                    return
            except Exception as e:
                self.log(f"命令执行测试失败: {str(e)}")
            
            # 如果所有方法都失败
            self.log("无法确认设备Root状态，请手动检查")
            messagebox.showwarning("Root测试", "无法确认设备Root状态，请手动检查")
            
        except Exception as e:
            self.log(f"Root测试失败: {str(e)}")
            messagebox.showerror("错误", f"Root测试失败: {str(e)}")
    
    def delete_selected(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("警告", "请先选择要删除的项目")
            return
        
        for item in selected_items:
            self.tree.delete(item)
        self.log(f"已删除 {len(selected_items)} 个项目")
    
    def browse_file(self):
        file_types = [("支持的文件格式", "*.csv;*.ini"), ("CSV 文件", "*.csv"), ("INI 文件", "*.ini"), ("所有文件", "*.*")]
        self.file_path = filedialog.askopenfilename(filetypes=file_types)
        if self.file_path:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, self.file_path)
            self.log(f"已选择文件: {os.path.basename(self.file_path)}")
    
    def load_list(self):
        self.packages = []
        self.tree.delete(*self.tree.get_children())
        
        if not self.file_path:
            messagebox.showerror("错误", "请先选择文件")
            return
        
        try:
            self.log(f"正在加载文件: {self.file_path}")
            
            if self.file_path.endswith('.csv'):
                with open(self.file_path, mode='r', encoding='utf-8') as file:
                    reader = csv.reader(file)
                    for row in reader:
                        if len(row) >= 1:
                            package = row[0]
                            note = row[1] if len(row) > 1 else ""
                            self.packages.append((package, note))
                            self.tree.insert("", "end", values=(package, note))
            elif self.file_path.endswith('.ini'):
                config = configparser.ConfigParser()
                with open(self.file_path, 'r', encoding='utf-8') as file:
                    config.read_file(file)
                if 'Packages' in config:
                    for package, note in config['Packages'].items():
                        self.packages.append((package, note))
                        self.tree.insert("", "end", values=(package, note))
            else:
                messagebox.showerror("错误", "不支持的文件格式")
                self.log("错误: 不支持的文件格式")
                return
            
            count = len(self.tree.get_children())
            self.log(f"已加载 {count} 个软件包")
        except Exception as e:
            messagebox.showerror("错误", f"加载文件失败: {str(e)}")
            self.log(f"加载文件失败: {str(e)}")
    
    def save_list(self):
        if not self.file_path:
            messagebox.showerror("错误", "请先选择文件")
            return
        
        try:
            self.log(f"正在保存文件: {self.file_path}")
            
            if self.file_path.endswith('.csv'):
                with open(self.file_path, mode='w', encoding='utf-8', newline='') as file:
                    writer = csv.writer(file)
                    for child in self.tree.get_children():
                        values = self.tree.item(child)['values']
                        writer.writerow(values)
            elif self.file_path.endswith('.ini'):
                config = configparser.ConfigParser()
                config.optionxform = str
                config['Packages'] = {}
                for child in self.tree.get_children():
                    package, note = self.tree.item(child)['values']
                    config['Packages'][package] = note
                with open(self.file_path, 'w', encoding='utf-8') as file:
                    config.write(file)
            
            count = len(self.tree.get_children())
            messagebox.showinfo("成功", f"列表已保存，共 {count} 个项目")
            self.log(f"列表已保存 ({count} 个项目)")
        except Exception as e:
            messagebox.showerror("错误", f"保存文件失败: {str(e)}")
            self.log(f"保存文件失败: {str(e)}")
    
    def add_item(self):
        def save_item():
            package = package_entry.get().strip()
            note = note_entry.get().strip()
            if package:
                self.tree.insert("", "end", values=(package, note))
                add_window.destroy()
                self.log(f"已添加: {package}")
            else:
                messagebox.showwarning("警告", "包名不能为空")
        
        add_window = tk.Toplevel(self.root)
        add_window.title("添加软件包")
        add_window.geometry("400x150")  # 设置更宽的窗口尺寸
        
        # 计算对话框位置使其居中
        main_x = self.root.winfo_x()
        main_y = self.root.winfo_y()
        main_width = self.root.winfo_width()
        main_height = self.root.winfo_height()
        
        dialog_width = 400
        dialog_height = 150
        
        pos_x = main_x + (main_width - dialog_width) // 2
        pos_y = main_y + (main_height - dialog_height) // 2
        
        add_window.geometry(f"{dialog_width}x{dialog_height}+{pos_x}+{pos_y}")
        
        # 使用网格布局
        ttk.Label(add_window, text="包名:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        package_entry = ttk.Entry(add_window, width=40)  # 设置更宽的输入框
        package_entry.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        
        ttk.Label(add_window, text="备注:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        note_entry = ttk.Entry(add_window, width=40)  # 设置更宽的输入框
        note_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        btn_frame = ttk.Frame(add_window)
        btn_frame.grid(row=2, column=1, padx=5, pady=10, sticky="e")
        
        ttk.Button(btn_frame, text="保存", command=save_item).pack(side="right", padx=5)
        
        # 设置列权重使输入框可以扩展
        add_window.columnconfigure(1, weight=1)
        
        # 设置焦点
        package_entry.focus_set()
    
    def sort_packages(self):
        """按包名英文字母顺序排序列表"""
        if not self.tree.get_children():
            messagebox.showinfo("提示", "列表为空，无需排序")
            return
        
        # 收集所有项目
        items = []
        for child in self.tree.get_children():
            package, note = self.tree.item(child)['values']
            items.append((package, note))
        
        # 按包名排序
        sorted_items = sorted(items, key=lambda x: x[0].lower())
        
        # 清空当前列表
        self.tree.delete(*self.tree.get_children())
        
        # 重新插入排序后的项目
        for package, note in sorted_items:
            self.tree.insert("", "end", values=(package, note))
        
        self.log("列表已按包名英文字母顺序排序")
        messagebox.showinfo("排序完成", "列表已按包名英文字母顺序排序\n\n请点击'保存列表'按钮保存排序结果")
    
    def uninstall_packages(self):
        if len(self.tree.get_children()) == 0:
            messagebox.showerror("错误", "没有可卸载的软件包")
            return
        
        # 全局确认：只有当show_confirmation为True时才显示全局确认对话框
        if self.show_confirmation.get():
            count = len(self.tree.get_children())
            if not messagebox.askyesno("全局确认", f"确定要卸载 {count} 个软件包吗？"):
                self.log("用户取消卸载操作")
                return
        else:
            self.log("跳过全局确认，直接开始卸载...")
            time.sleep(1)
        
        # 根据root选项决定命令
        if self.use_root.get():
            uninstall_cmd = "adb shell pm uninstall"
        else:
            uninstall_cmd = "adb shell pm uninstall --user 0"
        
        success_count = 0
        fail_count = 0
        skip_count = 0
        total = len(self.tree.get_children())
        
        self.progress["maximum"] = total
        self.progress["value"] = 0
        
        # 获取所有待卸载的项目
        children = self.tree.get_children()
        
        for i, child in enumerate(children):
            package, note = self.tree.item(child)['values']
            
            # 单个确认：如果全局确认已通过且单个确认选项开启
            if self.show_confirmation.get():
                # 使用更明确的对话框选项
                response = messagebox.askyesnocancel(
                    "确认卸载", 
                    f"是否要卸载软件包: {package}?\n\n备注: {note if note else '无'}",
                    icon=messagebox.QUESTION
                )
                
                if response is None:  # 用户点击了"取消"
                    self.log("用户终止卸载操作")
                    break
                elif not response:    # 用户点击了"否"
                    skip_count += 1
                    self.log(f"跳过卸载: {package}")
                    self.progress["value"] = i + 1
                    self.root.update()
                    continue
            
            # 构建卸载命令
            if self.use_root.get():
                # 使用 su -c 确保以 root 权限执行
                command = f"adb shell su -c 'pm uninstall {package}'"
            else:
                command = f"{uninstall_cmd} {package}"
            
            self.log(f"正在卸载 {package}...")
            self.progress["value"] = i + 1
            self.root.update()
            
            try:
                # 使用 subprocess 执行命令
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=15  # 设置超时时间
                )
                
                # 检查命令输出
                output = result.stdout + result.stderr
                
                if "Success" in output:
                    success_count += 1
                    self.tree.item(child, tags=('success',))
                    self.log(f"成功卸载: {package}")
                elif "not installed" in output:
                    fail_count += 1
                    self.tree.item(child, tags=('warning',))
                    self.log(f"软件未安装: {package}")
                else:
                    fail_count += 1
                    self.tree.item(child, tags=('fail',))
                    self.log(f"卸载失败: {package} - {output.strip()}")
            except subprocess.TimeoutExpired:
                fail_count += 1
                self.tree.item(child, tags=('error',))
                self.log(f"卸载超时: {package} - 命令执行时间过长")
            except Exception as e:
                fail_count += 1
                self.tree.item(child, tags=('error',))
                self.log(f"卸载出错: {package} - {str(e)}")
        
        # 显示最终结果
        result_message = f"卸载完成:\n\n成功: {success_count} 个\n失败: {fail_count} 个\n跳过: {skip_count} 个"
        self.log(result_message.replace("\n", " "))
        messagebox.showinfo("卸载结果", result_message)

if __name__ == "__main__":
    root = tk.Tk()
    try:
        root.iconbitmap('adb_uninstaller.ico')
    except:
        pass
    
    root.geometry("900x700+300+100")
    
    style = ttk.Style()
    style.configure('success.Treeview', foreground='green')
    style.configure('fail.Treeview', foreground='red')
    style.configure('error.Treeview', foreground='orange')
    style.configure('warning.Treeview', foreground='blue')
    
    app = ADBUninstallerApp(root)
    root.mainloop()