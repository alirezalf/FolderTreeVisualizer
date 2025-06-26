import os
from typing import Set

class TreeGenerator:
    def __init__(self, root_path: str, ignore_items: Set[str] = None):
        self.root_path = root_path
        self.ignore_items = ignore_items if ignore_items else set()
        
    def generate_tree(self) -> str:
        """تولید ساختار درختی به صورت رشته متنی"""
        if not os.path.exists(self.root_path):
            return "Error: Root path does not exist\n"
        
        base_name = os.path.basename(self.root_path.rstrip(os.sep))
        tree = f"{base_name}\n"
        tree += self._build_tree(self.root_path, "", True)
        return tree + "\n"
    
    def _build_tree(self, path: str, prefix: str, is_last: bool) -> str:
        """تابع بازگشتی برای ساخت درخت با خطوط متصل"""
        tree_str = ""
        try:
            items = sorted(os.listdir(path))
            items = [item for item in items if item not in self.ignore_items]
            count = len(items)
            
            for idx, item in enumerate(items):
                item_path = os.path.join(path, item)
                last = idx == count - 1
                connector = "└── " if last else "├── "
                display_name = f"[HIDDEN] {item}" if item.startswith('.') else item
                tree_str += prefix + connector + display_name + "\n"
                
                if os.path.isdir(item_path):
                    extension = "    " if last else "│   "
                    tree_str += self._build_tree(item_path, prefix + extension, last)
        except PermissionError:
            tree_str += prefix + "└── [Permission Denied]\n"
        
        return tree_str

    def save_tree_to_file(self, file_path: str, ignore_items: Set[str]):
        """ذخیره ساختار درختی در فایل"""
        tree = self.generate_tree()
        # جایگزینی کاراکترهای ضخیم با کاراکترهای باریک‌تر (با عرض ثابت)
        formatted_tree = tree.replace("│", "│").replace("├", "├").replace("└", "└")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(formatted_tree)

