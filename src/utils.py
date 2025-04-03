import pandas as pd
import os
from pathlib import Path
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from .config import config


def load_data_file(filepath):
    """加载数据文件，支持CSV和Excel格式"""
    try:
        if filepath.endswith('.csv'):
            df = pd.read_csv(filepath)
        elif filepath.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(filepath)
        else:
            return None, config.get("invalid_file_msg")

        # 检查数据是否为空
        if df.empty:
            return None, config.get("invalid_file_msg")

        return df, None
    except Exception as e:
        print(f"Error loading file: {e}")
        return None, config.get("invalid_file_msg")


def save_annotated_data(df, original_path, filename):
    """保存标注后的数据"""
    try:
        if not filename:
            return False, config.get("filename_required")

        # 确定保存路径
        original_dir = os.path.dirname(original_path)
        save_path = os.path.join(original_dir, f"{filename}.csv")

        # 避免覆盖
        counter = 1
        while os.path.exists(save_path):
            save_path = os.path.join(original_dir, f"{filename}_{counter}.csv")
            counter += 1

        # 保存为CSV
        df.to_csv(save_path, index=False)

        # 获取文件信息
        file_size = os.path.getsize(save_path)
        file_size_str = f"{file_size / 1024:.2f} KB" if file_size < 1024 * 1024 else f"{file_size / (1024 * 1024):.2f} MB"
        save_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return True, (save_path, file_size_str, save_time)
    except Exception as e:
        print(f"Error saving file: {e}")
        return False, str(e)


def validate_record_number(input_str, max_records):
    """验证记录号输入是否有效"""
    try:
        num = int(input_str)
        if 1 <= num <= max_records:
            return True, num
        return False, config.get("invalid_record_num")
    except ValueError:
        return False, config.get("invalid_record_num")


def show_message(title, message, message_type="info"):
    """显示消息对话框"""
    root = tk.Tk()
    root.withdraw()

    if message_type == "error":
        messagebox.showerror(title, message)
    elif message_type == "warning":
        messagebox.showwarning(title, message)
    elif message_type == "success":
        messagebox.showinfo(title, message)
    else:
        messagebox.showinfo(title, message)

    root.destroy()


def create_tooltip(widget, text):
    """创建工具提示"""
    tooltip = tk.Toplevel(widget)
    tooltip.withdraw()
    tooltip.overrideredirect(True)

    label = tk.Label(tooltip, text=text, bg="lightyellow", relief="solid", borderwidth=1)
    label.pack()

    def enter(event):
        x = widget.winfo_rootx() + widget.winfo_width() + 5
        y = widget.winfo_rooty()
        tooltip.geometry(f"+{x}+{y}")
        tooltip.deiconify()

    def leave(event):
        tooltip.withdraw()

    widget.bind("<Enter>", enter)
    widget.bind("<Leave>", leave)

    return tooltip