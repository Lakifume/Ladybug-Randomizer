import Manager
import MapHelper

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

import os
from enum import Enum

TILEWIDTH = 15
TILEHEIGHT = 10
OUTLINE = 2
    
def modify_color(color, hsv_mod):
    hue = (color.hueF() + hsv_mod[0]) % 1
    if hsv_mod[1] < 1:
        sat = color.saturationF() * hsv_mod[1]
    else:
        sat = color.saturationF() + (1 - color.saturationF())*(hsv_mod[1] - 1)
    if hsv_mod[2] < 1:
        val = color.valueF() * hsv_mod[2]
    else:
        val = color.valueF() + (1 - color.valueF())*(hsv_mod[2] - 1)
    return QColor.fromHsvF(hue, sat, val)
    
def modify_pixmap_color(pixmap, hsv_mod):
    image = pixmap.toImage()
    for x in range(image.width()):
        for y in range(image.height()):
            color = image.pixelColor(x, y)
            if color.alpha() != 0:
                color = modify_color(color, hsv_mod)
                image.setPixelColor(x, y, color)
    return QPixmap.fromImage(image)

class RoomTheme(Enum):
    Default = 1
    Light   = 2
    Dark    = 0

theme_to_mod = {
    RoomTheme.Default: (0,   1,    1),
    RoomTheme.Light:   (0, 1/3, 1.75),
    RoomTheme.Dark:    (0,   1, 0.25)
}
theme_to_visuals = {
    RoomTheme.Default: {},
    RoomTheme.Light:   {},
    RoomTheme.Dark:    {}
}

class RoomItem(QGraphicsRectItem):
    def __init__(self, room_data):
        super().__init__(0, 0, room_data.width * TILEWIDTH, room_data.height * TILEHEIGHT)
        
        self.room_data = room_data
        self.reset_pos()
        
        self.outline = QPen()
        self.outline.setWidth(OUTLINE)
        self.outline.setJoinStyle(Qt.MiterJoin)
        
        self.setToolTip(room_data.name)
        self.set_theme(RoomTheme.Default)
    
    def set_theme(self, theme):
        self.current_theme = theme
        self.setZValue(theme.value)
        self.reset_visuals()
    
    def reset_pos(self):
        self.setPos(self.room_data.offset_x * TILEWIDTH, self.room_data.offset_y * TILEHEIGHT)
    
    def reset_visuals(self):
        current_fill = theme_to_visuals[self.current_theme]["Fill"][self.room_data.stage_id]
        self.setBrush(current_fill)
        self.outline.setColor(theme_to_visuals[self.current_theme]["Outline"])
        self.setPen(self.outline)
        for item in self.childItems():
            if type(item) == QGraphicsRectItem:
                item.setBrush(current_fill)
            if type(item) == QGraphicsPixmapItem:
                item.setPixmap(theme_to_visuals[self.current_theme]["Icon"][self.room_data.icon])

class MainWindow(QMainWindow):
    def __init__(self, seed, spoiler):
        super().__init__()
        self.seed = seed
        self.spoiler = spoiler
        self.init()
    
    def init(self):
        self.setStyleSheet("QWidget{background:transparent; color: #ffffff; font-family: Cambria; font-size: 18px}"
        + "QMainWindow{background-image: url(Data/background.png); background-position: center}"
        + "QGraphicsView{border: 0px}"
        + "QComboBox{background-color: #404040; selection-background-color: #32ffffff}"
        + "QComboBox QAbstractItemView{border: 1px solid #404040; selection-background-color: #ffffff}"
        + "QPushButton{background-color: #404040}"
        + "QScrollBar::add-page{background-color: #333333}"
        + "QScrollBar::sub-page{background-color: #333333}"
        + "QToolTip{border: 0px; background-color: #404040; color: #ffffff; font-family: Cambria; font-size: 18px}")
        
        #Graphics
        
        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene, self)
        
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.scale(2, -2)
        self.setCentralWidget(self.view)
        
        #Drop down lists
        
        self.key_drop_down = QComboBox()
        self.key_drop_down.currentIndexChanged.connect(self.key_drop_down_change)
        
        button_1 = QPushButton("Close")
        button_1.clicked.connect(self.button_1_clicked)
        
        #Layouts
        
        hbox_top = QHBoxLayout()
        hbox_top.addWidget(self.key_drop_down)
        hbox_top.addStretch(1)
        
        hbox_bottom = QHBoxLayout()
        hbox_bottom.addStretch(1)
        hbox_bottom.addWidget(button_1)
        
        vbox = QVBoxLayout()
        vbox.addLayout(hbox_top)
        vbox.addStretch(1)
        vbox.addLayout(hbox_bottom)
        
        #Window
        
        self.view.setLayout(vbox)
        self.setFixedSize(1200, 600)
        self.setWindowTitle(self.seed)
        self.setWindowIcon(QIcon("Data\\icon.png"))
        self.show()
        self.load_map()
    
    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        if event.key() == Qt.Key_Space:
            self.reset_rooms()
    
    def keyReleaseEvent(self, event):
        super().keyReleaseEvent(event)
        if event.key() == Qt.Key_Space:
            self.key_drop_down_change(self.key_drop_down.currentIndex())
    
    def add_room_to_completion(self, room):
        room.set_theme(RoomTheme.Default)
    
    def button_1_clicked(self):
        self.close()
    
    def key_drop_down_change(self, index):
        for room in self.room_list:
            if room.room_data.name == MapHelper.check_to_room[self.spoiler[list(self.spoiler)[index]]]:
                room.set_theme(RoomTheme.Default)
            else:
                room.set_theme(RoomTheme.Dark)
    
    def get_room_by_name(self, name):
        return self.room_list[list(Manager.constant["RoomLayout"]).index(name)]
    
    def reset_rooms(self):
        for room in self.room_list:
            room.set_theme(RoomTheme.Default)

    def load_map(self):
        self.fill_visuals()
        
        self.room_list = []
        for room in Manager.constant["RoomLayout"]:
            room_data = MapHelper.room_to_object(room)
            new_room = RoomItem(room_data)
            self.scene.addItem(new_room)
            self.room_list.append(new_room)
            self.add_room_items(new_room)
        
        for item in self.spoiler:
            self.key_drop_down.addItem(Manager.constant["ItemInfo"][item]["Name"])
    
    def fill_visuals(self):
        for theme in theme_to_visuals:
            theme_to_visuals[theme]["Fill"] = []
            theme_to_visuals[theme]["Icon"] = {}
        for color in Manager.game.map_colors:
            for theme in theme_to_visuals:
                theme_to_visuals[theme]["Fill"].append(modify_color(QColor(color), theme_to_mod[theme]))
        for theme in theme_to_visuals:
            theme_to_visuals[theme]["Outline"] = modify_color(QColor("#ffffff"), theme_to_mod[theme])
        for file in os.listdir("Data\\" + Manager.game_name + "\\MapIcon"):
            name, extension = os.path.splitext(file)
            for theme in theme_to_visuals:
                theme_to_visuals[theme]["Icon"][name] = modify_pixmap_color(QPixmap("Data\\" + Manager.game_name + "\\MapIcon\\" + file), theme_to_mod[theme])
            
    def add_room_items(self, room):
        
        #Icons
        if room.room_data.icon:
            icon = self.scene.addPixmap(QPixmap(""))
            icon.setTransform(QTransform.fromScale(1, -1))
            icon.setPos(room.room_data.width*TILEWIDTH/2 - 6, room.room_data.height*TILEHEIGHT/2 + TILEHEIGHT/2 - 1)
            icon.setParentItem(room)
        
        #Doors
        outline = QPen("#00000000")
        for door in room.room_data.doors:
            if door.direction == "Left":
                new_door = self.scene.addRect(0, 0, OUTLINE, 4, outline)
                new_door.setPos(door.x_block*TILEWIDTH - 1, door.y_block*TILEHEIGHT + 3)
                new_door.setParentItem(room)
            if door.direction == "Right":
                new_door = self.scene.addRect(0, 0, OUTLINE, 4, outline)
                new_door.setPos(door.x_block*TILEWIDTH + TILEWIDTH - 1, door.y_block*TILEHEIGHT + 3)
                new_door.setParentItem(room)
            if door.direction == "Bottom":
                new_door = self.scene.addRect(0, 0, 4, OUTLINE, outline)
                new_door.setPos(door.x_block*TILEWIDTH + 5.5, door.y_block*TILEHEIGHT - 1)
                new_door.setParentItem(room)
            if door.direction == "Top":
                new_door = self.scene.addRect(0, 0, 4, OUTLINE, outline)
                new_door.setPos(door.x_block*TILEWIDTH + 5.5, door.y_block*TILEHEIGHT + TILEHEIGHT - 1)
                new_door.setParentItem(room)