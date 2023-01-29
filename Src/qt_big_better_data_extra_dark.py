import os
import nbtlib
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QFileDialog, QTreeWidget, QTreeWidgetItem, QApplication
from PyQt5.QtCore import Qt
import datetime
import pytz
import re

class NBTExplorer(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("NBT Explorer")
        self.setWindowIcon(QtGui.QIcon("icon.png"))
        self.setStyleSheet("QMainWindow {background-color: #141414;}")

        self.tree = QTreeWidget(self)
        self.tree.setHeaderHidden(True)
        self.tree.setStyleSheet("QTreeWidget {background-color: #141414; color: white;}")
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
                    tooltip = ""
                    # From Here
                    if key == "GameType" and isinstance(value, nbtlib.tag.Int):
                        if value == 0:
                            tooltip = "Survival"
                        elif value == 1:
                            tooltip = "Creative"
                        elif value == 2:
                            tooltip = "Adventure"
                        elif value == 3:
                            tooltip = "Spectator"
                        else:
                            tooltip = ""
                    elif key == "Difficulty" and isinstance(value, nbtlib.tag.Byte):
                        if value == 0:
                            tooltip = "Peaceful"
                        elif value == 1:
                            tooltip = "Easy"
                        elif value == 2:
                            tooltip = "Normal"
                        else:
                            tooltip = "Hard"
                    elif key == "Time" and isinstance(value, nbtlib.tag.Long):
                        tooltip = ""

                        if value >= 0:
                            secs = value // 20
                            mins = secs // 60
                            hours = mins // 60
                            days = hours // 24

                        if days > 0:
                            tooltip = tooltip + str(days) + " days, "
                        if hours > 0:
                            tooltip = tooltip + str(hours % 24) + " hours, "
                        if mins > 0:
                            tooltip = tooltip + str(mins % 60) + " minutes, "
                        if secs > 0:
                            tooltip = tooltip + str(secs % 60) + " seconds"
                    elif key == "LastPlayed" and isinstance(value, nbtlib.tag.Long):
                        lastPlayed = value
                        timestamp = lastPlayed // 1000
                        # Convert the timestamp to a datetime object
                        date_time = datetime.datetime.fromtimestamp(timestamp)

                        # Format the datetime object using strftime
                        tooltip = date_time.strftime("%B %d, %Y, %I:%M%p")
                        timestamp = lastPlayed//1000
                    
                    elif key == "DayTime" and isinstance(value, nbtlib.tag.Long):
                        dayTime = value

                        if dayTime >= 0:
                            actualDayTime = dayTime % 24000
                            realHour = (actualDayTime // 1000) + 6
                            ampm = "AM"

                            if realHour >= 24:
                                realHour = realHour - 24

                            if realHour >= 12:
                                ampm = "PM"
                                realHour = realHour - 12

                            if realHour == 0:
                                realHour = 12

                            if actualDayTime > 3000 and actualDayTime <= 9000:
                                tooltip = "Noon " + str(realHour) + ampm
                            elif actualDayTime > 9000 and actualDayTime <= 15000:
                                tooltip = "Sunset " + str(realHour) + ampm
                            elif actualDayTime > 15000 and actualDayTime <= 21000:
                                tooltip = "Midnight " + str(realHour) + ampm
                            elif actualDayTime > 21000 or actualDayTime <= 3000:
                                tooltip = "Sunrise " + str(realHour) + ampm

                    if tooltip.strip() != "":
                        child.setText(0, f"{key}: {value} - {tooltip}")
                    else:
                        child.setText(0, f"{key}: {value}")
                    # To here is the beutiful naming convention!!!!
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
