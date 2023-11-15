import Manager
import RandoCore
import MapHelper
import MapViewer
import LunaNights
import WonderLab

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

import json
import configparser
import sys
import random
import os
import shutil
import requests
import zipfile
import subprocess

#Get script name

script_name, script_extension = os.path.splitext(os.path.basename(__file__))

#Config

config = configparser.ConfigParser()
config.optionxform = str
config.read("Data\\config.ini")

#Functions

def writing():
    with open("Data\\config.ini", "w") as file_writer:
        config.write(file_writer)
    sys.exit()

#Threads

class Signaller(QObject):
    progress = Signal(int)
    finished = Signal()

class Update(QThread):
    def __init__(self, progressBar, api):
        QThread.__init__(self)
        self.signaller = Signaller()
        self.progressBar = progressBar
        self.api = api

    def run(self):
        progress = 0
        zip_name = "Ladybug Randomizer.zip"
        exe_name = script_name + ".exe"
        self.signaller.progress.emit(progress)
        
        #Download
        
        with open(zip_name, "wb") as file_writer:
            url = requests.get(self.api["assets"][0]["browser_download_url"], stream=True)
            for data in url.iter_content(chunk_size=4096):
                file_writer.write(data)
                progress += len(data)
                self.signaller.progress.emit(progress)
        
        self.progressBar.setLabelText("Extracting...")
        
        #Purge folders
        
        shutil.rmtree("Data")
        
        os.rename(exe_name, "delete.me")
        with zipfile.ZipFile(zip_name, "r") as zip_ref:
            zip_ref.extractall("")
        os.remove(zip_name)
        
        #Carry previous config
        
        new_config = configparser.ConfigParser()
        new_config.optionxform = str
        new_config.read("Data\\config.ini")
        for each_section in new_config.sections():
            for (each_key, each_val) in new_config.items(each_section):
                if each_key == "sVersion":
                    continue
                try:
                    new_config.set(each_section, each_key, config.get(each_section, each_key))
                except (configparser.NoSectionError, configparser.NoOptionError):
                    continue
        with open("Data\\config.ini", "w") as file_writer:
            new_config.write(file_writer)
        
        #Exit
        
        subprocess.Popen(exe_name)
        self.signaller.finished.emit()

#Interface

class DropFolder(QObject):    
    def eventFilter(self, watched, event):
        if event.type() == QEvent.DragEnter:
            md = event.mimeData()
            if md.hasUrls():
                if len(md.urls()) == 1:
                    if not "." in md.urls()[0].toLocalFile():
                        event.accept()
        if event.type() == QEvent.Drop:
            md = event.mimeData()
            watched.setText(md.urls()[0].toLocalFile().replace("/", "\\"))
            return True
        return super().eventFilter(watched, event)

class Main(QWidget):
    def __init__(self):
        super().__init__()
        self.setEnabled(False)
        self.initUI()
        self.check_for_updates()

    def initUI(self):
        
        #Main layout
        
        main_vbox = QVBoxLayout()
        main_vbox.setSpacing(10)

        #Groupboxes

        box_1_grid = QGridLayout()
        self.box_1 = QGroupBox("Randomize")
        self.box_1.setLayout(box_1_grid)
        main_vbox.addWidget(self.box_1)

        box_2_grid = QGridLayout()
        self.box_2 = QGroupBox("Game")
        self.box_2.setLayout(box_2_grid)
        main_vbox.addWidget(self.box_2)
        
        #Checkboxes

        self.check_box_1 = QCheckBox("Key Items")
        self.check_box_1.setToolTip("Include progression items in the item pool.")
        self.check_box_1.stateChanged.connect(self.check_box_1_changed)
        box_1_grid.addWidget(self.check_box_1, 0, 0)

        self.check_box_2 = QCheckBox("Upgrades")
        self.check_box_2.setToolTip("Include stat upgrades in the item pool.")
        self.check_box_2.stateChanged.connect(self.check_box_2_changed)
        box_1_grid.addWidget(self.check_box_2, 1, 0)

        self.check_box_3 = QCheckBox("Spells")
        self.check_box_3.setToolTip("Include spell pickups in the item pool.")
        self.check_box_3.stateChanged.connect(self.check_box_3_changed)
        box_1_grid.addWidget(self.check_box_3, 2, 0)

        self.check_box_4 = QCheckBox("Jewels")
        self.check_box_4.setToolTip("Include breakable jewel towers in the item pool.")
        self.check_box_4.stateChanged.connect(self.check_box_4_changed)
        box_1_grid.addWidget(self.check_box_4, 3, 0)

        self.check_box_5 = QCheckBox("Weapons")
        self.check_box_5.setToolTip("Include weapons and bows in the item pool.")
        self.check_box_5.stateChanged.connect(self.check_box_5_changed)
        box_1_grid.addWidget(self.check_box_5, 3, 0)
        
        self.check_box_6 = QCheckBox("Enemy Types")
        self.check_box_6.setToolTip("Shuffle enemies by type.")
        self.check_box_6.stateChanged.connect(self.check_box_6_changed)
        box_1_grid.addWidget(self.check_box_6, 4, 0)
        
        #SpinButtons
        
        self.spin_button_1 = QPushButton()
        self.spin_button_1.setToolTip("Logic complexity. Higher values usually follow a\nprogression chain.")
        self.spin_button_1.setStyleSheet("QPushButton{color: #ffffff; font-family: Impact}" + "QToolTip{color: #ffffff; font-family: Cambria}")
        self.spin_button_1.setFixedSize(28, 24)
        self.spin_button_1.clicked.connect(self.spin_button_1_clicked)
        self.spin_button_1.setVisible(False)
        box_1_grid.addWidget(self.spin_button_1, 0, 1)
        
        self.spin_button_2 = QPushButton()
        self.spin_button_2.setToolTip("Enemy type weight. The higher the value the wider\nthe range of possible enemy types.")
        self.spin_button_2.setStyleSheet("QPushButton{color: #ffffff; font-family: Impact}" + "QToolTip{color: #ffffff; font-family: Cambria}")
        self.spin_button_2.setFixedSize(28, 24)
        self.spin_button_2.clicked.connect(self.spin_button_2_clicked)
        self.spin_button_2.setVisible(False)
        box_1_grid.addWidget(self.spin_button_2, 4, 1)
        
        #Radio buttons
        
        self.radio_button_1 = QRadioButton("Luna Nights")
        self.radio_button_1.toggled.connect(self.radio_button_group_1_checked)
        box_2_grid.addWidget(self.radio_button_1, 0, 0)
        
        self.radio_button_2 = QRadioButton("Wonder Labyrinth")
        self.radio_button_2.toggled.connect(self.radio_button_group_1_checked)
        box_2_grid.addWidget(self.radio_button_2, 1, 0)
        
        #Seed
        
        self.seed_layout = QGridLayout()
        
        self.seed_field = QLineEdit(config.get("Misc", "sSeed"))
        self.seed_field.setStyleSheet("color: #ffffff")
        self.seed_field.setMaxLength(30)
        self.seed_field.textChanged[str].connect(self.new_seed)
        self.seed_layout.addWidget(self.seed_field, 0, 0, 1, 2)
        
        seed_button_1 = QPushButton("New Seed")
        seed_button_1.clicked.connect(self.seed_button_1_clicked)
        self.seed_layout.addWidget(seed_button_1, 1, 0, 1, 1)
        
        seed_button_2 = QPushButton("Confirm")
        seed_button_2.clicked.connect(self.seed_button_2_clicked)
        self.seed_layout.addWidget(seed_button_2, 1, 1, 1, 1)
        
        #Init checkboxes
        
        self.check_box_1.setChecked(config.getboolean("Randomize", "bKeyItems"))
        self.check_box_2.setChecked(config.getboolean("Randomize", "bUpgrades"))
        self.check_box_3.setChecked(config.getboolean("Randomize", "bSpells"))
        self.check_box_4.setChecked(config.getboolean("Randomize", "bJewels"))
        self.check_box_5.setChecked(config.getboolean("Randomize", "bWeapons"))
        self.check_box_6.setChecked(config.getboolean("Randomize", "bEnemyTypes"))
        
        self.spin_button_1_set_index(config.getint("Randomize", "iLogicComplexity"))
        self.spin_button_2_set_index(config.getint("Randomize", "iEnemyTypesWeight"))
        
        #Text field
        
        output_hbox = QHBoxLayout()
        
        self.output_field = QLineEdit()
        self.output_field.setPlaceholderText("Game Directory")
        self.output_field.textChanged[str].connect(self.new_output)
        self.output_field.installEventFilter(DropFolder(self))
        output_hbox.addWidget(self.output_field)
        
        browse_button = QPushButton()
        browse_button.setIcon(QPixmap("Data\\browse.png"))
        browse_button.clicked.connect(self.browse_button_clicked)
        output_hbox.addWidget(browse_button)
        
        main_vbox.addLayout(output_hbox)

        #Buttons
        
        button_hbox = QHBoxLayout()
        
        button_1 = QPushButton("Randomize")
        button_1.setToolTip("Randomize game with current settings.")
        button_1.clicked.connect(self.button_1_clicked)
        button_hbox.addWidget(button_1)
        
        button_2 = QPushButton("Restore Vanilla")
        button_2.setToolTip("Revert game directory back to vanilla.")
        button_2.clicked.connect(self.button_2_clicked)
        button_hbox.addWidget(button_2)
        
        button_3 = QPushButton("Load Spoilers")
        button_3.setToolTip("Display solution from a spoiler log.")
        button_3.clicked.connect(self.button_3_clicked)
        button_hbox.addWidget(button_3)
        
        main_vbox.addLayout(button_hbox)
        
        #Window
        
        self.setLayout(main_vbox)
        self.setFixedSize(516, 448)
        self.setWindowTitle(script_name)
        self.setWindowIcon(QIcon("Data\\icon.png"))
        self.show()
        
        self.radio_button_1.setChecked(config.getboolean("Game", "bLunaNights"))
        self.radio_button_2.setChecked(config.getboolean("Game", "bWonderLab"))
        
        #Position
        
        center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
        geo = self.frameGeometry()
        geo.moveCenter(center)
        self.move(geo.topLeft())
        
        QApplication.processEvents()

    def check_box_1_changed(self):
        checked = self.check_box_1.isChecked()
        config.set("Randomize", "bKeyItems", str(checked).lower())
        self.spin_button_1.setVisible(checked)

    def check_box_2_changed(self):
        checked = self.check_box_2.isChecked()
        config.set("Randomize", "bUpgrades", str(checked).lower())

    def check_box_3_changed(self):
        checked = self.check_box_3.isChecked()
        config.set("Randomize", "bSpells", str(checked).lower())

    def check_box_4_changed(self):
        checked = self.check_box_4.isChecked()
        config.set("Randomize", "bJewels", str(checked).lower())

    def check_box_5_changed(self):
        checked = self.check_box_5.isChecked()
        config.set("Randomize", "bWeapons", str(checked).lower())

    def check_box_6_changed(self):
        checked = self.check_box_6.isChecked()
        config.set("Randomize", "bEnemyTypes", str(checked).lower())
        self.spin_button_2.setVisible(checked)

    def spin_button_1_clicked(self):
        index = int(self.spin_button_1.text())
        index = index % 3 + 1
        self.spin_button_1_set_index(index)
    
    def spin_button_1_set_index(self, index):
        self.spin_button_1.setText(str(index))
        config.set("Randomize", "iLogicComplexity", str(index))

    def spin_button_2_clicked(self):
        index = int(self.spin_button_2.text())
        index = index % 3 + 1
        self.spin_button_2_set_index(index)
    
    def spin_button_2_set_index(self, index):
        self.spin_button_2.setText(str(index))
        config.set("Randomize", "iEnemyTypesWeight", str(index))
    
    def radio_button_group_1_checked(self):
        config.set("Game", "bLunaNights", str(self.radio_button_1.isChecked()).lower())
        config.set("Game", "bWonderLab", str(self.radio_button_2.isChecked()).lower())
        self.check_box_4.setVisible(self.radio_button_1.isChecked())
        self.check_box_5.setVisible(self.radio_button_2.isChecked())
        if self.radio_button_1.isChecked():
            self.output_field.setText(config.get("Misc", "sLunaNightsGameDir"))
            self.reset_visuals("LunaNights", "#391a18", "#32ff3f33")
        if self.radio_button_2.isChecked():
            self.output_field.setText(config.get("Misc", "sWonderLabGameDir"))
            self.reset_visuals("WonderLab", "#151e30", "#323377ff")
    
    def reset_visuals(self, game, main_color, sub_color):
        self.setStyleSheet("QWidget{background:transparent; color: #ffffff; font-family: Cambria; font-size: 18px}"
        + "QLabel{border: 1px}"
        + "QMessageBox{background-color: " + main_color + "}"
        + "QDialog{background-color: " + main_color + "}"
        + "QProgressDialog{background-color: " + main_color + "}"
        + "QPushButton{background-color: " + main_color + "}"
        + "QDoubleSpinBox{background-color: " + main_color + "; selection-background-color: " + sub_color + "}"
        + "QLineEdit{background-color: " + main_color + "; selection-background-color: " + sub_color + "}"
        + "QProgressBar{border: 2px solid white; text-align: center; font: bold}"
        + "QToolTip{border: 0px; background-color: " + main_color + "; color: #ffffff; font-family: Cambria; font-size: 18px}")
        background = QPixmap("Data\\" + game + "\\background.png")
        palette = QPalette()
        palette.setBrush(QPalette.Window, background)
        self.setPalette(palette)
    
    def new_output(self, output):
        if config.getboolean("Game", "bLunaNights"):
            config.set("Misc", "sLunaNightsGameDir", output)
        if config.getboolean("Game", "bWonderLab"):
            config.set("Misc", "sWonderLabGameDir", output)
    
    def new_seed(self, text):
        if " " in text:
            self.seed_field.setText(text.replace(" ", ""))
        else:
            config.set("Misc", "sSeed", text)
    
    def set_progress(self, progress):
        self.progressBar.setValue(progress)
    
    def update_finished(self):
        sys.exit()

    def button_1_clicked(self):
        
        #Determine game
        if config.getboolean("Game", "bLunaNights"):
            Manager.init(LunaNights)
        else:
            Manager.init(WonderLab)
        
        game_path = config.get("Misc", "s" + Manager.game_name + "GameDir")
        
        #Check path
        if not os.path.isdir(game_path):
            self.no_path()
            return
        
        #Seed prompt
        self.seed = ""
        self.seed_box = QDialog(self)
        self.seed_box.setLayout(self.seed_layout)
        self.seed_box.setWindowTitle("Seed")
        self.seed_box.exec()
        if not self.seed:
            return
        
        self.setEnabled(False)
        QApplication.processEvents()
        
        #Step 1
        try:
            #Backup files
            if os.path.isfile(game_path + "\\data.bak"):
                shutil.copyfile(game_path + "\\data.bak", game_path + "\\data.win")
            else:
                shutil.copyfile(game_path + "\\data.win", game_path + "\\data.bak")
            
            if os.path.isfile(game_path + "\\data\\dial_e.bak"):
                shutil.copyfile(game_path + "\\data\\dial_e.bak", game_path + "\\data\\dial_e.txt")
            else:
                shutil.copyfile(game_path + "\\data\\dial_e.txt", game_path + "\\data\\dial_e.bak")
            
            #Appy patches
            if config.getboolean("Randomize", "bKeyItems"):
                Manager.apply_xdelta_patch(game_path + "\\data.win", Manager.game_name + "\\ability.xdelta")
            
            #Init
            Manager.game.init()
            Manager.load_constant()
            
        except Exception:
            self.abort_process("An error has occured.\nCheck the command window for more detail.")
            raise
        
        #Step 2
        try:
            #Open game
            Manager.open_game_data(game_path)
            Manager.read_game_data()
            
            #Apply changes
            Manager.game.apply_default_tweaks()
            
            RandoCore.init()
            RandoCore.categorize_items()
            RandoCore.set_logic_complexity(config.getint("Randomize", "iLogicComplexity"))
            RandoCore.set_enemy_type_wheight(config.getint("Randomize", "iEnemyTypesWeight"))
            
            MapHelper.init()
            
            if config.getboolean("Randomize", "bKeyItems"):
                RandoCore.add_item_type("Key")
                if not config.getboolean("Randomize", "bUpgrades") and not config.getboolean("Randomize", "bSpells") and config.getboolean("Randomize", "bJewels"):
                    RandoCore.remove_ice_magatama()
            
            if config.getboolean("Randomize", "bUpgrades"):
                RandoCore.add_item_type("Upgrade")
            
            if config.getboolean("Randomize", "bSpells"):
                RandoCore.add_item_type("Spell")
            
            if config.getboolean("Randomize", "bJewels"):
                RandoCore.add_item_type("Jewel")
            
            if config.getboolean("Randomize", "bWeapons"):
                RandoCore.add_item_type("Weapon")
            
            if config.getboolean("Randomize", "bKeyItems"):
                random.seed(self.seed)
                MapHelper.get_map_info()
                try:
                    RandoCore.process_key_logic()
                except RuntimeError:
                    Manager.close_game_data(game_path)
                    self.abort_process("Failed to generate seed.\nItem pool too restricted.")
                    return
                RandoCore.write_spoiler_log(self.seed)
                Manager.game.fix_progression_obstacles()
                Manager.game.update_ability_description()
                if os.path.isdir("Data\\" + Manager.game_name + "\\TileMap"):
                    for file in os.listdir("Data\\" + Manager.game_name + "\\TileMap"):
                        Manager.import_tilemap("Data\\" + Manager.game_name + "\\TileMap\\" + file)
            
            random.seed(self.seed)
            RandoCore.randomize_items()
            
            if config.getboolean("Randomize", "bEnemyTypes"):
                random.seed(self.seed)
                RandoCore.randomize_enemies()
            
            #Close game
            Manager.write_game_data()
            Manager.close_game_data(game_path)
            
        except Exception:
            Manager.close_game_data(game_path)
            self.abort_process("An error has occured.\nCheck the command window for more detail.")
            raise
        
        self.setEnabled(True)
        box = QMessageBox(self)
        box.setWindowTitle("Message")
        box.setText("Game randomized !")
        box.exec()
    
    def abort_process(self, message):
        self.setEnabled(True)
        box = QMessageBox(self)
        box.setWindowTitle("Error")
        box.setIcon(QMessageBox.Critical)
        box.setText(message)
        box.exec()
    
    def button_2_clicked(self):
        
        #Determine game
        if config.getboolean("Game", "bLunaNights"):
            Manager.init(LunaNights)
        else:
            Manager.init(WonderLab)
        
        game_path = config.get("Misc", "s" + Manager.game_name + "GameDir")
        
        #Check path
        if not os.path.isdir(game_path):
            self.no_path()
            return
        
        self.setEnabled(False)
        QApplication.processEvents()
        
        #Restore files
        try:
            if os.path.isfile(game_path + "\\data.bak"):
                os.remove(game_path + "\\data.win")
                os.rename(game_path + "\\data.bak", game_path + "\\data.win")
            if os.path.isfile(game_path + "\\data\\dial_e.bak"):
                os.remove(game_path + "\\data\\dial_e.txt")
                os.rename(game_path + "\\data\\dial_e.bak", game_path + "\\data\\dial_e.txt")
        except Exception:
            self.abort_process()
        
        box = QMessageBox(self)
        box.setWindowTitle("Message")
        box.setText("Game directory reverted back to vanilla !")
        box.exec()
        self.setEnabled(True)
    
    def button_3_clicked(self):
        file = QFileDialog.getOpenFileName(parent=self, caption="File", filter="*.json")[0].replace("/", "\\")
        if file:
            name, extension = os.path.splitext(file)
            filename = name.split("\\")[-1]
            with open(file, "r", encoding="utf8") as file_reader:
                spoiler = json.load(file_reader)
            
            #Determine game
            if config.getboolean("Game", "bLunaNights"):
                Manager.init(LunaNights)
            else:
                Manager.init(WonderLab)
            
            #Check game
            if Manager.game_name != filename.split(" - ")[0]:
                box = QMessageBox(self)
                box.setWindowTitle("Warning")
                box.setIcon(QMessageBox.Critical)
                box.setText("Game mismatch !")
                box.exec()
                return
            
            Manager.game.init()
            Manager.load_constant()
            
            MapHelper.init()
            MapHelper.get_map_info()
            MapHelper.fill_check_to_room()
            
            self.map_viewer = MapViewer.MainWindow(filename.split(" - ")[1], spoiler)
    
    def browse_button_clicked(self):
        path = QFileDialog.getExistingDirectory(self, "Folder").replace("/", "\\")
        if path:
            self.output_field.setText(path)
    
    def seed_button_1_clicked(self):
        self.seed_field.setText(str(random.randint(1000000000, 9999999999)))
    
    def seed_button_2_clicked(self):
        self.seed = config.get("Misc", "sSeed")
        if not self.seed:
            return
        #Cast seed to another object type if possible
        try:
            if "." in self.seed:
                self.seed = float(self.seed)
            else:
                self.seed = int(self.seed)
        except ValueError:
            pass
        self.seed_box.close()
    
    def no_path(self):
        box = QMessageBox(self)
        box.setWindowTitle("Warning")
        box.setIcon(QMessageBox.Critical)
        box.setText("Input path invalid.")
        box.exec()
    
    def check_for_updates(self):
        if os.path.isfile("delete.me"):
            os.remove("delete.me")
        try:
            api = requests.get("https://api.github.com/repos/Lakifume/Ladybug-Randomizer/releases/latest").json()
        except requests.ConnectionError:
            self.setEnabled(True)
            return
        try:
            tag = api["tag_name"]
        except KeyError:
            self.setEnabled(True)
            return
        if tag != config.get("Misc", "sVersion"):
            choice = QMessageBox.question(self, "Auto Updater", "New version found:\n\n" + api["body"] + "\n\nUpdate ?", QMessageBox.Yes | QMessageBox.No)
            if choice == QMessageBox.Yes:
                self.progressBar = QProgressDialog("Downloading...", None, 0, api["assets"][0]["size"], self)
                self.progressBar.setWindowTitle("Status")
                self.progressBar.setWindowModality(Qt.WindowModal)
                self.progressBar.setAutoClose(False)
                self.progressBar.setAutoReset(False)
                
                self.worker = Update(self.progressBar, api)
                self.worker.signaller.progress.connect(self.set_progress)
                self.worker.signaller.finished.connect(self.update_finished)
                self.worker.start()
            else:
                self.setEnabled(True)
        else:
            self.setEnabled(True)

def main():
    app = QApplication(sys.argv)
    app.aboutToQuit.connect(writing)
    main = Main()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()