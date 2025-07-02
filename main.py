import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QTreeView, QFileSystemModel, QPushButton, QTextEdit, 
                             QLabel, QFileDialog, QSplitter, QHeaderView, QCheckBox)
from PyQt5.QtCore import Qt, QDir, QModelIndex, QSize
from tree_generator import TreeGenerator

class CheckableFileSystemModel(QFileSystemModel):
    def __init__(self):
        super().__init__()
        self.checked_items = set()

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.CheckStateRole and index.column() == 0:
            return Qt.Checked if self.filePath(index) in self.checked_items else Qt.Unchecked
        return super().data(index, role)

    def setData(self, index, value, role):
        if role == Qt.CheckStateRole and index.column() == 0:
            path = self.filePath(index)
            if value == Qt.Checked:
                self.checked_items.add(path)
            else:
                self.checked_items.discard(path)
            self.dataChanged.emit(index, index)
            return True
        return super().setData(index, value, role)

    def flags(self, index):
        return super().flags(index) | Qt.ItemIsUserCheckable

class FolderTreeVisualizer(QMainWindow):
    def center_window(self):
        # گرفتن مرکز صفحه نمایش
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        window_geometry = self.frameGeometry()

        # محاسبه مرکز
        center_point = screen_geometry.center()
        window_geometry.moveCenter(center_point)

        # جابجایی پنجره به نقطه‌ی جدید
        self.move(window_geometry.topLeft())
        
        
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Folder Tree Visualizer - (written by Alireza Labbaf)")
        self.setGeometry(100, 100, 1200, 800)
        
        self.root_path = ""
        self.ignore_items = set()
        
        self.init_ui()
        
    def init_ui(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        
        splitter = QSplitter(Qt.Horizontal)
        
        # پنل سمت چپ (انتخاب فولدر با چک باکس)
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        
        # بخش انتخاب فولدر ریشه
        self.folder_label = QLabel("Selected Root Folder: None")
        left_layout.addWidget(self.folder_label)
                        
        # درخت فایل سیستم با چک باکس
        self.folder_tree = QTreeView()
        self.folder_model = CheckableFileSystemModel()
        self.folder_model.setRootPath("")
        self.folder_model.setFilter(QDir.AllDirs | QDir.Files | QDir.NoDotAndDotDot | QDir.Hidden)
        self.folder_tree.setModel(self.folder_model)
        
        # تنظیمات هدر
        self.folder_tree.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.folder_tree.header().setStretchLastSection(True)
        self.folder_tree.setSelectionMode(QTreeView.SingleSelection)
        
        left_layout.addWidget(self.folder_tree)
        
        # دکمه های سمت چپ
        btn_panel = QWidget()
        btn_layout = QHBoxLayout()
        
        select_btn = QPushButton("Browse Folder")
        select_btn.clicked.connect(self.select_root_folder)
        btn_layout.addWidget(select_btn)
        
        reset_btn = QPushButton("Reset")
        reset_btn.clicked.connect(self.reset_selection)
        btn_layout.addWidget(reset_btn)
        
        btn_panel.setLayout(btn_layout)
        left_layout.addWidget(btn_panel)
        
        left_panel.setLayout(left_layout)
        
        # پنل سمت راست (موارد نادیده گرفته شده)
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        
        right_layout.addWidget(QLabel("Select Items to Ignore:"))
        
        self.ignore_tree = QTreeView()
        self.ignore_model = CheckableFileSystemModel()
        self.ignore_model.setRootPath("")
        self.ignore_model.setFilter(QDir.AllDirs | QDir.Files | QDir.NoDotAndDotDot | QDir.Hidden)
        self.ignore_tree.setModel(self.ignore_model)
        
        # تنظیم هدر برای نمایش اطلاعات کامل
        self.ignore_tree.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.ignore_tree.setSelectionMode(QTreeView.NoSelection)
        
        right_layout.addWidget(self.ignore_tree)
        
        right_panel.setLayout(right_layout)
        
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([500, 500])
        
        # پنل پایینی (نمایش ساختار درختی)
        bottom_panel = QWidget()
        bottom_layout = QVBoxLayout()
        
        self.tree_display = QTextEdit()
        self.tree_display.setReadOnly(True)
        self.tree_display.setFontFamily("Courier New")
        self.tree_display.setFontPointSize(11)
        
        # دکمه های پایینی
        action_panel = QWidget()
        action_layout = QHBoxLayout()
        
        generate_btn = QPushButton("Generate Tree")
        generate_btn.clicked.connect(self.generate_tree)
        action_layout.addWidget(generate_btn)
                       
        save_btn = QPushButton("Save to File")
        save_btn.clicked.connect(self.save_to_file)
        action_layout.addWidget(save_btn)
        
        clear_btn = QPushButton("Clear All")
        clear_btn.clicked.connect(self.clear_all)
        action_layout.addWidget(clear_btn)
        
        action_panel.setLayout(action_layout)
        
        bottom_layout.addWidget(QLabel("Folder Tree Structure:"))
        bottom_layout.addWidget(self.tree_display)
        bottom_layout.addWidget(action_panel)
        
        bottom_panel.setLayout(bottom_layout)
        
        # چیدمان نهایی
        # تقسیم کننده اصلی برای ارتفاع
        main_splitter = QSplitter(Qt.Vertical)
        main_splitter.addWidget(splitter)        # پنل بالا (چپ و راست)
        main_splitter.addWidget(bottom_panel)    # پنل پایین (نمایش درخت)

        # تنظیم ارتفاع پنل‌ها (مثلاً 700 برای بالا، 300 برای پایین)
        main_splitter.setSizes([400, 600])

        self.setCentralWidget(main_splitter)
        
        # اتصال سیگنال ها
        self.folder_tree.selectionModel().selectionChanged.connect(self.update_root_selection)
        self.folder_model.dataChanged.connect(self.update_ignore_view)
        initial_path = os.getcwd()
        self.folder_tree.setRootIndex(self.folder_model.index(initial_path))
        self.ignore_tree.setRootIndex(self.ignore_model.index(initial_path))
        self.folder_label.setText(f"Selected Root Folder: {initial_path}")
        self.root_path = initial_path
        self.center_window()
        
    def select_root_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Root Folder")
        if folder:
            self.root_path = folder
            self.folder_label.setText(f"Selected Root Folder: {folder}")
            self.folder_tree.setRootIndex(self.folder_model.index(folder))
            self.ignore_tree.setRootIndex(self.ignore_model.index(folder))

            self.folder_model.checked_items.clear()
            self.ignore_model.checked_items.clear() 

            self.update_ignore_view() 

    def update_root_selection(self, selected, deselected):
        indexes = selected.indexes()
        if indexes:
            index = indexes[0]
            path = self.folder_model.filePath(index)
            if os.path.isdir(path):
                self.root_path = path
                self.folder_label.setText(f"Selected Root Folder: {path}")
                self.ignore_tree.setRootIndex(self.ignore_model.index(path))
    
    def update_ignore_view(self):
        if self.root_path:
            root_index = self.folder_model.index(self.root_path)
            self.ignore_tree.setRootIndex(self.ignore_model.index(self.root_path))
    
    
    def generate_tree(self):
        if not self.root_path:
            self.tree_display.setPlainText("Please select a root folder first.")
            return

        # ✅ گرفتن آیتم‌های تیک‌خورده از مدل سمت راست (ignore_model)
        ignore_items = {os.path.basename(path) for path in self.ignore_model.checked_items}

        generator = TreeGenerator(self.root_path, ignore_items)
        tree_structure = generator.generate_tree()

        display_tree = tree_structure.replace("│", "│").replace("├", "├").replace("└", "└")
        self.tree_display.setPlainText(display_tree)
        self.ignore_items = ignore_items

        
    def save_to_file(self):
        if not self.root_path:
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Tree Structure", "folder_structure.txt", "Text Files (*.txt);;All Files (*)"
        )
        
        if file_path:
            generator = TreeGenerator(self.root_path, self.ignore_items)
            generator.save_tree_to_file(file_path, self.ignore_items)
            self.statusBar().showMessage(f"Tree saved to {file_path}", 3000)
    
    def reset_selection(self):
        self.folder_model.checked_items.clear()
        root_index = self.folder_model.index(self.root_path)
        self.folder_model.dataChanged.emit(root_index, root_index)
        self.tree_display.clear()
    
    def clear_all(self):
        self.root_path = ""
        self.folder_label.setText("Selected Root Folder: None")
        self.folder_model.checked_items.clear()
        self.folder_tree.setRootIndex(self.folder_model.index(""))
        self.ignore_tree.setRootIndex(self.ignore_model.index(""))
        self.tree_display.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FolderTreeVisualizer()
    window.show()
    sys.exit(app.exec_())