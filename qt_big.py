import os
import nbtlib
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QFileDialog, QTreeWidget, QTreeWidgetItem, QApplication

class NBTExplorer(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("NBT Explorer")
        self.setWindowIcon(QtGui.QIcon("icon.png"))
        self.setStyleSheet("QMainWindow {background-color: #2d2d2d;}")

        self.tree = QTreeWidget(self)
        self.tree.setHeaderHidden(True)
        self.tree.setStyleSheet("QTreeWidget {background-color: #3d3d3d; color: white;}")
        self.setCentralWidget(self.tree)

        self.open_folder_action = QtWidgets.QAction("Open Folder", self)
        self.open_folder_action.setShortcut("Ctrl+O")
        self.open_folder_action.triggered.connect(self.open_folder)

        self.open_file_action = QtWidgets.QAction("Open File", self)
        self.open_file_action.setShortcut("Ctrl+Shift+O")
        self.open_file_action.triggered.connect(self.open_file)

        self.menu = self.menuBar()
        self.file_menu = self.menu.addMenu("File")
        self.file_menu.addAction(self.open_file_action)
        self.file_menu.addAction(self.open_folder_action)

    def open_folder(self, folder_path=None):
        if not folder_path:
            options = QFileDialog.Options()
            options |= QFileDialog.ReadOnly
            folder_path = QFileDialog.getExistingDirectory(self, "Select Folder", options=options)
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.endswith(".nbt") or file.endswith(".dat"):
                    nbt_file = nbtlib.load(os.path.join(root, file))
                    child = QTreeWidgetItem(self.tree)
                    child.setText(0, file)
                    self.print_tags(child, nbt_file)
            for dir in dirs:
                child = QTreeWidgetItem(self.tree)
                child.setText(0, dir)
                self.open_folder(os.path.join(root, dir))
                
    def open_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File", "", "NBT Files (*.nbt);;DAT Files (*.dat);; All Files (*)", options=options)
        if file_path:
            nbt_file = nbtlib.load(file_path)
            child = QTreeWidgetItem(self.tree)
            child.setText(0, os.path.basename(file_path))
            self.print_tags(child, nbt_file)

    def print_tags(self, parent, tag):
        if isinstance(tag, nbtlib.tag.Compound):
            for key, value in tag.items():
                child = QTreeWidgetItem(parent)
                child.setText(0, key)
                self.print_tags(child, value)
        elif isinstance(tag, nbtlib.tag.List):
            for value in tag:
                child = QTreeWidgetItem(parent)
                child.setText(0, str(value))
                self.print_tags(child, value)
        else:
            child = QTreeWidgetItem(parent)
            child.setText(0, str(tag))

if __name__ == '__main__':
    app = QApplication([])
    window = NBTExplorer()
    window.show()
    app.exec_()
