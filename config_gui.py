#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置界面，用于管理回复规则和信息源设置
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import logging
from keyword_matcher import MatchType
from info_fetcher import InfoSourceType

# 配置日志
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ConfigGUI:
    """配置界面类"""
    
    def __init__(self, master, auto_reply_manager=None):
        """初始化配置界面
        
        Args:
            master: 主窗口
            auto_reply_manager: 自动回复管理器实例（可选）
        """
        self.master = master
        self.auto_reply_manager = auto_reply_manager
        
        # 设置窗口标题和大小
        self.master.title("微信自动回复系统 - 配置界面")
        self.master.geometry("800x600")
        self.master.resizable(True, True)
        
        # 配置文件路径
        self.config_file = "auto_reply_config.json"
        
        # 初始化界面
        self._create_widgets()
        
        logger.info("配置界面初始化完成")
    
    def _create_widgets(self):
        """创建界面组件"""
        # 创建主标签页
        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 回复规则标签页
        self.rule_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.rule_frame, text="回复规则管理")
        self._create_rule_tab()
        
        # 信息源标签页
        self.source_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.source_frame, text="信息源管理")
        self._create_source_tab()
        
        # 系统状态标签页
        self.status_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.status_frame, text="系统状态")
        self._create_status_tab()
        
        # 底部按钮栏
        self.bottom_frame = ttk.Frame(self.master)
        self.bottom_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # 保存配置按钮
        self.save_btn = ttk.Button(self.bottom_frame, text="保存配置", command=self.save_config)
        self.save_btn.pack(side=tk.LEFT, padx=5)
        
        # 加载配置按钮
        self.load_btn = ttk.Button(self.bottom_frame, text="加载配置", command=self.load_config)
        self.load_btn.pack(side=tk.LEFT, padx=5)
        
        # 退出按钮
        self.exit_btn = ttk.Button(self.bottom_frame, text="退出", command=self.master.quit)
        self.exit_btn.pack(side=tk.RIGHT, padx=5)
    
    def _create_rule_tab(self):
        """创建回复规则标签页"""
        # 规则列表
        self.rule_list_frame = ttk.Frame(self.rule_frame)
        self.rule_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 规则列表树状视图
        self.rule_tree = ttk.Treeview(self.rule_list_frame, columns=("keyword", "response", "match_type", "priority"), show="headings")
        self.rule_tree.heading("keyword", text="关键词")
        self.rule_tree.heading("response", text="回复内容")
        self.rule_tree.heading("match_type", text="匹配类型")
        self.rule_tree.heading("priority", text="优先级")
        
        # 设置列宽
        self.rule_tree.column("keyword", width=150)
        self.rule_tree.column("response", width=300)
        self.rule_tree.column("match_type", width=100)
        self.rule_tree.column("priority", width=80)
        
        # 添加滚动条
        rule_scrollbar = ttk.Scrollbar(self.rule_list_frame, orient=tk.VERTICAL, command=self.rule_tree.yview)
        self.rule_tree.configure(yscrollcommand=rule_scrollbar.set)
        
        self.rule_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        rule_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 规则操作按钮
        self.rule_btn_frame = ttk.Frame(self.rule_frame)
        self.rule_btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.add_rule_btn = ttk.Button(self.rule_btn_frame, text="添加规则", command=self.add_rule)
        self.add_rule_btn.pack(side=tk.LEFT, padx=5)
        
        self.edit_rule_btn = ttk.Button(self.rule_btn_frame, text="编辑规则", command=self.edit_rule)
        self.edit_rule_btn.pack(side=tk.LEFT, padx=5)
        
        self.delete_rule_btn = ttk.Button(self.rule_btn_frame, text="删除规则", command=self.delete_rule)
        self.delete_rule_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_rules_btn = ttk.Button(self.rule_btn_frame, text="清空规则", command=self.clear_rules)
        self.clear_rules_btn.pack(side=tk.LEFT, padx=5)
    
    def _create_source_tab(self):
        """创建信息源标签页"""
        # 信息源列表
        self.source_list_frame = ttk.Frame(self.source_frame)
        self.source_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 信息源列表树状视图
        self.source_tree = ttk.Treeview(self.source_list_frame, columns=("name", "type", "url", "interval"), show="headings")
        self.source_tree.heading("name", text="名称")
        self.source_tree.heading("type", text="类型")
        self.source_tree.heading("url", text="URL")
        self.source_tree.heading("interval", text="更新间隔(秒)")
        
        # 设置列宽
        self.source_tree.column("name", width=120)
        self.source_tree.column("type", width=100)
        self.source_tree.column("url", width=350)
        self.source_tree.column("interval", width=120)
        
        # 添加滚动条
        source_scrollbar = ttk.Scrollbar(self.source_list_frame, orient=tk.VERTICAL, command=self.source_tree.yview)
        self.source_tree.configure(yscrollcommand=source_scrollbar.set)
        
        self.source_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        source_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 信息源操作按钮
        self.source_btn_frame = ttk.Frame(self.source_frame)
        self.source_btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.add_source_btn = ttk.Button(self.source_btn_frame, text="添加信息源", command=self.add_source)
        self.add_source_btn.pack(side=tk.LEFT, padx=5)
        
        self.edit_source_btn = ttk.Button(self.source_btn_frame, text="编辑信息源", command=self.edit_source)
        self.edit_source_btn.pack(side=tk.LEFT, padx=5)
        
        self.delete_source_btn = ttk.Button(self.source_btn_frame, text="删除信息源", command=self.delete_source)
        self.delete_source_btn.pack(side=tk.LEFT, padx=5)
    
    def _create_status_tab(self):
        """创建系统状态标签页"""
        self.status_text = tk.Text(self.status_frame, wrap=tk.WORD)
        self.status_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.status_text.config(state=tk.DISABLED)
        
        # 刷新状态按钮
        self.refresh_status_btn = ttk.Button(self.status_frame, text="刷新状态", command=self.refresh_status)
        self.refresh_status_btn.pack(padx=5, pady=5)
        
        # 初始刷新状态
        self.refresh_status()
    
    def add_rule(self):
        """添加回复规则"""
        # 创建添加规则对话框
        dialog = RuleDialog(self.master, title="添加回复规则")
        if dialog.result:
            # 将规则添加到列表
            self.rule_tree.insert("", tk.END, values=dialog.result)
            # 如果有自动回复管理器实例，添加到管理器
            if self.auto_reply_manager:
                keyword, response, match_type, priority = dialog.result
                self.auto_reply_manager.add_reply_rule(keyword, response, match_type, int(priority))
    
    def edit_rule(self):
        """编辑回复规则"""
        # 获取选中的规则
        selected_items = self.rule_tree.selection()
        if not selected_items:
            messagebox.showwarning("警告", "请先选择要编辑的规则")
            return
        
        item = selected_items[0]
        values = self.rule_tree.item(item, "values")
        
        # 创建编辑规则对话框
        dialog = RuleDialog(self.master, title="编辑回复规则", initial_values=values)
        if dialog.result:
            # 更新规则列表
            self.rule_tree.item(item, values=dialog.result)
            # 如果有自动回复管理器实例，需要先清除所有规则并重新添加
            if self.auto_reply_manager:
                self._update_rules_in_manager()
    
    def delete_rule(self):
        """删除回复规则"""
        # 获取选中的规则
        selected_items = self.rule_tree.selection()
        if not selected_items:
            messagebox.showwarning("警告", "请先选择要删除的规则")
            return
        
        # 确认删除
        if messagebox.askyesno("确认", "确定要删除选中的规则吗？"):
            for item in selected_items:
                self.rule_tree.delete(item)
            # 如果有自动回复管理器实例，需要先清除所有规则并重新添加
            if self.auto_reply_manager:
                self._update_rules_in_manager()
    
    def clear_rules(self):
        """清空所有回复规则"""
        # 确认清空
        if messagebox.askyesno("确认", "确定要清空所有规则吗？"):
            # 清空规则列表
            for item in self.rule_tree.get_children():
                self.rule_tree.delete(item)
            # 如果有自动回复管理器实例，清除所有规则
            if self.auto_reply_manager:
                self.auto_reply_manager.keyword_matcher.clear_rules()
    
    def add_source(self):
        """添加信息源"""
        # 创建添加信息源对话框
        dialog = SourceDialog(self.master, title="添加信息源")
        if dialog.result:
            # 将信息源添加到列表
            self.source_tree.insert("", tk.END, values=dialog.result)
            # 如果有自动回复管理器实例，添加到管理器
            if self.auto_reply_manager:
                name, source_type, url, interval = dialog.result
                # 这里简化处理，实际使用时需要更复杂的配置
                source_config = {
                    "type": source_type,
                    "url": url
                }
                self.auto_reply_manager.add_info_source(name, source_config, int(interval))
    
    def edit_source(self):
        """编辑信息源"""
        # 获取选中的信息源
        selected_items = self.source_tree.selection()
        if not selected_items:
            messagebox.showwarning("警告", "请先选择要编辑的信息源")
            return
        
        item = selected_items[0]
        values = self.rule_tree.item(item, "values")
        
        # 创建编辑信息源对话框
        dialog = SourceDialog(self.master, title="编辑信息源", initial_values=values)
        if dialog.result:
            # 更新信息源列表
            self.source_tree.item(item, values=dialog.result)
            # 注意：由于信息源更新比较复杂，这里暂时不更新到自动回复管理器
            messagebox.showinfo("提示", "信息源已更新到配置，但需要重启程序才能生效")
    
    def delete_source(self):
        """删除信息源"""
        # 获取选中的信息源
        selected_items = self.source_tree.selection()
        if not selected_items:
            messagebox.showwarning("警告", "请先选择要删除的信息源")
            return
        
        # 确认删除
        if messagebox.askyesno("确认", "确定要删除选中的信息源吗？"):
            for item in selected_items:
                self.source_tree.delete(item)
            # 注意：由于信息源更新比较复杂，这里暂时不更新到自动回复管理器
            messagebox.showinfo("提示", "信息源已从配置中删除，但需要重启程序才能生效")
    
    def save_config(self):
        """保存配置"""
        config = {
            "rules": [],
            "sources": []
        }
        
        # 保存回复规则
        for item in self.rule_tree.get_children():
            values = self.rule_tree.item(item, "values")
            config["rules"].append({
                "keyword": values[0],
                "response": values[1],
                "match_type": values[2],
                "priority": int(values[3])
            })
        
        # 保存信息源
        for item in self.source_tree.get_children():
            values = self.source_tree.item(item, "values")
            config["sources"].append({
                "name": values[0],
                "type": values[1],
                "url": values[2],
                "interval": int(values[3])
            })
        
        # 写入配置文件
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("成功", "配置已保存")
            logger.info("配置已保存到文件")
        except Exception as e:
            messagebox.showerror("错误", f"保存配置失败: {e}")
            logger.error(f"保存配置失败: {e}")
    
    def load_config(self):
        """加载配置"""
        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                config = json.load(f)
            
            # 清空现有规则
            for item in self.rule_tree.get_children():
                self.rule_tree.delete(item)
            
            # 加载回复规则
            for rule in config.get("rules", []):
                self.rule_tree.insert("", tk.END, values=(
                    rule["keyword"],
                    rule["response"],
                    rule["match_type"],
                    rule["priority"]
                ))
            
            # 清空现有信息源
            for item in self.source_tree.get_children():
                self.source_tree.delete(item)
            
            # 加载信息源
            for source in config.get("sources", []):
                self.source_tree.insert("", tk.END, values=(
                    source["name"],
                    source["type"],
                    source["url"],
                    source["interval"]
                ))
            
            # 更新自动回复管理器
            if self.auto_reply_manager:
                self._update_rules_in_manager()
                # 信息源更新比较复杂，需要重启程序才能生效
            
            messagebox.showinfo("成功", "配置已加载")
            logger.info("配置已从文件加载")
        except FileNotFoundError:
            messagebox.showwarning("警告", "配置文件不存在")
        except Exception as e:
            messagebox.showerror("错误", f"加载配置失败: {e}")
            logger.error(f"加载配置失败: {e}")
    
    def refresh_status(self):
        """刷新系统状态"""
        self.status_text.config(state=tk.NORMAL)
        self.status_text.delete(1.0, tk.END)
        
        if self.auto_reply_manager:
            status = self.auto_reply_manager.get_system_status()
            self.status_text.insert(tk.END, "=== 系统状态 ===\n")
            self.status_text.insert(tk.END, f"关键词规则数量: {status['keyword_rule_count']}\n")
            self.status_text.insert(tk.END, f"活跃对话数量: {status['active_conversation_count']}\n")
            self.status_text.insert(tk.END, f"信息源数量: {status['info_source_count']}\n")
            self.status_text.insert(tk.END, "\n=== 缓存信息 ===\n")
            for key, info in status['cache_info']['items'].items():
                self.status_text.insert(tk.END, f"{key}: 过期时间 {info['expire_time']}秒, 已缓存 {info['elapsed_seconds']}秒\n")
        else:
            self.status_text.insert(tk.END, "自动回复管理器未连接，无法获取实时状态\n")
            self.status_text.insert(tk.END, "请先启动主程序\n")
        
        self.status_text.config(state=tk.DISABLED)
    
    def _update_rules_in_manager(self):
        """更新自动回复管理器中的规则"""
        # 清除现有规则
        self.auto_reply_manager.keyword_matcher.clear_rules()
        
        # 添加所有规则
        for item in self.rule_tree.get_children():
            values = self.rule_tree.item(item, "values")
            self.auto_reply_manager.add_reply_rule(
                values[0], values[1], values[2], int(values[3])
            )

class RuleDialog(simpledialog.Dialog):
    """回复规则对话框"""
    
    def __init__(self, parent, title=None, initial_values=None):
        """初始化规则对话框
        
        Args:
            parent: 父窗口
            title: 对话框标题
            initial_values: 初始值
        """
        self.initial_values = initial_values
        self.result = None
        super().__init__(parent, title)
    
    def body(self, master):
        """创建对话框主体"""
        # 关键词
        ttk.Label(master, text="关键词:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.keyword_entry = ttk.Entry(master, width=50)
        self.keyword_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # 回复内容
        ttk.Label(master, text="回复内容:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.NW)
        self.response_text = tk.Text(master, width=50, height=5)
        self.response_text.grid(row=1, column=1, padx=5, pady=5)
        
        # 匹配类型
        ttk.Label(master, text="匹配类型:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.match_type_var = tk.StringVar()
        self.match_type_combo = ttk.Combobox(master, textvariable=self.match_type_var, values=[MatchType.EXACT, MatchType.FUZZY, MatchType.REGEX], state="readonly")
        self.match_type_combo.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        self.match_type_combo.current(0)
        
        # 优先级
        ttk.Label(master, text="优先级:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.priority_var = tk.StringVar()
        self.priority_entry = ttk.Entry(master, textvariable=self.priority_var, width=10)
        self.priority_entry.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
        self.priority_var.set("0")
        
        # 填充初始值
        if self.initial_values:
            self.keyword_entry.insert(0, self.initial_values[0])
            self.response_text.insert(1.0, self.initial_values[1])
            self.match_type_var.set(self.initial_values[2])
            self.priority_var.set(self.initial_values[3])
        
        return self.keyword_entry  # 返回第一个焦点控件
    
    def apply(self):
        """应用对话框结果"""
        keyword = self.keyword_entry.get().strip()
        response = self.response_text.get(1.0, tk.END).strip()
        match_type = self.match_type_var.get()
        priority = self.priority_var.get().strip()
        
        # 验证输入
        if not keyword:
            messagebox.showwarning("警告", "关键词不能为空")
            return
        
        if not response:
            messagebox.showwarning("警告", "回复内容不能为空")
            return
        
        try:
            priority = int(priority)
        except ValueError:
            messagebox.showwarning("警告", "优先级必须是整数")
            return
        
        self.result = (keyword, response, match_type, priority)

class SourceDialog(simpledialog.Dialog):
    """信息源对话框"""
    
    def __init__(self, parent, title=None, initial_values=None):
        """初始化信息源对话框
        
        Args:
            parent: 父窗口
            title: 对话框标题
            initial_values: 初始值
        """
        self.initial_values = initial_values
        self.result = None
        super().__init__(parent, title)
    
    def body(self, master):
        """创建对话框主体"""
        # 名称
        ttk.Label(master, text="名称:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.name_entry = ttk.Entry(master, width=50)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # 类型
        ttk.Label(master, text="类型:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.type_var = tk.StringVar()
        self.type_combo = ttk.Combobox(master, textvariable=self.type_var, values=[InfoSourceType.WEB_PAGE, InfoSourceType.API], state="readonly")
        self.type_combo.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        self.type_combo.current(0)
        
        # URL
        ttk.Label(master, text="URL:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.url_entry = ttk.Entry(master, width=50)
        self.url_entry.grid(row=2, column=1, padx=5, pady=5)
        
        # 更新间隔
        ttk.Label(master, text="更新间隔(秒):").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.interval_var = tk.StringVar()
        self.interval_entry = ttk.Entry(master, textvariable=self.interval_var, width=10)
        self.interval_entry.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
        self.interval_var.set("3600")
        
        # 填充初始值
        if self.initial_values:
            self.name_entry.insert(0, self.initial_values[0])
            self.type_var.set(self.initial_values[1])
            self.url_entry.insert(0, self.initial_values[2])
            self.interval_var.set(self.initial_values[3])
        
        return self.name_entry  # 返回第一个焦点控件
    
    def apply(self):
        """应用对话框结果"""
        name = self.name_entry.get().strip()
        source_type = self.type_var.get()
        url = self.url_entry.get().strip()
        interval = self.interval_var.get().strip()
        
        # 验证输入
        if not name:
            messagebox.showwarning("警告", "名称不能为空")
            return
        
        if not url:
            messagebox.showwarning("警告", "URL不能为空")
            return
        
        try:
            interval = int(interval)
            if interval <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("警告", "更新间隔必须是正整数")
            return
        
        self.result = (name, source_type, url, interval)

# 运行配置界面
if __name__ == "__main__":
    root = tk.Tk()
    app = ConfigGUI(root)
    root.mainloop()
