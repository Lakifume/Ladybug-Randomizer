import Manager
import Gameplay
import Cosmetic
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

#variables

game_to_visuals = {
    "LunaNights": ("#391a18", "#32ff3f33"),
    "WonderLab":  ("#151e30", "#323377ff")
}

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
    error    = Signal(str)

class Generate(QThread):
    def __init__(self, progress_bar, seed, path):
        QThread.__init__(self)
        self.signaller = Signaller()
        self.progress_bar = progress_bar
        self.seed = seed
        self.path = path
    
    def run(self):
        try:
            self.process()
        except Gameplay.CompletionError:
            self.signaller.error.emit("Failed to generate seed.\nItem pool too restricted.")
        except Exception:
            self.signaller.error.emit("An error has occured.\nCheck the command window for more detail.")
            raise

    def process(self):
        current = 0
        self.signaller.progress.emit(current)
        
        #Backup files
        if os.path.isfile(self.path + "\\data.bak"):
            shutil.copyfile(self.path + "\\data.bak", self.path + "\\data.win")
        else:
            shutil.copyfile(self.path + "\\data.win", self.path + "\\data.bak")
        
        if os.path.isdir(self.path + "\\backup"):
            shutil.rmtree(self.path + "\\data")
            shutil.copytree(self.path + "\\backup", self.path + "\\data")
        else:
            shutil.copytree(self.path + "\\data", self.path + "\\backup")
        
        #Init
        Gameplay.init()
        Cosmetic.init()
        MapHelper.init()
        Manager.game.init()
        Manager.load_constant()
        
        current += 1
        self.signaller.progress.emit(current)
        self.progress_bar.setLabelText("Unpacking data...")
        
        Manager.unpack_game_data(self.path)
        Manager.read_game_data()
        
        current += 1
        self.signaller.progress.emit(current)
        self.progress_bar.setLabelText("Applying tweaks...")
        
        Manager.game.apply_default_tweaks()
        Manager.convert_tilemaps_to_patches()
        
        if config.getboolean("Gameplay", "bKeyItems"):
            Manager.game.apply_key_logic_tweaks()
            Manager.game.apply_progressive_ability_tweaks()
        
        if config.getboolean("Cosmetic", "bWorldColors"):
            Manager.game.apply_world_color_rando_tweaks()
        
        if config.getboolean("Cosmetic", "bEnemyColors"):
            Manager.game.apply_enemy_color_rando_tweaks()
        
        if config.getboolean("Cosmetic", "bCharacterColors"):
            Manager.game.apply_chara_color_rando_tweaks()
        
        if Manager.game == LunaNights and random.random() < 1/8:
            LunaNights.swap_skeleton_sprites()
        
        if Manager.game == WonderLab and config.getboolean("Extra", "bSkipBossRush"):
            WonderLab.skip_boss_rush()
        
        current += 1
        self.signaller.progress.emit(current)
        self.progress_bar.setLabelText("Randomizing items...")
        
        Gameplay.categorize_items()
        Gameplay.set_logic_complexity(config.getint("Gameplay", "iLogicComplexity"))
        Gameplay.set_enemy_type_wheight(config.getint("Gameplay", "iEnemyTypesWeight"))
        Gameplay.set_room_logic(config.getboolean("Extra", "bSpeedrunLogic"))
        
        if config.getboolean("Gameplay", "bKeyItems"):
            Gameplay.add_item_type("Key")
            if Manager.game == LunaNights and not config.getboolean("Gameplay", "bUpgrades") and not config.getboolean("Gameplay", "bSpells") and config.getboolean("Gameplay", "bJewels"):
                Gameplay.remove_hardcoded_items()
            MapHelper.get_map_info()
        
        if config.getboolean("Gameplay", "bUpgrades"):
            Gameplay.add_item_type("Upgrade")
        
        if config.getboolean("Gameplay", "bSpells"):
            Gameplay.add_item_type("Spell")
        
        if config.getboolean("Gameplay", "bJewels"):
            Gameplay.add_item_type("Jewel")
        
        if config.getboolean("Gameplay", "bWeapons"):
            Gameplay.add_item_type("Weapon")
        
        if config.getboolean("Gameplay", "bKeyItems"):
            random.seed(self.seed)
            Gameplay.process_key_logic()
            Gameplay.write_spoiler_log(self.seed)
        
        random.seed(self.seed)
        Gameplay.randomize_items()
        
        if config.getboolean("Gameplay", "bEnemyTypes"):
            random.seed(self.seed)
            Gameplay.randomize_enemies()
        
        if config.getboolean("Cosmetic", "bBackgroundMusic"):
            random.seed(self.seed)
            Cosmetic.randomize_background_music(self.path)
            Cosmetic.update_music_names()
        
        current += 1
        self.signaller.progress.emit(current)
        self.progress_bar.setLabelText("Randomizing world colors...")
        
        if config.getboolean("Cosmetic", "bWorldColors"):
            random.seed(self.seed)
            Cosmetic.randomize_texture_colors("WorldTexture")
        
        current += 1
        self.signaller.progress.emit(current)
        self.progress_bar.setLabelText("Randomizing enemy colors...")
        
        if config.getboolean("Cosmetic", "bEnemyColors"):
            random.seed(self.seed)
            Cosmetic.randomize_texture_colors("EnemyTexture")
        
        current += 1
        self.signaller.progress.emit(current)
        self.progress_bar.setLabelText("Randomizing character colors...")
        
        if config.getboolean("Cosmetic", "bCharacterColors"):
            random.seed(self.seed)
            Cosmetic.randomize_texture_colors("CharacterTexture")
        
        if config.getboolean("Cosmetic", "bDialogues"):
            random.seed(self.seed)
            Cosmetic.randomize_dialogues()
        
        current += 1
        self.signaller.progress.emit(current)
        self.progress_bar.setLabelText("Repacking data...")
        
        Cosmetic.save_game_textures()
        Manager.write_game_data()
        Manager.repack_game_data(self.path)
        
        current += 1
        self.signaller.progress.emit(current)
        self.signaller.finished.emit()

class Update(QThread):
    def __init__(self, progress_bar, api):
        QThread.__init__(self)
        self.signaller = Signaller()
        self.progress_bar = progress_bar
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
        
        self.progress_bar.setLabelText("Extracting...")
        
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
        
        random_hbox = QHBoxLayout()

        box_1_grid = QGridLayout()
        self.box_1 = QGroupBox("Gameplay")
        self.box_1.setLayout(box_1_grid)
        random_hbox.addWidget(self.box_1)

        box_2_grid = QGridLayout()
        self.box_2 = QGroupBox("Cosmetic")
        self.box_2.setLayout(box_2_grid)
        random_hbox.addWidget(self.box_2)
        
        main_vbox.addLayout(random_hbox)

        box_3_grid = QGridLayout()
        self.box_3 = QGroupBox()
        self.box_3.setLayout(box_3_grid)
        main_vbox.addWidget(self.box_3)

        box_4_grid = QGridLayout()
        self.box_4 = QGroupBox()
        self.box_4.setLayout(box_4_grid)
        main_vbox.addWidget(self.box_4)
        
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

        self.check_box_7 = QCheckBox("Background Music")
        self.check_box_7.setToolTip("Shuffle music tracks by type.")
        self.check_box_7.stateChanged.connect(self.check_box_7_changed)
        box_2_grid.addWidget(self.check_box_7, 0, 0)

        self.check_box_8 = QCheckBox("World Colors")
        self.check_box_8.setToolTip("Randomize the hue of tilesets and backgrounds.")
        self.check_box_8.stateChanged.connect(self.check_box_8_changed)
        box_2_grid.addWidget(self.check_box_8, 1, 0)

        self.check_box_9 = QCheckBox("Enemy Colors")
        self.check_box_9.setToolTip("Randomize the hue of enemy sprites.")
        self.check_box_9.stateChanged.connect(self.check_box_9_changed)
        box_2_grid.addWidget(self.check_box_9, 2, 0)

        self.check_box_10 = QCheckBox("Character Colors")
        self.check_box_10.setToolTip("Randomize the hue of character sprites.")
        self.check_box_10.stateChanged.connect(self.check_box_10_changed)
        box_2_grid.addWidget(self.check_box_10, 3, 0)
        
        self.check_box_11 = QCheckBox("Dialogues")
        self.check_box_11.setToolTip("Randomize all conversation lines.")
        self.check_box_11.stateChanged.connect(self.check_box_11_changed)
        box_2_grid.addWidget(self.check_box_11, 4, 0)

        self.check_box_12 = QCheckBox("Speedrun Logic")
        self.check_box_12.setToolTip("Switch to a progression logic that may require\nspeedrun tricks, glitches and taking damage.")
        self.check_box_12.stateChanged.connect(self.check_box_12_changed)
        box_3_grid.addWidget(self.check_box_12, 0, 0)
        
        self.check_box_13 = QCheckBox("Skip Boss Rush")
        self.check_box_13.setToolTip("Allow going around the boss rush at the end of stage 6.")
        self.check_box_13.stateChanged.connect(self.check_box_13_changed)
        box_3_grid.addWidget(self.check_box_13, 1, 0)
        retain = self.check_box_13.sizePolicy()
        retain.setRetainSizeWhenHidden(True)
        self.check_box_13.setSizePolicy(retain)
        
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
        box_4_grid.addWidget(self.radio_button_1, 0, 0)
        
        self.radio_button_2 = QRadioButton("Wonder Labyrinth")
        self.radio_button_2.toggled.connect(self.radio_button_group_1_checked)
        box_4_grid.addWidget(self.radio_button_2, 1, 0)
        
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
        
        self.check_box_1.setChecked(config.getboolean("Gameplay", "bKeyItems"))
        self.check_box_2.setChecked(config.getboolean("Gameplay", "bUpgrades"))
        self.check_box_3.setChecked(config.getboolean("Gameplay", "bSpells"))
        self.check_box_4.setChecked(config.getboolean("Gameplay", "bJewels"))
        self.check_box_5.setChecked(config.getboolean("Gameplay", "bWeapons"))
        self.check_box_6.setChecked(config.getboolean("Gameplay", "bEnemyTypes"))
        
        self.check_box_7.setChecked(config.getboolean("Cosmetic", "bBackgroundMusic"))
        self.check_box_8.setChecked(config.getboolean("Cosmetic", "bWorldColors"))
        self.check_box_9.setChecked(config.getboolean("Cosmetic", "bEnemyColors"))
        self.check_box_10.setChecked(config.getboolean("Cosmetic", "bCharacterColors"))
        self.check_box_11.setChecked(config.getboolean("Cosmetic", "bDialogues"))
        
        self.check_box_12.setChecked(config.getboolean("Extra", "bSpeedrunLogic"))
        self.check_box_13.setChecked(config.getboolean("Extra", "bSkipBossRush"))
        
        self.spin_button_1_set_index(config.getint("Gameplay", "iLogicComplexity"))
        self.spin_button_2_set_index(config.getint("Gameplay", "iEnemyTypesWeight"))
        
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
        config.set("Gameplay", "bKeyItems", str(checked).lower())
        self.spin_button_1.setVisible(checked)
        self.reset_visuals()

    def check_box_2_changed(self):
        checked = self.check_box_2.isChecked()
        config.set("Gameplay", "bUpgrades", str(checked).lower())

    def check_box_3_changed(self):
        checked = self.check_box_3.isChecked()
        config.set("Gameplay", "bSpells", str(checked).lower())

    def check_box_4_changed(self):
        checked = self.check_box_4.isChecked()
        config.set("Gameplay", "bJewels", str(checked).lower())

    def check_box_5_changed(self):
        checked = self.check_box_5.isChecked()
        config.set("Gameplay", "bWeapons", str(checked).lower())

    def check_box_6_changed(self):
        checked = self.check_box_6.isChecked()
        config.set("Gameplay", "bEnemyTypes", str(checked).lower())
        self.spin_button_2.setVisible(checked)
        self.reset_visuals()

    def check_box_7_changed(self):
        checked = self.check_box_7.isChecked()
        config.set("Cosmetic", "bBackgroundMusic", str(checked).lower())

    def check_box_8_changed(self):
        checked = self.check_box_8.isChecked()
        config.set("Cosmetic", "bWorldColors", str(checked).lower())

    def check_box_9_changed(self):
        checked = self.check_box_9.isChecked()
        config.set("Cosmetic", "bEnemyColors", str(checked).lower())

    def check_box_10_changed(self):
        checked = self.check_box_10.isChecked()
        config.set("Cosmetic", "bCharacterColors", str(checked).lower())

    def check_box_11_changed(self):
        checked = self.check_box_11.isChecked()
        config.set("Cosmetic", "bDialogues", str(checked).lower())

    def check_box_12_changed(self):
        checked = self.check_box_12.isChecked()
        config.set("Extra", "bSpeedrunLogic", str(checked).lower())

    def check_box_13_changed(self):
        checked = self.check_box_13.isChecked()
        config.set("Extra", "bSkipBossRush", str(checked).lower())

    def spin_button_1_clicked(self):
        index = int(self.spin_button_1.text())
        index = index % 3 + 1
        self.spin_button_1_set_index(index)
    
    def spin_button_1_set_index(self, index):
        self.spin_button_1.setText(str(index))
        config.set("Gameplay", "iLogicComplexity", str(index))

    def spin_button_2_clicked(self):
        index = int(self.spin_button_2.text())
        index = index % 3 + 1
        self.spin_button_2_set_index(index)
    
    def spin_button_2_set_index(self, index):
        self.spin_button_2.setText(str(index))
        config.set("Gameplay", "iEnemyTypesWeight", str(index))
    
    def radio_button_group_1_checked(self):
        config.set("Game", "bLunaNights", str(self.radio_button_1.isChecked()).lower())
        config.set("Game", "bWonderLab", str(self.radio_button_2.isChecked()).lower())
        self.check_box_4.setVisible(self.radio_button_1.isChecked())
        self.check_box_5.setVisible(self.radio_button_2.isChecked())
        self.check_box_13.setVisible(self.radio_button_2.isChecked())
        if self.radio_button_1.isChecked():
            self.output_field.setText(config.get("Misc", "sLunaNightsGameDir"))
        if self.radio_button_2.isChecked():
            self.output_field.setText(config.get("Misc", "sWonderLabGameDir"))
        self.reset_visuals()
    
    def reset_visuals(self):
        #Determine game
        if config.getboolean("Game", "bLunaNights"):
            game = "LunaNights"
        if config.getboolean("Game", "bWonderLab"):
            game = "WonderLab"
        main_color = game_to_visuals[game][0]
        sub_color  = game_to_visuals[game][1]
        #Update colors
        self.setStyleSheet("QWidget{background:transparent; color: #ffffff; font-family: Cambria; font-size: 18px}"
        + "QMessageBox{background-color: " + main_color + "}"
        + "QDialog{background-color: " + main_color + "}"
        + "QProgressDialog{background-color: " + main_color + "}"
        + "QPushButton{background-color: " + main_color + "}"
        + "QLineEdit{background-color: " + main_color + "; selection-background-color: " + sub_color + "}"
        + "QProgressBar{border: 2px solid white; text-align: center; font: bold}"
        + "QToolTip{border: 0px; background-color: " + main_color + "; color: #ffffff; font-family: Cambria; font-size: 18px}")
        #Update background
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
        self.progress_bar.setValue(progress)
    
    def rando_finished(self):
        self.setEnabled(True)
        box = QMessageBox(self)
        box.setWindowTitle("Message")
        box.setText("Game randomized !")
        box.exec()
    
    def update_finished(self):
        sys.exit()
    
    def thread_failure(self, reason):
        self.progress_bar.close()
        self.setEnabled(True)
        self.notify_error(reason)
    
    def notify_error(self, message):
        box = QMessageBox(self)
        box.setWindowTitle("Error")
        box.setIcon(QMessageBox.Critical)
        box.setText(message)
        box.exec()

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
        
        self.progress_bar = QProgressDialog("Initializing...", None, 0, 8, self)
        self.progress_bar.setFixedSize(280, 80)
        self.progress_bar.setWindowTitle("Status")
        self.progress_bar.setWindowModality(Qt.WindowModal)
        
        self.worker = Generate(self.progress_bar, self.seed, game_path)
        self.worker.signaller.progress.connect(self.set_progress)
        self.worker.signaller.finished.connect(self.rando_finished)
        self.worker.signaller.error.connect(self.thread_failure)
        self.worker.start()
    
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
        if os.path.isfile(game_path + "\\data.bak"):
            os.remove(game_path + "\\data.win")
            os.rename(game_path + "\\data.bak", game_path + "\\data.win")
        if os.path.isdir(game_path + "\\backup"):
            shutil.rmtree(game_path + "\\data")
            os.rename(game_path + "\\backup", game_path + "\\data")
        
        self.setEnabled(True)
        box = QMessageBox(self)
        box.setWindowTitle("Message")
        box.setText("Game directory reverted back to vanilla !")
        box.exec()
    
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
                self.progress_bar = QProgressDialog("Downloading...", None, 0, api["assets"][0]["size"], self)
                self.progress_bar.setWindowTitle("Status")
                self.progress_bar.setWindowModality(Qt.WindowModal)
                self.progress_bar.setAutoClose(False)
                self.progress_bar.setAutoReset(False)
                
                self.worker = Update(self.progress_bar, api)
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