import json
import os
from pathlib import Path


class Config:
    def __init__(self):
        self.current_language = "en"  # 默认英文
        self.strings = self.load_strings()

    def load_strings(self):
        """加载语言字符串"""
        resources_dir = Path(__file__).parent / "resources"
        lang_file = f"strings_{self.current_language}.json"
        file_path = resources_dir / lang_file

        if not file_path.exists():
            # 如果语言文件不存在，默认使用英文
            file_path = resources_dir / "strings_en.json"

        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def set_language(self, language):
        """设置语言"""
        if language in ["en", "zh"]:
            self.current_language = language
            self.strings = self.load_strings()

    def get(self, key, default=None):
        """获取语言字符串"""
        return self.strings.get(key, default)


config = Config()