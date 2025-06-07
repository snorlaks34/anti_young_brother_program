import os
from random import randint, random
from time import sleep

import psutil
import sys
import json
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon, QShortcut, QKeySequence, QAction
from PyQt6.QtWidgets import QWidget, QApplication, QVBoxLayout, QPushButton, QHBoxLayout, QLabel, QLineEdit, \
    QFormLayout, QComboBox, QDoubleSpinBox, QSystemTrayIcon, QMenu, QListWidget

path_to_icon=""
class Main_window(QWidget):
    def __init__(self):
        super().__init__()
        self.toggled="" #when true app is on, when off app is off
        self.appilactions=[]
        self.min_time = 0
        self.max_time = 0
        self.setGeometry(300,300,500,500)
        self.load_from_json()
        self.tray_handle()
        self.initializeUI()
        self.add_items_to_list()
        self.change_text()

    # do all shit requested to tray
    def tray_handle(self):
        menu = QMenu()
        open_window_action=QAction("Open window",self)
        open_window_action.triggered.connect(self.stealth)
        menu.addAction(open_window_action)

        self.tray = QSystemTrayIcon(self)

        path_to_icon=self.resource_path("favicon.ico")
        self.tray.setIcon(QIcon(path_to_icon))
        self.tray.setContextMenu(menu)
        self.tray.setVisible(True)

    def style(self):

        stylesheet="""
            
            """

        app.setStyleSheet(stylesheet)

    def initializeUI(self):

        Main_V_layout=QVBoxLayout()
        button_H_layout=QHBoxLayout()


        self.timer = QTimer()
        self.timer.timeout.connect(self.main_function)
        self.timer.start(2000)

        shortcut = QShortcut(QKeySequence("Ctrl+F12"), self)
        shortcut.setContext(Qt.ShortcutContext.ApplicationShortcut)
        shortcut.activated.connect(self.stealth)

        shortcut1 = QShortcut(QKeySequence(Qt.Key.Key_Return), self)
        shortcut1.setContext(Qt.ShortcutContext.ApplicationShortcut)
        shortcut1.activated.connect(self.handle_inputs)

        form_layout=QFormLayout()
        self.switch=QPushButton("ON/OFF")
        self.switch.clicked.connect(self.change_toggled)
        self.switch.clicked.connect(self.change_text)
        self.switch_label=QLabel("ON")

        application_input_label=QLabel("Add new aplication for ban:")
        self.application_input=QLineEdit()
        self.application_input.setPlaceholderText("Notepad.exe")

        application_delete_label = QLabel("Delete from list of the banned apps")
        self.delete_application_list=QComboBox()
        self.delete_application_list.activated[int].connect(self.delete_item_from_array)

        timer_min_label=QLabel("Set minimum time before shutdown the app")
        self.timer_min=QDoubleSpinBox()
        self.timer_min.setRange(10,999)
        self.timer_min.setValue(10)
        self.timer_min.setDecimals(0)

        timer_max_label = QLabel("Set maximum time before shutdown the app")
        self.timer_max = QDoubleSpinBox()
        self.timer_max.setRange(10, 1000)
        self.timer_max.setValue(1000)
        self.timer_max.setDecimals(0)


        send_button=QPushButton("Send new parameters")
        send_button.clicked.connect(self.handle_inputs)

        form_layout.addRow(application_input_label,self.application_input)
        form_layout.addRow(application_delete_label, self.delete_application_list)
        form_layout.addRow(timer_min_label,self.timer_min)
        form_layout.addRow(timer_max_label,self.timer_max)

        button_H_layout.addWidget(self.switch, alignment=Qt.AlignmentFlag.AlignHCenter)
        button_H_layout.addWidget(self.switch_label, alignment=Qt.AlignmentFlag.AlignHCenter)


        Main_V_layout.addLayout(form_layout)
        Main_V_layout.addLayout(button_H_layout)
        Main_V_layout.addWidget(send_button,alignment=Qt.AlignmentFlag.AlignCenter)
        Main_V_layout.addStretch()
        self.setLayout(Main_V_layout)

    def change_toggled(self):
        if self.toggled:
            self.toggled=False
            self.switch_label.setText("OFF")
        else:
            self.toggled = True
            self.switch_label.setText("ON")
        self.save_to_json()

    def change_text(self):
        if self.toggled:
            self.switch_label.setText("ON")
        else:
            self.switch_label.setText("OFF")

    def handle_inputs(self):

        self.load_from_json()
        self.min_time=self.timer_min.text()
        self.max_time=self.timer_max.text()
        if self.application_input.text()!="": self.appilactions.append(self.application_input.text().lower())

        self.save_to_json()
        self.add_items_to_list()

    #get path to json
    def resource_path(self,relative_path):

        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

    def save_to_json(self):
        try:
            path=self.resource_path("settings.json")
            with open(path,"w",encoding="UTF-8") as file:
                x={
                    "ON/OFF": self.toggled,
                    "Appilactions": self.appilactions,
                    "Min_Time": self.min_time,
                    "Max_Time": self.max_time
                }
                json.dump(x,file,indent=4,ensure_ascii=False)
        except FileNotFoundError as e:
            print(f"File not found {e}")

    def load_from_json(self):
        try:
            path = self.resource_path("settings.json")
            with open(path, "r", encoding="UTF-8") as file:
                x=json.load(file)
                self.toggled=x["ON/OFF"]
                self.min_time=x["Min_Time"]
                self.max_time=x["Max_Time"]
                self.appilactions=x["Appilactions"]

        except FileNotFoundError as e:
            print(f"File not found {e}")

    #change between hide and show
    def stealth(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()

    # main function that shut down applications
    def main_function(self):
        if self.toggled:
            # killing process
            def kill_process_by_name(p):
                try:
                    p.kill()
                    self.timer.start(2000)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    print(f"unsucceded we didn't kill it")

            # check if process is running
            def is_process_running():
                #good info watch on size of cases
                for proc in psutil.process_iter(['name']):
                    if proc.info['name'].lower() in self.appilactions:
                        rand_time = randint(int(self.min_time),int(self.max_time))
                        self.timer.stop()
                        QTimer.singleShot(rand_time*1000,lambda p=proc: kill_process_by_name(p))

                return False

            is_process_running()

    #add and delete items from combobox
    def add_items_to_list(self):
        self.load_from_json()
        if self.delete_application_list.count()==0:
            self.delete_application_list.addItems(self.appilactions)
        else:
            self.delete_application_list.clear()
            self.delete_application_list.addItems(self.appilactions)

    #delete items from list and array
    def delete_item_from_array(self,index):
        text=self.delete_application_list.itemText(index)
        if text != self.appilactions[0]:
            self.appilactions.remove(text)
            self.delete_application_list.removeItem(index)
            self.save_to_json()


if __name__ == '__main__':

    app = QApplication(sys.argv)
    Window = Main_window()
    app.setWindowIcon(QIcon("path_to_icon"))
    Window.setWindowIcon(QIcon("path_to_icon"))
    sys.exit(app.exec())




