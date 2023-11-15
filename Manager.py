import json
import os
import struct

class Object:
    def __init__(self, sprite, visible, solid, unknown, persistent, parent, texture_mask_id, uses_physics, is_sensor, collision_shape, events):
        self.sprite = sprite
        self.visible = visible
        self.solid = solid
        self.unknown = unknown
        self.persistent = persistent
        self.parent = parent
        self.texture_mask_id = texture_mask_id
        self.uses_physics = uses_physics
        self.is_sensor = is_sensor
        self.collision_shape = collision_shape
        self.events = events

class Event:
    def __init__(self, subtype_id, action):
        self.subtype_id = subtype_id
        self.action = action

class Entity:
    def __init__(self, x_pos, y_pos, type, creation_code, scale_x, scale_y, image_speed, frame_index, color, rotation, pre_create_code):
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.type = type
        self.creation_code = creation_code
        self.scale_x = scale_x
        self.scale_y = scale_y
        self.image_speed = image_speed
        self.frame_index = frame_index
        self.color = color
        self.rotation = rotation
        self.pre_create_code = pre_create_code

def init(module):
    global game
    game = module
    global game_name
    game_name = game.__name__
    global game_objects
    game_objects = {}
    global game_objects_backup
    game_objects_backup = {}
    global game_entities
    game_entities = {}
    global event_types
    event_types = [
        "Create",
        "Destroy",
        "Alarm",
        "Step",
        "Collision",
        "Keyboard",
        "Mouse",
        "Other",
        "Draw",
        "KeyPress",
        "KeyRelease",
        "Trigger",
        "CleanUp",
        "Gesture",
        "PreCreate"
    ]

def open_game_data(game_path):
    global game_data
    game_data = open(game_path + "\\data.win", "r+b")
    global game_text
    with open(game_path + "\\data\\dial_e.txt", "r", encoding="utf8") as file_reader:
        game_text = file_reader.readlines()

def close_game_data(game_path):
    game_data.close()
    with open(game_path + "\\data\\dial_e.txt", "w", encoding="utf8") as file_reader:
        file_reader.writelines(game_text)

def load_constant():
    global constant
    constant = {}
    for file in os.listdir("Data\\" + game_name + "\\Constant"):
        name, extension = os.path.splitext(file)
        with open("Data\\" + game_name + "\\Constant\\" + file, "r", encoding="utf8") as file_reader:
            constant[name] = json.load(file_reader)

def read_game_data():
    #Object data
    game_data.seek(game.object_list_pointer)
    object_list_length = int.from_bytes(game_data.read(4), "little")
    for object_index in range(object_list_length):
        game_data.seek(game.object_list_pointer + 4 + object_index*4)
        object_offset = int.from_bytes(game_data.read(4), "little")
        #Get name
        game_data.seek(object_offset)
        name_offset = int.from_bytes(game_data.read(4), "little")
        game_data.seek(name_offset - 4)
        name_length = int.from_bytes(game_data.read(4), "little")
        name = game_data.read(name_length).decode("utf-8")
        #Read data
        game_data.seek(object_offset + 4)
        sprite          = int.from_bytes(game_data.read(4), "little")
        sprite          = -(sprite & 0x8000) | (sprite & 0x7fff)
        visible         = bool(int.from_bytes(game_data.read(4), "little"))
        solid           = bool(int.from_bytes(game_data.read(4), "little"))
        unknown         = bool(int.from_bytes(game_data.read(4), "little"))
        persistent      = bool(int.from_bytes(game_data.read(4), "little"))
        parent          = int.from_bytes(game_data.read(4), "little")
        parent          = -(parent & 0x8000) | (parent & 0x7fff)
        texture_mask_id = int.from_bytes(game_data.read(4), "little")
        texture_mask_id = -(texture_mask_id & 0x8000) | (texture_mask_id & 0x7fff)
        uses_physics    = bool(int.from_bytes(game_data.read(4), "little"))
        is_sensor       = bool(int.from_bytes(game_data.read(4), "little"))
        collision_shape = int.from_bytes(game_data.read(4), "little")
        #Events
        events = {}
        events_backup = {}
        event_list_offset = object_offset + 0x50
        game_data.seek(event_list_offset)
        event_list_length = int.from_bytes(game_data.read(4), "little")
        for event_index in range(event_list_length):
            events[event_types[event_index]] = []
            events_backup[event_types[event_index]] = []
            game_data.seek(event_list_offset + 4 + event_index*4)
            subevent_list_offset = int.from_bytes(game_data.read(4), "little")
            game_data.seek(subevent_list_offset)
            subevent_list_length = int.from_bytes(game_data.read(4), "little")
            for subevent_index in range(subevent_list_length):
                game_data.seek(subevent_list_offset + 4 + subevent_index*4)
                subevent_offset = int.from_bytes(game_data.read(4), "little")
                game_data.seek(subevent_offset)
                subtype_id = int.from_bytes(game_data.read(4), "little")
                game_data.read(0x28)
                action = int.from_bytes(game_data.read(4), "little")
                action = -(action & 0x8000) | (action & 0x7fff)
                events[event_types[event_index]].append(Event(subtype_id, action))
                events_backup[event_types[event_index]].append(Event(subtype_id, action))
        game_objects[name] = Object(sprite, visible, solid, unknown, persistent, parent, texture_mask_id, uses_physics, is_sensor, collision_shape, events)
        game_objects_backup[name] = Object(sprite, visible, solid, unknown, persistent, parent, texture_mask_id, uses_physics, is_sensor, collision_shape, events_backup)
    #Room data
    game_data.seek(game.room_list_pointer)
    room_list_length = int.from_bytes(game_data.read(4), "little")
    for room_index in range(room_list_length):
        game_data.seek(game.room_list_pointer + 4 + room_index*4)
        room_offset = int.from_bytes(game_data.read(4), "little")
        game_data.seek(room_offset + 0x30)
        entity_list_offset = int.from_bytes(game_data.read(4), "little")
        game_data.seek(entity_list_offset)
        entity_list_length = int.from_bytes(game_data.read(4), "little")
        for entity_index in range(entity_list_length):
            game_data.seek(entity_list_offset + 4 + entity_index*4)
            entity_offset = int.from_bytes(game_data.read(4), "little")
            game_data.seek(entity_offset)
            x_pos           = int.from_bytes(game_data.read(4), "little")
            y_pos           = int.from_bytes(game_data.read(4), "little")
            type            = list(game_objects)[int.from_bytes(game_data.read(4), "little")]
            instance_id     = int.from_bytes(game_data.read(4), "little")
            creation_code   = int.from_bytes(game_data.read(4), "little")
            creation_code   = -(creation_code & 0x8000) | (creation_code & 0x7fff)
            scale_x         = struct.unpack('!f', bytes.fromhex("{:08x}".format(int.from_bytes(game_data.read(4), "little"))))[0]
            scale_y         = struct.unpack('!f', bytes.fromhex("{:08x}".format(int.from_bytes(game_data.read(4), "little"))))[0]
            image_speed     = struct.unpack('!f', bytes.fromhex("{:08x}".format(int.from_bytes(game_data.read(4), "little"))))[0]
            frame_index     = int.from_bytes(game_data.read(4), "little")
            color           = "{:08x}".format(int.from_bytes(game_data.read(4), "little")).upper()
            rotation        = struct.unpack('!f', bytes.fromhex("{:08x}".format(int.from_bytes(game_data.read(4), "little"))))[0]
            pre_create_code = int.from_bytes(game_data.read(4), "little")
            pre_create_code = -(pre_create_code & 0x8000) | (pre_create_code & 0x7fff)
            game_entities[instance_id] = Entity(x_pos, y_pos, type, creation_code, scale_x, scale_y, image_speed, frame_index, color, rotation, pre_create_code)

def write_game_data():
    #Object data
    game_data.seek(game.object_list_pointer)
    object_list_length = int.from_bytes(game_data.read(4), "little")
    for object_index in range(object_list_length):
        game_data.seek(game.object_list_pointer + 4 + object_index*4)
        object_offset = int.from_bytes(game_data.read(4), "little")
        #Get name
        game_data.seek(object_offset)
        name_offset = int.from_bytes(game_data.read(4), "little")
        game_data.seek(name_offset - 4)
        name_length = int.from_bytes(game_data.read(4), "little")
        name = game_data.read(name_length).decode("utf-8")
        #Write data
        game_data.seek(object_offset + 4)
        game_data.write((game_objects[name].sprite & 0xFFFFFFFF).to_bytes(4, "little"))
        game_data.write(int(game_objects[name].visible).to_bytes(4, "little"))
        game_data.write(int(game_objects[name].solid).to_bytes(4, "little"))
        game_data.write(int(game_objects[name].unknown).to_bytes(4, "little"))
        game_data.write(int(game_objects[name].persistent).to_bytes(4, "little"))
        game_data.write((game_objects[name].parent & 0xFFFFFFFF).to_bytes(4, "little"))
        game_data.write((game_objects[name].texture_mask_id & 0xFFFFFFFF).to_bytes(4, "little"))
        game_data.write(int(game_objects[name].uses_physics).to_bytes(4, "little"))
        game_data.write(int(game_objects[name].is_sensor).to_bytes(4, "little"))
        game_data.write(game_objects[name].collision_shape.to_bytes(4, "little"))
        #Events
        event_list_offset = object_offset + 0x50
        game_data.seek(event_list_offset)
        event_list_length = int.from_bytes(game_data.read(4), "little")
        for event_index in range(event_list_length):
            game_data.seek(event_list_offset + 4 + event_index*4)
            subevent_list_offset = int.from_bytes(game_data.read(4), "little")
            game_data.seek(subevent_list_offset)
            subevent_list_length = int.from_bytes(game_data.read(4), "little")
            for subevent_index in range(subevent_list_length):
                game_data.seek(subevent_list_offset + 4 + subevent_index*4)
                subevent_offset = int.from_bytes(game_data.read(4), "little")
                game_data.seek(subevent_offset)
                game_data.write(game_objects[name].events[event_types[event_index]][subevent_index].subtype_id.to_bytes(4, "little"))
                game_data.read(0x28)
                game_data.write((game_objects[name].events[event_types[event_index]][subevent_index].action & 0xFFFFFFFF).to_bytes(4, "little"))
    #Room data
    game_data.seek(game.room_list_pointer)
    room_list_length = int.from_bytes(game_data.read(4), "little")
    for room_index in range(room_list_length):
        game_data.seek(game.room_list_pointer + 4 + room_index*4)
        room_offset = int.from_bytes(game_data.read(4), "little")
        game_data.seek(room_offset + 0x30)
        entity_list_offset = int.from_bytes(game_data.read(4), "little")
        game_data.seek(entity_list_offset)
        entity_list_length = int.from_bytes(game_data.read(4), "little")
        for entity_index in range(entity_list_length):
            game_data.seek(entity_list_offset + 4 + entity_index*4)
            entity_offset = int.from_bytes(game_data.read(4), "little")
            game_data.seek(entity_offset + 0xC)
            instance_id = int.from_bytes(game_data.read(4), "little")
            game_data.seek(entity_offset)
            game_data.write(game_entities[instance_id].x_pos.to_bytes(4, "little"))
            game_data.write(game_entities[instance_id].y_pos.to_bytes(4, "little"))
            game_data.write(list(game_objects).index(game_entities[instance_id].type).to_bytes(4, "little"))
            game_data.read(4)
            game_data.write((game_entities[instance_id].creation_code & 0xFFFFFFFF).to_bytes(4, "little"))
            game_data.write(struct.unpack('<I', struct.pack('<f', game_entities[instance_id].scale_x))[0].to_bytes(4, "little"))
            game_data.write(struct.unpack('<I', struct.pack('<f', game_entities[instance_id].scale_y))[0].to_bytes(4, "little"))
            game_data.write(struct.unpack('<I', struct.pack('<f', game_entities[instance_id].image_speed))[0].to_bytes(4, "little"))
            game_data.write(game_entities[instance_id].frame_index.to_bytes(4, "little"))
            game_data.write(int(game_entities[instance_id].color, 16).to_bytes(4, "little"))
            game_data.write(struct.unpack('<I', struct.pack('<f', game_entities[instance_id].rotation))[0].to_bytes(4, "little"))
            game_data.write((game_entities[instance_id].pre_create_code & 0xFFFFFFFF).to_bytes(4, "little"))

def transfer_object_code(recipient, giver):
    game_objects[recipient].sprite = game_objects_backup[giver].sprite
    for event_type in game_objects[recipient].events:
        for subevent in game_objects[recipient].events[event_type]:
            for subevent_backup in game_objects_backup[giver].events[event_type]:
                if subevent.subtype_id == subevent_backup.subtype_id:
                    subevent.action = subevent_backup.action

def remove_entity(instance):
    game_entities[instance].x_pos = 0
    game_entities[instance].x_pos = 0
    game_entities[instance].scale_x = 0
    game_entities[instance].scale_y = 0

def import_tilemap(tile_path):
    name, extension = os.path.splitext(tile_path)
    offset = int(name.split("\\")[-1], 16)
    with open(tile_path) as file_reader:
        tile_map = file_reader.read().strip().replace("\n", ",").split(",")
    game_data.seek(offset)
    for tile in tile_map:
        game_data.write(int(tile).to_bytes(4, "little"))

def is_text_entry(string):
    if game_text.count(string + "\n") != 1:
        return False
    if string[0] in ["@", "#", "+", "="]:
        return True
    if string[0:3] == "bgm":
        return True
    if string[0:4] == "boss":
        return True
    return False

def replace_text_entry(entry, new_text):
    if not is_text_entry(entry):
        raise Exception("Text entry invalid")
    for line_index in range(len(game_text)):
        if game_text[line_index].strip() == entry:
            start_index = line_index + 1
            break
    while start_index < len(game_text):
        game_text.pop(start_index)
        if not game_text[start_index].strip():
            break
        if is_text_entry(game_text[start_index].strip()):
            break
    text_lines = new_text.split("\n")
    for line_index in range(len(text_lines) -1, -1, -1):
        line = text_lines[line_index] + "\n"
        game_text.insert(start_index, line)

def apply_xdelta_patch(data_path, patch):
    data_name, data_extension = os.path.splitext(data_path)
    root = os.getcwd()
    os.chdir("Data")
    os.system("cmd /c xdelta.exe -d -n -s \"" + data_path + "\" \"" + patch + "\" \"" + data_name + ".out\"")
    os.chdir(root)
    os.remove(data_path)
    os.rename(data_name + ".out", data_path)