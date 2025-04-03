import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.font import Font
import pandas as pd
import time
from datetime import datetime
from .config import config
from .utils import load_data_file, save_annotated_data, validate_record_number, show_message
import os
from threading import Thread


class DataAnnotationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Data Annotation Tool")
        self.root.geometry("800x600")
        self.root.minsize(700, 500)

        # 设置样式
        self.setup_styles()

        # 初始化变量
        self.df = None
        self.current_record = 0
        self.unsaved_changes = False
        self.save_reminder_active = False
        self.label_column = None
        self.label_type = None
        self.label_options = []

        # 创建语言选择界面
        self.create_language_selection()

        # 设置保存提醒
        self.setup_save_reminder()

        # 窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def setup_styles(self):
        """设置GUI样式"""
        style = ttk.Style()
        style.configure("TFrame", background="#f0f0f0")
        style.configure("TButton",
                        font=("Arial", 10),
                        padding=6,
                        relief="flat",
                        background="#4a6ea9",
                        foreground="black")
        style.map("TButton",
                  background=[("active", "#3a5a8a")])
        style.configure("TLabel", background="#f0f0f0", font=("Arial", 10))
        style.configure("Header.TLabel", font=("Arial", 12, "bold"))
        style.configure("TEntry", font=("Arial", 10), padding=5)
        style.configure("TCombobox", font=("Arial", 10), padding=5)
        style.configure("TRadiobutton", background="#f0f0f0", font=("Arial", 10))
        style.configure("TNotebook", background="#f0f0f0")
        style.configure("TNotebook.Tab", font=("Arial", 10), padding=6)

        # 圆角按钮
        self.root.option_add("*Button*highlightThickness", 0)
        self.root.option_add("*Button*borderWidth", 0)
        self.root.option_add("*Button*relief", "flat")
        self.root.option_add("*Button*background", "#4a6ea9")
        self.root.option_add("*Button*foreground", "black")
        self.root.option_add("*Button*activeBackground", "#3a5a8a")
        self.root.option_add("*Button*activeForeground", "white")
        self.root.option_add("*Button*font", ("Arial", 10))
        self.root.option_add("*Button*padding", 6)
        self.root.option_add("*Button*borderRadius", 10)

    def create_language_selection(self):
        """创建语言选择界面"""
        self.clear_window()

        frame = ttk.Frame(self.root, padding=20)
        frame.pack(expand=True, fill="both")

        label = ttk.Label(frame, text=config.get("language_selection"), style="Header.TLabel")
        label.pack(pady=20)

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=20)

        english_btn = ttk.Button(
            btn_frame,
            text=config.get("english"),
            command=lambda: self.set_language("en")
        )
        english_btn.pack(side="left", padx=10, ipadx=20, ipady=10)

        chinese_btn = ttk.Button(
            btn_frame,
            text=config.get("chinese"),
            command=lambda: self.set_language("zh")
        )
        chinese_btn.pack(side="left", padx=10, ipadx=20, ipady=10)

    def set_language(self, language):
        """设置语言并进入主界面"""
        config.set_language(language)
        self.create_file_selection()

    def create_file_selection(self):
        """创建文件选择界面"""
        self.clear_window()

        frame = ttk.Frame(self.root, padding=20)
        frame.pack(expand=True, fill="both")

        title = ttk.Label(frame, text=config.get("select_file"), style="Header.TLabel")
        title.pack(pady=10)

        file_types_label = ttk.Label(frame, text=config.get("file_types"))
        file_types_label.pack(pady=5)

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=20)

        self.file_path_var = tk.StringVar(value=config.get("file_not_selected"))
        file_label = ttk.Label(frame, textvariable=self.file_path_var, wraplength=600)
        file_label.pack(pady=10)

        browse_btn = ttk.Button(
            btn_frame,
            text=config.get("select_file"),
            command=self.browse_file
        )
        browse_btn.pack(side="left", padx=10, ipadx=20, ipady=10)

        next_btn = ttk.Button(
            btn_frame,
            text=config.get("next"),
            command=self.validate_and_proceed,
            state="disabled"
        )
        next_btn.pack(side="left", padx=10, ipadx=20, ipady=10)
        self.next_btn = next_btn

    def browse_file(self):
        """浏览文件"""
        filetypes = [
            (config.get("file_types"), "*.csv;*.xlsx;*.xls"),
            ("CSV Files", "*.csv"),
            ("Excel Files", "*.xlsx;*.xls")
        ]

        filepath = filedialog.askopenfilename(
            title=config.get("select_file"),
            filetypes=filetypes
        )

        if filepath:
            self.file_path_var.set(f"{config.get('file_selected')} {filepath}")
            self.filepath = filepath
            self.next_btn["state"] = "normal"

    def validate_and_proceed(self):
        """验证文件并进入下一步"""
        self.df, error = load_data_file(self.filepath)

        if error:
            show_message(config.get("error"), error, "error")
            return

        # 检查列数是否过多
        if len(self.df.columns) > 10:
            show_message(
                config.get("warning"),
                config.get("max_columns_warning").format(len(self.df.columns)),
                "warning"
            )

        self.show_file_stats()

    def show_file_stats(self):
        """显示文件统计信息"""
        self.clear_window()

        frame = ttk.Frame(self.root, padding=20)
        frame.pack(expand=True, fill="both")

        title = ttk.Label(frame, text=config.get("file_stats"), style="Header.TLabel")
        title.pack(pady=10)

        # 显示基本信息
        stats_frame = ttk.Frame(frame)
        stats_frame.pack(fill="x", pady=10)

        rows_label = ttk.Label(stats_frame, text=f"{config.get('total_rows')} {len(self.df)}")
        rows_label.pack(anchor="w")

        cols_label = ttk.Label(stats_frame, text=f"{config.get('total_columns')} {len(self.df.columns)}")
        cols_label.pack(anchor="w")

        cols_names_label = ttk.Label(
            stats_frame,
            text=f"{config.get('column_names')} {', '.join(self.df.columns)}",
            wraplength=600
        )
        cols_names_label.pack(anchor="w", pady=10)

        # 按钮框架
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=20)

        back_btn = ttk.Button(
            btn_frame,
            text=config.get("back"),
            command=self.create_file_selection
        )
        back_btn.pack(side="left", padx=10, ipadx=20, ipady=10)

        next_btn = ttk.Button(
            btn_frame,
            text=config.get("confirm_proceed"),
            command=self.setup_label_column
        )
        next_btn.pack(side="left", padx=10, ipadx=20, ipady=10)

    def setup_label_column(self):
        """设置标注列"""
        self.clear_window()

        frame = ttk.Frame(self.root, padding=20)
        frame.pack(expand=True, fill="both")

        title = ttk.Label(frame, text=config.get("has_label_column"), style="Header.TLabel")
        title.pack(pady=10)

        # 是否有标注列
        self.has_label_var = tk.StringVar(value="no")

        yes_btn = ttk.Radiobutton(
            frame,
            text=config.get("yes"),
            variable=self.has_label_var,
            value="yes"
        )
        yes_btn.pack(anchor="w", pady=5)

        no_btn = ttk.Radiobutton(
            frame,
            text=config.get("no"),
            variable=self.has_label_var,
            value="no"
        )
        no_btn.pack(anchor="w", pady=5)

        # 下一步按钮
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=20)

        back_btn = ttk.Button(
            btn_frame,
            text=config.get("back"),
            command=self.show_file_stats
        )
        back_btn.pack(side="left", padx=10, ipadx=20, ipady=10)

        next_btn = ttk.Button(
            btn_frame,
            text=config.get("next"),
            command=self.process_label_column
        )
        next_btn.pack(side="left", padx=10, ipadx=20, ipady=10)

    def process_label_column(self):
        """处理标注列选择"""
        if self.has_label_var.get() == "yes":
            self.select_existing_label_column()
        else:
            self.create_new_label_column()

    def select_existing_label_column(self):
        """选择已有的标注列"""
        self.clear_window()

        frame = ttk.Frame(self.root, padding=20)
        frame.pack(expand=True, fill="both")

        title = ttk.Label(frame, text=config.get("select_label_column"), style="Header.TLabel")
        title.pack(pady=10)

        self.label_column_var = tk.StringVar()
        columns = list(self.df.columns)

        combobox = ttk.Combobox(frame, textvariable=self.label_column_var, values=columns)
        combobox.pack(pady=10, fill="x")
        combobox.current(0)

        # 下一步按钮
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=20)

        back_btn = ttk.Button(
            btn_frame,
            text=config.get("back"),
            command=self.setup_label_column
        )
        back_btn.pack(side="left", padx=10, ipadx=20, ipady=10)

        next_btn = ttk.Button(
            btn_frame,
            text=config.get("next"),
            command=self.process_label_type
        )
        next_btn.pack(side="left", padx=10, ipadx=20, ipady=10)

    def create_new_label_column(self):
        """创建新的标注列"""
        self.clear_window()

        frame = ttk.Frame(self.root, padding=20)
        frame.pack(expand=True, fill="both")

        title = ttk.Label(frame, text=config.get("enter_label_name"), style="Header.TLabel")
        title.pack(pady=10)

        self.new_label_name_var = tk.StringVar(value="label")
        entry = ttk.Entry(frame, textvariable=self.new_label_name_var)
        entry.pack(pady=10, fill="x")

        # 下一步按钮
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=20)

        back_btn = ttk.Button(
            btn_frame,
            text=config.get("back"),
            command=self.setup_label_column
        )
        back_btn.pack(side="left", padx=10, ipadx=20, ipady=10)

        next_btn = ttk.Button(
            btn_frame,
            text=config.get("next"),
            command=self.process_new_label_column
        )
        next_btn.pack(side="left", padx=10, ipadx=20, ipady=10)

    def process_new_label_column(self):
        """处理新标注列"""
        label_name = self.new_label_name_var.get().strip()
        if not label_name:
            show_message(config.get("error"), config.get("filename_required"), "error")
            return

        # 添加新列
        self.df[label_name] = ""
        self.label_column = label_name
        self.process_label_type()

    def process_label_type(self):
        """处理标注类型选择"""
        if self.has_label_var.get() == "yes":
            self.label_column = self.label_column_var.get()

        self.clear_window()

        frame = ttk.Frame(self.root, padding=20)
        frame.pack(expand=True, fill="both")

        title = ttk.Label(frame, text=config.get("label_type"), style="Header.TLabel")
        title.pack(pady=10)

        self.label_type_var = tk.StringVar(value="categorical")

        categorical_btn = ttk.Radiobutton(
            frame,
            text=config.get("categorical"),
            variable=self.label_type_var,
            value="categorical"
        )
        categorical_btn.pack(anchor="w", pady=5)

        text_btn = ttk.Radiobutton(
            frame,
            text=config.get("text"),
            variable=self.label_type_var,
            value="text"
        )
        text_btn.pack(anchor="w", pady=5)

        # 下一步按钮
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=20)

        back_btn = ttk.Button(
            btn_frame,
            text=config.get("back"),
            command=self.setup_label_column if self.has_label_var.get() == "no" else self.select_existing_label_column
        )
        back_btn.pack(side="left", padx=10, ipadx=20, ipady=10)

        next_btn = ttk.Button(
            btn_frame,
            text=config.get("next"),
            command=self.process_label_type_selection
        )
        next_btn.pack(side="left", padx=10, ipadx=20, ipady=10)

    def process_label_type_selection(self):
        """处理标注类型选择"""
        self.label_type = self.label_type_var.get()

        if self.label_type == "categorical":
            self.setup_label_options()
        else:
            self.start_annotation()

    def setup_label_options(self):
        """设置标注选项"""
        self.clear_window()

        frame = ttk.Frame(self.root, padding=20)
        frame.pack(expand=True, fill="both")

        title = ttk.Label(frame, text=config.get("num_options"), style="Header.TLabel")
        title.pack(pady=10)

        self.num_options_var = tk.StringVar(value="2")
        entry = ttk.Entry(frame, textvariable=self.num_options_var)
        entry.pack(pady=10, fill="x")

        # 下一步按钮
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=20)

        back_btn = ttk.Button(
            btn_frame,
            text=config.get("back"),
            command=self.process_label_type
        )
        back_btn.pack(side="left", padx=10, ipadx=20, ipady=10)

        next_btn = ttk.Button(
            btn_frame,
            text=config.get("next"),
            command=self.process_num_options
        )
        next_btn.pack(side="left", padx=10, ipadx=20, ipady=10)

    def process_num_options(self):
        """处理选项数量"""
        try:
            num_options = int(self.num_options_var.get())
            if num_options < 1:
                raise ValueError
        except ValueError:
            show_message(config.get("error"), config.get("invalid_record_num"), "error")
            return

        if num_options > 10:
            show_message(
                config.get("warning"),
                config.get("max_options_warning").format(num_options),
                "warning"
            )

        self.setup_option_entries(num_options)

    def setup_option_entries(self, num_options):
        """设置选项输入框"""
        self.clear_window()

        frame = ttk.Frame(self.root, padding=20)
        frame.pack(expand=True, fill="both")

        title = ttk.Label(frame, text=config.get("enter_options"), style="Header.TLabel")
        title.pack(pady=10)

        self.option_vars = []
        for i in range(num_options):
            option_frame = ttk.Frame(frame)
            option_frame.pack(fill="x", pady=5)

            label = ttk.Label(option_frame, text=f"{config.get('option')}{i + 1}:")
            label.pack(side="left", padx=5)

            var = tk.StringVar()
            entry = ttk.Entry(option_frame, textvariable=var)
            entry.pack(side="left", fill="x", expand=True)

            self.option_vars.append(var)

        # 按钮框架
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=20)

        back_btn = ttk.Button(
            btn_frame,
            text=config.get("back"),
            command=self.setup_label_options
        )
        back_btn.pack(side="left", padx=10, ipadx=20, ipady=10)

        next_btn = ttk.Button(
            btn_frame,
            text=config.get("next"),
            command=self.process_options
        )
        next_btn.pack(side="left", padx=10, ipadx=20, ipady=10)

    def process_options(self):
        """处理选项输入"""
        self.label_options = []
        for var in self.option_vars:
            option = var.get().strip()
            if not option:
                show_message(config.get("error"),
                             f"{config.get('option')} {len(self.label_options) + 1} {config.get('filename_required')}",
                             "error")
                return
            self.label_options.append(option)

        self.start_annotation()

    def start_annotation(self):
        """开始标注"""
        self.clear_window()

        # 初始化当前记录
        self.current_record = 0

        # 如果是新列，初始化空值
        if self.has_label_var.get() == "no":
            self.df[self.label_column] = ""

        # 创建主界面
        self.create_annotation_interface()

    def create_annotation_interface(self):
        """创建标注界面"""
        self.clear_window()

        # 主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(expand=True, fill="both", padx=10, pady=10)

        # 标题
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill="x", pady=5)

        title = ttk.Label(title_frame, text=config.get("annotation_title"), style="Header.TLabel")
        title.pack(side="left")

        # 记录导航
        nav_frame = ttk.Frame(main_frame)
        nav_frame.pack(fill="x", pady=10)

        self.record_label = ttk.Label(
            nav_frame,
            text=f"{config.get('record_num')}{self.current_record + 1}{config.get('of')}{len(self.df)}"
        )
        self.record_label.pack(side="left", padx=10)

        # 跳转记录
        jump_frame = ttk.Frame(nav_frame)
        jump_frame.pack(side="right")

        jump_label = ttk.Label(jump_frame, text=config.get("jump_to"))
        jump_label.pack(side="left", padx=5)

        self.jump_entry = ttk.Entry(jump_frame, width=5)
        self.jump_entry.pack(side="left", padx=5)

        jump_btn = ttk.Button(
            jump_frame,
            text=config.get("go"),
            command=self.jump_to_record
        )
        jump_btn.pack(side="left", padx=5)

        # 数据展示
        data_frame = ttk.LabelFrame(main_frame, text="Data", padding=10)
        data_frame.pack(fill="both", expand=True, pady=10)

        # 使用Canvas和Frame实现可滚动区域
        canvas = tk.Canvas(data_frame)
        scrollbar = ttk.Scrollbar(data_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 显示当前记录
        self.display_record(scrollable_frame)

        # 导航按钮
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill="x", pady=10)

        self.prev_btn = ttk.Button(
            btn_frame,
            text=config.get("prev"),
            command=self.prev_record,
            state="disabled" if self.current_record == 0 else "normal"
        )
        self.prev_btn.pack(side="left", padx=10, ipadx=20, ipady=10)

        save_btn = ttk.Button(
            btn_frame,
            text=config.get("save_now"),
            command=self.save_data
        )
        save_btn.pack(side="left", padx=10, ipadx=20, ipady=10)

        self.next_btn = ttk.Button(
            btn_frame,
            text=config.get("next_record"),
            command=self.next_record,
            state="disabled" if self.current_record == len(self.df) - 1 else "normal"
        )
        self.next_btn.pack(side="left", padx=10, ipadx=20, ipady=10)

        finish_btn = ttk.Button(
            btn_frame,
            text=config.get("finish_annotation"),
            command=self.finish_annotation
        )
        finish_btn.pack(side="right", padx=10, ipadx=20, ipady=10)

    def display_record(self, parent_frame):
        """显示当前记录"""
        # 清除之前的显示
        for widget in parent_frame.winfo_children():
            widget.destroy()

        # 获取当前记录
        record = self.df.iloc[self.current_record]

        # 显示每个字段
        for i, (col_name, value) in enumerate(record.items()):
            if col_name == self.label_column:
                continue

            field_frame = ttk.Frame(parent_frame)
            field_frame.pack(fill="x", pady=5)

            name_label = ttk.Label(field_frame, text=f"{col_name}:", width=20, anchor="e")
            name_label.pack(side="left", padx=5)

            value_label = ttk.Label(field_frame, text=str(value), wraplength=400, anchor="w")
            value_label.pack(side="left", fill="x", expand=True)

        # 添加标注区域
        label_frame = ttk.Frame(parent_frame)
        label_frame.pack(fill="x", pady=10)

        name_label = ttk.Label(label_frame, text=f"{self.label_column}:", width=20, anchor="e")
        name_label.pack(side="left", padx=5)

        if self.label_type == "categorical":
            self.label_var = tk.StringVar(value=record[self.label_column])

            for option in self.label_options:
                rb = ttk.Radiobutton(
                    label_frame,
                    text=option,
                    variable=self.label_var,
                    value=option
                )
                rb.pack(anchor="w", padx=5, pady=2)
        else:
            self.label_var = tk.StringVar(value=record[self.label_column])
            entry = ttk.Entry(label_frame, textvariable=self.label_var)
            entry.pack(fill="x", expand=True)

    def prev_record(self):
        """显示上一条记录"""
        if self.current_record > 0:
            self.save_current_label()
            self.current_record -= 1
            self.update_annotation_interface()

    def next_record(self):
        """显示下一条记录"""
        if self.current_record < len(self.df) - 1:
            self.save_current_label()
            self.current_record += 1
            self.update_annotation_interface()

    def jump_to_record(self):
        """跳转到指定记录"""
        input_str = self.jump_entry.get()
        valid, result = validate_record_number(input_str, len(self.df))

        if valid:
            self.save_current_label()
            self.current_record = result - 1
            self.update_annotation_interface()
        else:
            show_message(config.get("error"), result, "error")

    def save_current_label(self):
        """保存当前记录的标注"""
        current_label = self.label_var.get()
        self.df.at[self.current_record, self.label_column] = current_label

        if not self.unsaved_changes and current_label != "":
            self.unsaved_changes = True

    def update_annotation_interface(self):
        """更新标注界面"""
        self.record_label.config(
            text=f"{config.get('record_num')}{self.current_record + 1}{config.get('of')}{len(self.df)}"
        )

        # 更新按钮状态
        self.prev_btn["state"] = "disabled" if self.current_record == 0 else "normal"
        self.next_btn["state"] = "disabled" if self.current_record == len(self.df) - 1 else "normal"

        # 直接重新创建整个数据区域
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Frame):  # 主框架
                for child in widget.winfo_children():
                    if isinstance(child, ttk.LabelFrame) and child["text"] == "Data":
                        # 销毁原有数据区域
                        child.destroy()
                        # 创建新的数据区域
                        new_data_frame = ttk.LabelFrame(widget, text="Data", padding=10)
                        new_data_frame.pack(fill="both", expand=True, pady=10)

                        # 重新创建Canvas和滚动条
                        canvas = tk.Canvas(new_data_frame)
                        scrollbar = ttk.Scrollbar(new_data_frame, orient="vertical", command=canvas.yview)
                        scrollable_frame = ttk.Frame(canvas)

                        scrollable_frame.bind(
                            "<Configure>",
                            lambda e: canvas.configure(
                                scrollregion=canvas.bbox("all")
                            )
                        )

                        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
                        canvas.configure(yscrollcommand=scrollbar.set)

                        canvas.pack(side="left", fill="both", expand=True)
                        scrollbar.pack(side="right", fill="y")

                        # 显示当前记录
                        self.display_record(scrollable_frame)
                        break
                break

    def save_data(self):
        """保存数据"""
        self.save_current_label()

        # 创建保存对话框
        self.clear_window()

        frame = ttk.Frame(self.root, padding=20)
        frame.pack(expand=True, fill="both")

        title = ttk.Label(frame, text=config.get("enter_filename"), style="Header.TLabel")
        title.pack(pady=10)

        self.filename_var = tk.StringVar()
        entry = ttk.Entry(frame, textvariable=self.filename_var)
        entry.pack(pady=10, fill="x")

        # 按钮框架
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=20)

        back_btn = ttk.Button(
            btn_frame,
            text=config.get("back"),
            command=self.create_annotation_interface
        )
        back_btn.pack(side="left", padx=10, ipadx=20, ipady=10)

        save_btn = ttk.Button(
            btn_frame,
            text=config.get("save_now"),
            command=self.process_save
        )
        save_btn.pack(side="left", padx=10, ipadx=20, ipady=10)

    def process_save(self):
        """处理保存操作"""
        filename = self.filename_var.get().strip()
        if not filename:
            show_message(config.get("error"), config.get("filename_required"), "error")
            return

        # 显示保存中状态
        saving_label = ttk.Label(self.root, text=config.get("saving"))
        saving_label.pack(pady=10)
        self.root.update()

        # 在后台线程中保存
        def save_thread():
            success, result = save_annotated_data(self.df, self.filepath, filename)

            self.root.after(0, lambda: self.handle_save_result(success, result, saving_label))

        Thread(target=save_thread, daemon=True).start()

    def handle_save_result(self, success, result, saving_label):
        """处理保存结果"""
        saving_label.destroy()

        if success:
            save_path, file_size, save_time = result
            message = (
                f"{config.get('save_complete')}\n\n"
                f"{config.get('save_location')}{save_path}\n"
                f"{config.get('file_size')}{file_size}\n"
                f"{config.get('save_time')}{save_time}"
            )

            show_message(config.get("success"), message, "success")
            self.unsaved_changes = False

            # 返回标注界面
            self.create_annotation_interface()
        else:
            show_message(config.get("error"), result, "error")

    def finish_annotation(self):
        """完成标注"""
        if self.unsaved_changes:
            if not messagebox.askyesno(
                    config.get("warning"),
                    config.get("unsaved_changes"),
                    parent=self.root
            ):
                return

        self.save_data()

    def setup_save_reminder(self):
        """设置保存提醒"""

        def reminder():
            if self.unsaved_changes and not self.save_reminder_active:
                self.save_reminder_active = True
                show_message(
                    config.get("info"),
                    config.get("save_reminder"),
                    "info"
                )
                self.save_reminder_active = False

            self.root.after(300000, reminder)  # 5分钟提醒一次

        self.root.after(300000, reminder)

    def clear_window(self):
        """清除窗口内容"""
        for widget in self.root.winfo_children():
            widget.destroy()

    def on_close(self):
        """窗口关闭事件处理"""
        if self.unsaved_changes:
            if not messagebox.askyesno(
                    config.get("warning"),
                    config.get("exit_confirmation"),
                    parent=self.root
            ):
                return

        self.root.destroy()