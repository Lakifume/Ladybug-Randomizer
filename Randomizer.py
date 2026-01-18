import Manager
import Gameplay
import Cosmetic
import MapHelper
import MapViewer
import ItemTracker
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

script_name = os.path.splitext(os.path.basename(__file__))[0]

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

def write_config():
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
        shutil.copyfile(f"{self.path}\\data.win", f"{self.path}\\data.bak")
        shutil.copytree(f"{self.path}\\data", f"{self.path}\\backup")
        
        #Init
        Gameplay.init()
        Cosmetic.init()
        MapHelper.init()
        Manager.load_constant()
        
        current += 1
        self.signaller.progress.emit(current)
        self.progress_bar.setLabelText("Unpacking data...")
        
        Manager.unpack_game_data(self.path)
        Manager.unpack_save_data()
        Manager.read_game_data()
        Manager.get_save_file_path()
        
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
        
        if config.getboolean("Extra", "bReverseRando"):
            Manager.game.set_reverse_start()
        
        if config.getboolean("Extra", "bRequireAllKeys"):
            Manager.game.set_all_keys_required()
        
        if Manager.game == LunaNights:
            if config.getboolean("Extra", "bSpeedrunLogic"):
                Gameplay.apply_extra_logic("SpeedrunLogic")
        
            if config.getboolean("Extra", "bStage6Unlocked"):
                LunaNights.unlock_extra_stage()
            
            if config.getboolean("Extra", "bStartWithDash"):
                LunaNights.set_dash_spike_start()
            
            if random.random() < 1/8:
                LunaNights.swap_skeleton_sprites()
        
        if Manager.game == WonderLab:
            if config.getboolean("Extra", "bSkipBossRush"):
                WonderLab.remove_boss_rush()
        
            if config.getboolean("Extra", "bPlayerLevel1"):
                WonderLab.set_player_level_1()
            
            if config.getboolean("Extra", "bSpiritLevel1"):
                WonderLab.set_spirit_level_1()
        
        if config.getboolean("Extra", "bOneHitKOMode"):
            Manager.game.set_one_hit_ko_mode()
        
        current += 1
        self.signaller.progress.emit(current)
        self.progress_bar.setLabelText("Randomizing items...")
        
        Gameplay.categorize_items()
        Gameplay.set_logic_complexity(config.getint("Gameplay", "iLogicComplexity"))
        Gameplay.set_enemy_type_wheight(config.getint("Gameplay", "iEnemyTypesWeight"))
        
        if config.getboolean("Gameplay", "bKeyItems"):
            Gameplay.add_item_type("Key")
            if Manager.game == LunaNights and config.getboolean("Gameplay", "bGemTowers"):
                if not config.getboolean("Gameplay", "bUpgrades") and not config.getboolean("Gameplay", "bSpells"):
                    Gameplay.remove_hardcoded_items()
            MapHelper.get_map_info()
        
        if config.getboolean("Gameplay", "bUpgrades"):
            Gameplay.add_item_type("Upgrade")
        
        if config.getboolean("Gameplay", "bSpells"):
            Gameplay.add_item_type("Spell")
        
        if config.getboolean("Gameplay", "bGemTowers"):
            Gameplay.add_item_type("Gem")
        
        if config.getboolean("Gameplay", "bWeapons"):
            Gameplay.add_item_type("Weapon")
        
        if config.getboolean("Gameplay", "bKeyItems"):
            random.seed(self.seed)
            Gameplay.process_key_logic()
            Gameplay.write_spoiler_log(self.seed)
            Gameplay.write_save_info()
        
        random.seed(self.seed)
        Gameplay.randomize_items()
        
        if config.getboolean("Gameplay", "bEnemyTypes"):
            random.seed(self.seed)
            Gameplay.randomize_enemies()
        
        current += 1
        self.signaller.progress.emit(current)
        self.progress_bar.setLabelText("Randomizing music...")
        
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
        Manager.repack_save_data()
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
        try:
            self.process()
        except Exception:
            self.signaller.error.emit(traceback.format_exc())

    def process(self):
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

class QCheckBox(QCheckBox):
    def nextCheckState(self):
        if self.checkState() == Qt.Unchecked:
            self.setCheckState(Qt.PartiallyChecked)
        elif self.checkState() == Qt.PartiallyChecked:
            self.setCheckState(Qt.Unchecked)
    
    def checkStateSet(self):
        super().checkStateSet()
        if self.checkState() == Qt.Checked:
            self.setCheckState(Qt.PartiallyChecked)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setEnabled(False)
        self.init()
        self.check_for_updates()

    def init(self):
        
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

        self.check_box_4 = QCheckBox("Gem Towers")
        self.check_box_4.setToolTip("Include gem towers in the item pool.")
        self.check_box_4.stateChanged.connect(self.check_box_4_changed)
        box_1_grid.addWidget(self.check_box_4, 3, 0)

        self.check_box_19 = QCheckBox("Weapons")
        self.check_box_19.setToolTip("Include swords and bows in the item pool.")
        self.check_box_19.stateChanged.connect(self.check_box_19_changed)
        box_1_grid.addWidget(self.check_box_19, 3, 0)
        
        self.check_box_5 = QCheckBox("Enemy Types")
        self.check_box_5.setToolTip("Shuffle enemies by type.")
        self.check_box_5.stateChanged.connect(self.check_box_5_changed)
        box_1_grid.addWidget(self.check_box_5, 4, 0)

        self.check_box_6 = QCheckBox("Background Music")
        self.check_box_6.setToolTip("Shuffle music tracks by type.")
        self.check_box_6.stateChanged.connect(self.check_box_6_changed)
        box_2_grid.addWidget(self.check_box_6, 0, 0)

        self.check_box_7 = QCheckBox("World Colors")
        self.check_box_7.setToolTip("Randomize the hue of tilesets and backgrounds.")
        self.check_box_7.stateChanged.connect(self.check_box_7_changed)
        box_2_grid.addWidget(self.check_box_7, 1, 0)

        self.check_box_8 = QCheckBox("Enemy Colors")
        self.check_box_8.setToolTip("Randomize the hue of enemy sprites.")
        self.check_box_8.stateChanged.connect(self.check_box_8_changed)
        box_2_grid.addWidget(self.check_box_8, 2, 0)

        self.check_box_9 = QCheckBox("Character Colors")
        self.check_box_9.setToolTip("Randomize the hue of character sprites.")
        self.check_box_9.stateChanged.connect(self.check_box_9_changed)
        box_2_grid.addWidget(self.check_box_9, 3, 0)
        
        self.check_box_10 = QCheckBox("Dialogues")
        self.check_box_10.setToolTip("Randomize all conversation lines.")
        self.check_box_10.stateChanged.connect(self.check_box_10_changed)
        box_2_grid.addWidget(self.check_box_10, 4, 0)
        
        self.check_box_18 = QCheckBox("Reverse Rando")
        self.check_box_18.setToolTip("Start the game near the top of the map.")
        self.check_box_18.stateChanged.connect(self.check_box_18_changed)
        box_3_grid.addWidget(self.check_box_18, 0, 0)
        retain = self.check_box_18.sizePolicy()
        retain.setRetainSizeWhenHidden(True)
        self.check_box_18.setSizePolicy(retain)
        
        self.check_box_20 = QCheckBox("Require All Keys")
        self.check_box_20.setToolTip("Force acquiring all colored keys/switches\nto reach the final boss.")
        self.check_box_20.stateChanged.connect(self.check_box_20_changed)
        box_3_grid.addWidget(self.check_box_20, 1, 0)
        retain = self.check_box_20.sizePolicy()
        retain.setRetainSizeWhenHidden(True)
        self.check_box_20.setSizePolicy(retain)
        
        self.check_box_12 = QCheckBox("Stage 6 Unlocked")
        self.check_box_12.setToolTip("Have the extra stage available from the start,\nno longer requiring Flandre to unlock.")
        self.check_box_12.stateChanged.connect(self.check_box_12_changed)
        box_3_grid.addWidget(self.check_box_12, 0, 1)
        retain = self.check_box_12.sizePolicy()
        retain.setRetainSizeWhenHidden(True)
        self.check_box_12.setSizePolicy(retain)
        
        self.check_box_13 = QCheckBox("Skip Boss Rush")
        self.check_box_13.setToolTip("Remove the boss rush at the end of stage 6.")
        self.check_box_13.stateChanged.connect(self.check_box_13_changed)
        box_3_grid.addWidget(self.check_box_13, 0, 1)
        retain = self.check_box_13.sizePolicy()
        retain.setRetainSizeWhenHidden(True)
        self.check_box_13.setSizePolicy(retain)

        self.check_box_11 = QCheckBox("Speedrun Logic")
        self.check_box_11.setToolTip("Switch to a progression logic that may require\nspeedrun tricks, glitches and taking damage.")
        self.check_box_11.stateChanged.connect(self.check_box_11_changed)
        box_3_grid.addWidget(self.check_box_11, 1, 1)
        retain = self.check_box_11.sizePolicy()
        retain.setRetainSizeWhenHidden(True)
        self.check_box_11.setSizePolicy(retain)
        
        self.check_box_15 = QCheckBox("Player Level 1")
        self.check_box_15.setToolTip("Enable the built-in player level 1 locked mode.")
        self.check_box_15.stateChanged.connect(self.check_box_15_changed)
        box_3_grid.addWidget(self.check_box_15, 1, 1)
        retain = self.check_box_15.sizePolicy()
        retain.setRetainSizeWhenHidden(True)
        self.check_box_15.setSizePolicy(retain)
        
        self.check_box_16 = QCheckBox("One Hit KO Mode")
        self.check_box_16.setToolTip("Enable the built-in 1 HP locked mode.")
        self.check_box_16.stateChanged.connect(self.check_box_16_changed)
        box_3_grid.addWidget(self.check_box_16, 0, 2)
        retain = self.check_box_16.sizePolicy()
        retain.setRetainSizeWhenHidden(True)
        self.check_box_16.setSizePolicy(retain)
        
        self.check_box_14 = QCheckBox("Start With Dash")
        self.check_box_14.setToolTip("Start the game with the Dash Spike ability.\nUnlike the built-in mode this will not give\nyou all the spells from the start.")
        self.check_box_14.stateChanged.connect(self.check_box_14_changed)
        box_3_grid.addWidget(self.check_box_14, 1, 2)
        retain = self.check_box_14.sizePolicy()
        retain.setRetainSizeWhenHidden(True)
        self.check_box_14.setSizePolicy(retain)
        
        self.check_box_17 = QCheckBox("Spirit Level 1")
        self.check_box_17.setToolTip("Enable the built-in spirit level 1 locked mode.")
        self.check_box_17.stateChanged.connect(self.check_box_17_changed)
        box_3_grid.addWidget(self.check_box_17, 1, 2)
        retain = self.check_box_17.sizePolicy()
        retain.setRetainSizeWhenHidden(True)
        self.check_box_17.setSizePolicy(retain)
        
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
        
        #Init checkboxes
        
        self.check_box_1.setChecked(config.getboolean("Gameplay", "bKeyItems"))
        self.check_box_2.setChecked(config.getboolean("Gameplay", "bUpgrades"))
        self.check_box_3.setChecked(config.getboolean("Gameplay", "bSpells"))
        self.check_box_4.setChecked(config.getboolean("Gameplay", "bGemTowers"))
        self.check_box_19.setChecked(config.getboolean("Gameplay", "bWeapons"))
        self.check_box_5.setChecked(config.getboolean("Gameplay", "bEnemyTypes"))
        
        self.check_box_6.setChecked(config.getboolean("Cosmetic", "bBackgroundMusic"))
        self.check_box_7.setChecked(config.getboolean("Cosmetic", "bWorldColors"))
        self.check_box_8.setChecked(config.getboolean("Cosmetic", "bEnemyColors"))
        self.check_box_9.setChecked(config.getboolean("Cosmetic", "bCharacterColors"))
        self.check_box_10.setChecked(config.getboolean("Cosmetic", "bDialogues"))
        
        self.check_box_18.setChecked(config.getboolean("Extra", "bReverseRando"))
        self.check_box_20.setChecked(config.getboolean("Extra", "bRequireAllKeys"))
        self.check_box_12.setChecked(config.getboolean("Extra", "bStage6Unlocked"))
        self.check_box_13.setChecked(config.getboolean("Extra", "bSkipBossRush"))
        self.check_box_11.setChecked(config.getboolean("Extra", "bSpeedrunLogic"))
        self.check_box_15.setChecked(config.getboolean("Extra", "bPlayerLevel1"))
        self.check_box_16.setChecked(config.getboolean("Extra", "bOneHitKOMode"))
        self.check_box_14.setChecked(config.getboolean("Extra", "bStartWithDash"))
        self.check_box_17.setChecked(config.getboolean("Extra", "bSpiritLevel1"))
        
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
        
        button_2 = QPushButton("Reset Game")
        button_2.setToolTip("Revert game directory back to vanilla.")
        button_2.clicked.connect(self.button_2_clicked)
        button_hbox.addWidget(button_2)
        
        button_3 = QPushButton("Load Spoiler")
        button_3.setToolTip("Display solution from a spoiler log.")
        button_3.clicked.connect(self.button_3_clicked)
        button_hbox.addWidget(button_3)
        
        button_4 = QPushButton("Item Tracker")
        button_4.setToolTip("Open up an item tracker window for a randomized game.")
        button_4.clicked.connect(self.button_4_clicked)
        button_hbox.addWidget(button_4)
        
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
        if not checked:
            self.check_box_11.setChecked(False)
            self.check_box_18.setChecked(False)
        self.fix_background_glitch()

    def check_box_2_changed(self):
        checked = self.check_box_2.isChecked()
        config.set("Gameplay", "bUpgrades", str(checked).lower())

    def check_box_3_changed(self):
        checked = self.check_box_3.isChecked()
        config.set("Gameplay", "bSpells", str(checked).lower())

    def check_box_4_changed(self):
        checked = self.check_box_4.isChecked()
        config.set("Gameplay", "bGemTowers", str(checked).lower())

    def check_box_19_changed(self):
        checked = self.check_box_19.isChecked()
        config.set("Gameplay", "bWeapons", str(checked).lower())

    def check_box_5_changed(self):
        checked = self.check_box_5.isChecked()
        config.set("Gameplay", "bEnemyTypes", str(checked).lower())
        self.spin_button_2.setVisible(checked)
        self.fix_background_glitch()

    def check_box_6_changed(self):
        checked = self.check_box_6.isChecked()
        config.set("Cosmetic", "bBackgroundMusic", str(checked).lower())

    def check_box_7_changed(self):
        checked = self.check_box_7.isChecked()
        config.set("Cosmetic", "bWorldColors", str(checked).lower())

    def check_box_8_changed(self):
        checked = self.check_box_8.isChecked()
        config.set("Cosmetic", "bEnemyColors", str(checked).lower())

    def check_box_9_changed(self):
        checked = self.check_box_9.isChecked()
        config.set("Cosmetic", "bCharacterColors", str(checked).lower())

    def check_box_10_changed(self):
        checked = self.check_box_10.isChecked()
        config.set("Cosmetic", "bDialogues", str(checked).lower())

    def check_box_20_changed(self):
        checked = self.check_box_20.isChecked()
        config.set("Extra", "bRequireAllKeys", str(checked).lower())

    def check_box_11_changed(self):
        checked = self.check_box_11.isChecked()
        config.set("Extra", "bSpeedrunLogic", str(checked).lower())
        if checked:
            self.check_box_1.setChecked(True)
            self.check_box_16.setChecked(False)

    def check_box_18_changed(self):
        checked = self.check_box_18.isChecked()
        config.set("Extra", "bReverseRando", str(checked).lower())
        if checked:
            self.check_box_1.setChecked(True)
            self.check_box_16.setChecked(False)

    def check_box_12_changed(self):
        checked = self.check_box_12.isChecked()
        config.set("Extra", "bStage6Unlocked", str(checked).lower())

    def check_box_13_changed(self):
        checked = self.check_box_13.isChecked()
        config.set("Extra", "bSkipBossRush", str(checked).lower())

    def check_box_14_changed(self):
        checked = self.check_box_14.isChecked()
        config.set("Extra", "bStartWithDash", str(checked).lower())
        if checked:
            self.check_box_16.setChecked(False)

    def check_box_15_changed(self):
        checked = self.check_box_15.isChecked()
        config.set("Extra", "bPlayerLevel1", str(checked).lower())

    def check_box_16_changed(self):
        checked = self.check_box_16.isChecked()
        config.set("Extra", "bOneHitKOMode", str(checked).lower())
        if checked:
            self.check_box_11.setChecked(False)
            self.check_box_14.setChecked(False)
            self.check_box_18.setChecked(False)

    def check_box_17_changed(self):
        checked = self.check_box_17.isChecked()
        config.set("Extra", "bSpiritLevel1", str(checked).lower())

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
        checked_1 = self.radio_button_1.isChecked()
        checked_2 = self.radio_button_2.isChecked()
        config.set("Game", "bLunaNights", str(checked_1).lower())
        config.set("Game", "bWonderLab", str(checked_2).lower())
        self.check_box_4.setVisible(checked_1)
        self.check_box_19.setVisible(checked_2)
        self.check_box_11.setVisible(checked_1)
        self.check_box_12.setVisible(checked_1)
        self.check_box_14.setVisible(checked_1)
        self.check_box_13.setVisible(checked_2)
        self.check_box_15.setVisible(checked_2)
        self.check_box_17.setVisible(checked_2)
        game = "LunaNights" if config.getboolean("Game", "bLunaNights") else "WonderLab"
        self.output_field.setText(config.get("Misc", f"s{game}GameDir"))
        self.reset_visuals()
    
    def reset_visuals(self):
        #Determine game
        game = "LunaNights" if config.getboolean("Game", "bLunaNights") else "WonderLab"
        main_color = game_to_visuals[game][0]
        sub_color  = game_to_visuals[game][1]
        #Update colors
        self.setStyleSheet("QWidget{background: transparent; color: #ffffff; font-family: Cambria; font-size: 18px}"
        + "QMessageBox{background-color: " + main_color + "}"
        + "QDialog{background-color: " + main_color + "}"
        + "QProgressDialog{background-color: " + main_color + "}"
        + "QPushButton{background-color: " + main_color + "}"
        + "QLineEdit{background-color: " + main_color + "; selection-background-color: " + sub_color + "}"
        + "QProgressBar{border: 2px solid white; text-align: center; font: bold}"
        + "QToolTip{border: 1px solid white; background-color: " + main_color + "; color: #ffffff; font-family: Cambria; font-size: 18px}")
        #Update background
        background = QPixmap(f"Data\\{game}\\background.png")
        self.palette = QPalette()
        self.palette.setBrush(QPalette.Window, background)
        self.setPalette(self.palette)
    
    def create_seed_layout(self):
        self.seed_layout = QGridLayout()
        
        self.seed_field = QLineEdit(config.get("Misc", "sSeed"))
        self.seed_field.setMaxLength(30)
        self.seed_field.textChanged[str].connect(self.new_seed)
        self.seed_layout.addWidget(self.seed_field, 0, 0, 1, 2)
        
        seed_button_1 = QPushButton("New Seed")
        seed_button_1.clicked.connect(self.seed_button_1_clicked)
        self.seed_layout.addWidget(seed_button_1, 1, 0, 1, 1)
        
        seed_button_2 = QPushButton("Confirm")
        seed_button_2.clicked.connect(self.seed_button_2_clicked)
        self.seed_layout.addWidget(seed_button_2, 1, 1, 1, 1)
    
    def fix_background_glitch(self):
        try:
            self.box_1.setStyleSheet("")
            QApplication.processEvents()
            self.setPalette(self.palette)
        except TypeError:
            return
    
    def new_output(self, output):
        game = "LunaNights" if config.getboolean("Game", "bLunaNights") else "WonderLab"
        config.set("Misc", f"s{game}GameDir", output)
    
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
        Manager.init(LunaNights if config.getboolean("Game", "bLunaNights") else WonderLab)
        game_path = config.get("Misc", f"s{Manager.game_name}GameDir")
        
        #Check path
        if not os.path.isdir(game_path):
            self.game_path_invalid()
            return
        
        #Seed prompt
        self.create_seed_layout()
        self.seed = None
        self.seed_box = QDialog(self)
        self.seed_box.setLayout(self.seed_layout)
        self.seed_box.setWindowTitle("Seed")
        self.seed_box.exec()
        if not self.seed:
            return
        
        self.setEnabled(False)
        QApplication.processEvents()
        
        Manager.game.init()
        self.restore_vanilla(game_path)
        
        self.progress_bar = QProgressDialog("Initializing...", None, 0, 9, self)
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
        Manager.init(LunaNights if config.getboolean("Game", "bLunaNights") else WonderLab)
        game_path = config.get("Misc", f"s{Manager.game_name}GameDir")
        
        #Check path
        if not os.path.isdir(game_path):
            self.game_path_invalid()
            return
        
        self.setEnabled(False)
        QApplication.processEvents()
        
        Manager.game.init()
        self.restore_vanilla(game_path)
        
        self.setEnabled(True)
        box = QMessageBox(self)
        box.setWindowTitle("Message")
        box.setText("Game directory reverted back to vanilla !")
        box.exec()
    
    def button_3_clicked(self):
        file = QFileDialog.getOpenFileName(parent=self, caption="File", filter="*.json")[0].replace("/", "\\")
        if not file:
            return
        
        file_name = os.path.split(os.path.splitext(file)[0])[-1]
        game_name, seed = file_name.split(" - ")
        with open(file, "r", encoding="utf8") as file_reader:
            spoiler = json.load(file_reader)
        
        #Determine game
        Manager.init(LunaNights if config.getboolean("Game", "bLunaNights") else WonderLab)
        
        #Check game
        if Manager.game_name != game_name:
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
        
        self.map_viewer = MapViewer.MainWindow(seed, spoiler)
    
    def button_4_clicked(self):
        #Determine game
        Manager.init(LunaNights if config.getboolean("Game", "bLunaNights") else WonderLab)
        
        Manager.game.init()
        Manager.load_constant()
        
        save_info_list = Manager.get_save_info_list()
        
        #Check save info
        if not save_info_list:
            box = QMessageBox(self)
            box.setWindowTitle("Warning")
            box.setIcon(QMessageBox.Critical)
            box.setText("No active randomizer saves found !")
            box.exec()
            return
        if len(save_info_list) != 1:
            box = QMessageBox(self)
            box.setWindowTitle("Warning")
            box.setIcon(QMessageBox.Critical)
            box.setText("Multiple active randomizer saves found !")
            box.exec()
            return
        
        save_file_path = os.path.splitext(save_info_list[0])[0]
        self.item_tracker = ItemTracker.MainWindow(f"{save_file_path}.sav")
    
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
            self.seed = float(self.seed) if "." in self.seed else int(self.seed)
        except ValueError:
            pass
        self.seed_box.close()
    
    def restore_vanilla(self, game_path):
        #Restore game files
        if os.path.isfile(f"{game_path}\\data.bak"):
            os.remove(f"{game_path}\\data.win")
            os.rename(f"{game_path}\\data.bak", f"{game_path}\\data.win")
        if os.path.isdir(f"{game_path}\\backup"):
            shutil.rmtree(f"{game_path}\\data")
            os.rename(f"{game_path}\\backup", f"{game_path}\\data")
        #Reset save files
        for file in Manager.get_save_file_list():
            os.remove(file)
        for file in Manager.get_save_info_list():
            os.remove(file)
    
    def game_path_invalid(self):
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
                self.worker.signaller.error.connect(self.thread_failure)
                self.worker.start()
            else:
                self.setEnabled(True)
        else:
            self.setEnabled(True)

def main():
    app = QApplication(sys.argv)
    app.aboutToQuit.connect(write_config)
    main = MainWindow()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()