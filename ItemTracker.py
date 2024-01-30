import Manager

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

import os
import glob
import time

WIDTH = 4

class MainWindow(QWidget):
    def __init__(self, save_file_path):
        super().__init__()
        self.save_file_path = save_file_path
        self.init()
    
    def init(self):
        self.setStyleSheet("QWidget{background: transparent; color: #ffffff; font-family: Cambria; font-size: 18px}" + "QPushButton{background-color: #1a1a1a}")
        
        #Main layout
        
        main_vbox = QVBoxLayout()
        main_vbox.setSpacing(10)
        item_grid = QGridLayout()
        
        #Labels
        
        self.item_to_label_opacity = {}
        count = 0
        for item in Manager.game.tracker_to_save_watch:
            item_label = QLabel()
            item_label.setPixmap(QPixmap(f"Data\\{Manager.game_name}\\TrackerIcon\\{item}.png"))
            opacity_effect = QGraphicsOpacityEffect()
            opacity_effect.setOpacity(1)
            item_label.setGraphicsEffect(opacity_effect)
            item_grid.addWidget(item_label, count//WIDTH, count%WIDTH)
            self.item_to_label_opacity[item] = opacity_effect
            count += 1
        
        status_hbox = QHBoxLayout()
        self.status_image = QLabel()
        self.status_image.setPixmap(QPixmap("Data\\tracker_end.png"))
        self.status_label = QLabel()
        self.status_label.setStyleSheet("font-weight: bold; font-size: 8px")
        status_hbox.addWidget(self.status_image)
        status_hbox.addWidget(self.status_label)
        status_hbox.addStretch(1)
        
        #Buttons
        
        self.warp_button = QPushButton("Warp To Start")
        self.warp_button.clicked.connect(self.warp_button_clicked)
        
        #Layouts
        
        main_vbox.addLayout(item_grid)
        main_vbox.addWidget(self.warp_button)
        main_vbox.addLayout(status_hbox)
        
        #Window
        
        self.setLayout(main_vbox)
        self.setFixedSize(0, 0)
        self.setWindowTitle(" ")
        self.setWindowIcon(QIcon("Data\\icon.png"))
        self.show()
        
        #Watcher
        
        self.watcher = QFileSystemWatcher(self)
        self.watcher.fileChanged.connect(self.save_changed)
        self.set_watcher_enabled(True)
        self.save_changed(self.save_file_path)
    
    def set_tracker_status(self, is_ready, message):
        self.set_watcher_enabled(is_ready)
        self.warp_button.setEnabled(is_ready)
        status = "str" if is_ready else "end"
        self.status_image.setPixmap(QPixmap(f"Data\\tracker_{status}.png"))
        self.status_label.setText(message.upper())
        QApplication.processEvents()
    
    def set_watcher_enabled(self, enabled):
        if not enabled:
            self.watcher.removePath(self.save_file_path)
        elif not self.save_file_path in self.watcher.files():
            self.watcher.addPath(self.save_file_path)
    
    def save_changed(self, file_path):
        self.set_tracker_status(False, "Updating...")
        time.sleep(0.5)
        if not os.path.isfile(file_path):
            self.set_tracker_status(False, "Save deleted, aborting...")
            time.sleep(2.5)
            self.close()
            return
        with open(file_path, "r", encoding="utf8") as file_reader:
            save_data = file_reader.readlines()
        Manager.read_save_data(save_data)
        self.update_tracker_icons()
        self.set_tracker_status(True, "Ready")
    
    def update_tracker_icons(self):
        for item in self.item_to_label_opacity:
            opacity = self.item_to_label_opacity[item]
            save_entry = Manager.game.tracker_to_save_watch[item]
            save_value = Manager.game_save[save_entry]
            match save_entry:
                case "iSpecialMode":
                    ability_value = Manager.game_save["iAbilityIndex"]
                    ability_index = Manager.game.ability_order.index(item)
                    is_obtained = ability_index < ability_value or save_value == 1
                case "iAbilityIndex":
                    ability_index = Manager.game.ability_order.index(item)
                    is_obtained = ability_index < save_value
                case "iCurrentBow":
                    is_obtained = bool(save_value + 1)
                case _:
                    is_obtained = bool(save_value)
            opacity.setOpacity(1.0 if is_obtained else 0.25)
    
    def warp_button_clicked(self):
        self.set_tracker_status(False, "Overwriting save...")
        save_info_path = f"{os.path.splitext(self.save_file_path)[0]}.txt"
        with open(save_info_path, "r", encoding="utf8") as file_reader:
            save_info = file_reader.readlines()
        with open(self.save_file_path, "r", encoding="utf8") as file_reader:
            save_data = file_reader.readlines()
        Manager.read_save_data(save_data)
        if self.is_post_beld_save_point():
            self.set_tracker_status(False, "Nice try")
            time.sleep(2.5)
            self.set_tracker_status(True, "Ready")
            return
        Manager.game_save["iSpawnPosX"]  = int(save_info[0])
        Manager.game_save["iSpawnPosY"]  = int(save_info[1])
        Manager.game_save["iSpawnStage"] = int(save_info[2])
        Manager.write_save_data(save_data)
        with open(self.save_file_path, "w", encoding="utf8") as file_writer:
            file_writer.writelines(save_data)
        self.set_tracker_status(False, "Done, reload your game save")
        time.sleep(5.0)
        self.set_tracker_status(True, "Ready")
    
    def is_post_beld_save_point(self):
        position = (Manager.game_save["iSpawnPosX"], Manager.game_save["iSpawnPosY"], Manager.game_save["iSpawnStage"])
        return position in [(8640, 3168, 9), (9280, 1024, 9)]