import os
import nbtlib
from nbtlib import CompoundSchema, File, schema
from io import BytesIO
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QFileDialog, QTreeWidget, QTreeWidgetItem, QApplication
import re
from nbtlib.tag import (
    INT,
    Byte,
    Float,
    Int,
    List,
    Long,
    String,
    read_numeric,
    write_numeric,
)

class BedrockLevelFile(File, CompoundSchema):

    def __init__(
        self, level_data=None, version=8, *, gzipped=False, byteorder="little"
    ):
        super().__init__({"": level_data or {}}, gzipped=gzipped, byteorder=byteorder)
        self.version = version

    @classmethod
    def parse(cls, buff, byteorder="little"):
        version = read_numeric(INT, buff, byteorder)
        _length = read_numeric(INT, buff, byteorder)
        self = super().parse(buff, byteorder)
        self.version = version
        return self

    def write(self, buff, byteorder="little"):
        tmp = BytesIO()
        super().write(tmp, byteorder)
        tmp.seek(0)
        data = tmp.read()

        write_numeric(INT, self.version, buff, byteorder)
        write_numeric(INT, len(data), buff, byteorder)
        buff.write(data)

    @classmethod
    def from_buffer(cls, buff, byteorder="little"):
        return super().from_buffer(buff, byteorder)

    @classmethod
    def load(cls, filename, gzipped=False, byteorder="little"):
        return super().load(filename, gzipped, byteorder)

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
                    nbt_file = BedrockLevelFile.load(os.path.join(root, file))
                    child = QTreeWidgetItem(self.tree)
                    child.setText(0, file)
                    self.print_tags(child, nbt_file)
            for dir in dirs:
                self.open_folder(os.path.join(root, dir))
                
    def open_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File", "", "NBT Files (*.nbt);;DAT Files (*.dat);; All Files (*)", options=options)
        if file_path:
            nbt_file = BedrockLevelFile.load(file_path)
            child = QTreeWidgetItem(self.tree)
            child.setText(0, os.path.basename(file_path))
            self.print_tags(child, nbt_file)

    def print_tags(self, parent, tag):
        if isinstance(tag, nbtlib.tag.Compound):
            for key, value in tag.items():
                if isinstance(value, (nbtlib.tag.Compound, nbtlib.tag.List)):
                    child = QtWidgets.QTreeWidgetItem()
                    if isinstance(value, nbtlib.tag.Compound):
                        child.setIcon(0, QtGui.QIcon("compound.png"))
                    elif isinstance(value, nbtlib.tag.List):
                        child.setIcon(0, QtGui.QIcon("list.png"))
                    s = f"{value}"
                    substring = re.search("[\(\)\{\}\[\]]",s)
                    substring = s[:substring.start()]
                    child.setText(0, f"{key}: {substring}")
                    parent.addChild(child)
                    self.print_tags(child, value)
                else:
                    child = QtWidgets.QTreeWidgetItem()
                    child.setText(0, f"{key}: {value}")
                    parent.addChild(child)
                    if isinstance(value, nbtlib.tag.Byte):
                        child.setIcon(0, QtGui.QIcon("byte.png"))
                    elif isinstance(value, nbtlib.tag.Short):
                        child.setIcon(0, QtGui.QIcon("short.png"))
                    elif isinstance(value, nbtlib.tag.Int):
                        child.setIcon(0, QtGui.QIcon("int.png"))
                    elif isinstance(value, nbtlib.tag.Long):
                        child.setIcon(0, QtGui.QIcon("long.png"))
                    elif isinstance(value, nbtlib.tag.Float):
                        child.setIcon(0, QtGui.QIcon("float.png"))
                    elif isinstance(value, nbtlib.tag.Double):
                        child.setIcon(0, QtGui.QIcon("double.png"))
                    elif isinstance(value, nbtlib.tag.String):
                        child.setIcon(0, QtGui.QIcon("string.png"))
                    elif isinstance(value, nbtlib.tag.ByteArray):
                        child.setIcon(0, QtGui.QIcon("bytearray.png"))
                    elif isinstance(value, nbtlib.tag.IntArray):
                        child.setIcon(0, QtGui.QIcon("intarray.png"))
                    elif isinstance(value, nbtlib.tag.LongArray):
                        child.setIcon(0, QtGui.QIcon("longarray.png"))
        elif isinstance(tag, nbtlib.tag.List):
            for key, value in enumerate(tag):
                if isinstance(value, (nbtlib.tag.Compound, nbtlib.tag.List)):
                    child = QtWidgets.QTreeWidgetItem()
                    if isinstance(value, nbtlib.tag.Compound):
                        child.setIcon(0, QtGui.QIcon("compound.png"))
                    elif isinstance(value, nbtlib.tag.List):
                        child.setIcon(0, QtGui.QIcon("list.png"))
                    s = f"{value}"
                    s = f"{value}"
                    substring = re.search("[\(\)\{\}\[\]]",s)
                    substring = s[:substring.start()]
                    child.setText(0, f"{key}: {substring}")
                    parent.addChild(child)
                    self.print_tags(child, value)
                else:
                    child = QtWidgets.QTreeWidgetItem()
                    child.setText(0, f"{key}: {value}")
                    parent.addChild(child)
                    if isinstance(value, nbtlib.tag.Byte):
                        child.setIcon(0, QtGui.QIcon("byte.png"))
                    elif isinstance(value, nbtlib.tag.Short):
                        child.setIcon(0, QtGui.QIcon("short.png"))
                    elif isinstance(value, nbtlib.tag.Int):
                        child.setIcon(0, QtGui.QIcon("int.png"))
                    elif isinstance(value, nbtlib.tag.Long):
                        child.setIcon(0, QtGui.QIcon("long.png"))
                    elif isinstance(value, nbtlib.tag.Float):
                        child.setIcon(0, QtGui.QIcon("float.png"))
                    elif isinstance(value, nbtlib.tag.Double):
                        child.setIcon(0, QtGui.QIcon("double.png"))
                    elif isinstance(value, nbtlib.tag.String):
                        child.setIcon(0, QtGui.QIcon("string.png"))
                    elif isinstance(value, nbtlib.tag.ByteArray):
                        child.setIcon(0, QtGui.QIcon("bytearray.png"))
                    elif isinstance(value, nbtlib.tag.IntArray):
                        child.setIcon(0, QtGui.QIcon("intarray.png"))
                    elif isinstance(value, nbtlib.tag.LongArray):
                        child.setIcon(0, QtGui.QIcon("longarray.png"))

if __name__ == '__main__':
    app = QApplication([])
    window = NBTExplorer()
    window.show()
    app.exec_()
