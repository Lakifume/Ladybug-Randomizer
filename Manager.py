import LunaNights
import WonderLab

import json
import os
import re
import glob
import string
import shutil
import struct
import base64

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

class PageItem:
    def __init__(self, source_pos_x, source_pos_y, source_size_x, source_size_y, target_pos_x, target_pos_y, target_size_x, target_size_y, bound_size_x, bound_size_y, texture_id):
        self.source_pos_x = source_pos_x
        self.source_pos_y = source_pos_y
        self.source_size_x = source_size_x
        self.source_size_y = source_size_y
        self.target_pos_x = target_pos_x
        self.target_pos_y = target_pos_y
        self.target_size_x = target_size_x
        self.target_size_y = target_size_y
        self.bound_size_x = bound_size_x
        self.bound_size_y = bound_size_y
        self.texture_id = texture_id

class Sprite:
    def __init__(self, page_items):
        self.page_items = page_items

class TileSet:
    def __init__(self, page_item):
        self.page_item = page_item

class TileMap:
    def __init__(self, layer_z, size_x, size_y, tile_data):
        self.layer_z = layer_z
        self.size_x = size_x
        self.size_y = size_y
        self.tile_data = tile_data

class Sound:
    def __init__(self, effects, volume, pitch, audio_id):
        self.effects = effects
        self.volume = volume
        self.pitch = pitch
        self.audio_id = audio_id

class Audio:
    def __init__(self, wave_length):
        self.wave_length = wave_length

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
    global game_page_items
    game_page_items = {}
    global game_sounds
    game_sounds = {}
    global game_sprites
    game_sprites = {}
    global game_strings
    game_strings = {}
    global game_tilesets
    game_tilesets = {}
    global game_tilemaps
    game_tilemaps = {}
    global game_text
    game_text = []
    global game_audio
    game_audio = []
    global game_save
    game_save = {}
    global game_save_backup
    game_save_backup = {}
    global save_signature
    save_signature = "Ladybug Randomizer"
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
    global chunk_to_offset
    chunk_to_offset = {}

def load_constant():
    global constant
    constant = {}
    for file in os.listdir(f"Data\\{game_name}\\Constant"):
        file_name = os.path.splitext(file)[0]
        with open(f"Data\\{game_name}\\Constant\\" + file, "r", encoding="utf8") as file_reader:
            constant[file_name] = json.load(file_reader)
    with open(f"Data\\{game_name}\\Save\\Save.txt", "r", encoding="utf8") as file_reader:
        constant["SaveInfo"] = file_reader.readlines()

def unpack_game_data(game_path):
    #Create the game directory
    if not os.path.isdir("Game"):
        os.makedirs("Game")
    #Unpack data.win
    with open(f"{game_path}\\data.win", "rb") as file_reader:
        file_reader.seek(0, os.SEEK_END)
        data_size = file_reader.tell()
        current_offset = 8
        while current_offset < data_size:
            file_reader.seek(current_offset)
            chunk_name = file_reader.read(4).decode("utf-8")
            chunk_size = int.from_bytes(file_reader.read(4), "little") + 8
            with open(f"Game\\{chunk_name}", "wb") as file_writer:
                file_reader.seek(current_offset)
                file_writer.write(file_reader.read(chunk_size))
            chunk_to_offset[chunk_name] = current_offset
            current_offset += chunk_size
    unpack_textures()
    #Read game text
    with open(f"{game_path}\\data\\dial_e.txt", "r", encoding="utf8") as file_reader:
        game_text.extend(file_reader.readlines())

def repack_game_data(game_path):
    #Repack data.win
    repack_textures()
    with open(f"{game_path}\\data.win", "r+b") as file_writer:
        file_writer.truncate(8)
        file_writer.seek(8)
        for chunk in chunk_to_offset:
            with open(f"Game\\{chunk}", "rb") as file_reader:
                file_writer.write(file_reader.read())
        file_writer.seek(0, os.SEEK_END)
        data_size = file_writer.tell()
        file_writer.seek(4)
        file_writer.write((data_size - 8).to_bytes(4, "little"))
    #Remove the game directory
    shutil.rmtree("Game")
    #Write text changes
    with open(f"{game_path}\\data\\dial_e.txt", "w", encoding="utf8") as file_writer:
        file_writer.writelines(game_text)

def unpack_textures():
    if not os.path.isdir("Game\\Export"):
        os.makedirs("Game\\Export")
    #Export all pngs from TXTR
    with open("Game\\TXTR", "rb") as file_reader:
        file_reader.seek(8)
        texture_count = int.from_bytes(file_reader.read(4), "little")
        for index in range(texture_count):
            file_reader.seek(12 + index*4)
            texture_info_offset = int.from_bytes(file_reader.read(4), "little") - chunk_to_offset["TXTR"]
            file_reader.seek(texture_info_offset + 8)
            texture_offset = int.from_bytes(file_reader.read(4), "little") - chunk_to_offset["TXTR"]
            #Export texture data
            with open(f"Game\\export\\{index}.png", "wb") as file_writer:
                file_reader.seek(texture_offset)
                texture_size = file_reader.read().find((0x49454E44AE426082).to_bytes(8, "big")) + 8
                file_reader.seek(texture_offset)
                file_writer.write(file_reader.read(texture_size))

def repack_textures():
    #Reimport all pngs back into TXTR
    with open("Game\\TXTR", "r+b") as file_writer:
        first_texture = file_writer.read().find((0x89504E470D0A1A0A).to_bytes(8, "big"))
        file_writer.truncate(first_texture)
        file_writer.seek(8)
        texture_count = int.from_bytes(file_writer.read(4), "little")
        file_writer.seek(first_texture)
        for index in range(texture_count):
            #Fill remaining space
            remainder = file_writer.tell()%0x80
            if remainder > 0:
                file_writer.write((0).to_bytes(0x80 - remainder, "little"))
            #Update texture offset
            texture_offset = file_writer.tell()
            file_writer.seek(12 + index*4)
            texture_info_offset = int.from_bytes(file_writer.read(4), "little") - chunk_to_offset["TXTR"]
            file_writer.seek(texture_info_offset + 8)
            file_writer.write((texture_offset + chunk_to_offset["TXTR"]).to_bytes(4, "little"))
            #Append texture data
            file_writer.seek(texture_offset)
            with open(f"Game\\export\\{index}.png", "rb") as file_reader:
                file_writer.write(file_reader.read())
            #Fill remaining space
            remainder = file_writer.tell()%0x10
            if remainder > 0:
                file_writer.write((0).to_bytes(0x10 - remainder, "little"))
        #Update total file size
        file_writer.seek(4)
        old_size = int.from_bytes(file_writer.read(4), "little")
        file_writer.seek(0, os.SEEK_END)
        new_size = file_writer.tell() - 8
        file_writer.seek(4)
        file_writer.write(new_size.to_bytes(4, "little"))
    #Shift offsets in the only chunk that comes after textures
    with open("Game\\AUDO", "r+b") as file_writer:
        file_writer.seek(8)
        sound_count = int.from_bytes(file_writer.read(4), "little")
        for index in range(sound_count):
            file_writer.seek(12 + index*4)
            sound_offset = int.from_bytes(file_writer.read(4), "little")
            file_writer.seek(12 + index*4)
            file_writer.write((sound_offset + (new_size - old_size)).to_bytes(4, "little"))

def unpack_save_data():
    with open(f"Data\\{game_name}\\Save\\Save.sav", "r", encoding="utf8") as file_reader:
        save_data = file_reader.readlines()
    read_save_data(save_data)

def repack_save_data():
    #Don't repack if no changes were made
    if game_save == game_save_backup:
        return
    #Add a signature to the new save
    game_save["sFileName"] = save_signature
    #Open save data
    with open(f"Data\\{game_name}\\Save\\Save.sav", "r", encoding="utf8") as file_reader:
        save_data = file_reader.readlines()
    write_save_data(save_data)
    #Write the file in the proper location
    with open(save_file_path, "w", encoding="utf8") as file_writer:
        file_writer.writelines(save_data)

def read_save_data(save_data):
    for line_index in range(len(constant["SaveInfo"])):
        entry = constant["SaveInfo"][line_index].strip()
        if not entry:
            continue
        data_type = entry[0]
        value = save_data[line_index].strip()
        value = base64_to_string(value)
        if data_type.isupper():
            value = value.split(",")
            if value:
                value.pop()
            for index in range(len(value)):
                value[index] = read_save_value(data_type, line_index, value[index])
        else:
            value = read_save_value(data_type, line_index, value)
        game_save[entry] = value
        game_save_backup[entry] = value

def write_save_data(save_data):
    for line_index in range(len(constant["SaveInfo"])):
        entry = constant["SaveInfo"][line_index].strip()
        if not entry:
            continue
        data_type = entry[0]
        value = game_save[entry]
        if data_type.isupper():
            for index in range(len(value)):
                value[index] = write_save_value(data_type, line_index, value[index])
            value = ",".join(value)
            if value:
                value += ","
            else:
                value = "0" if game == LunaNights else "undefined"
        else:
            value = write_save_value(data_type, line_index, value)
        value = string_to_base64(value)
        save_data[line_index] = value + "\n"

def read_game_data():
    #String data
    with open("Game\\STRG", "rb") as file_reader:
        file_reader.seek(8)
        string_list_length = int.from_bytes(file_reader.read(4), "little")
        for string_index in range(string_list_length):
            file_reader.seek(12 + string_index*4)
            string_offset = int.from_bytes(file_reader.read(4), "little")
            file_reader.seek(string_offset - chunk_to_offset["STRG"])
            string_length = int.from_bytes(file_reader.read(4), "little")
            string = file_reader.read(string_length).decode("utf-8")
            game_strings[string_offset + 4] = string
    #Audio data
    with open("Game\\AUDO", "rb") as file_reader:
        file_reader.seek(8)
        audio_list_length = int.from_bytes(file_reader.read(4), "little")
        for audio_index in range(audio_list_length):
            file_reader.seek(12 + audio_index*4)
            audio_offset = int.from_bytes(file_reader.read(4), "little") - chunk_to_offset["AUDO"]
            file_reader.seek(audio_offset)
            wave_length = int.from_bytes(file_reader.read(4), "little")
            game_audio.append(Audio(wave_length))
    #Sound data
    with open("Game\\SOND", "rb") as file_reader:
        file_reader.seek(8)
        sound_list_length = int.from_bytes(file_reader.read(4), "little")
        for sound_index in range(sound_list_length):
            file_reader.seek(12 + sound_index*4)
            sound_offset = int.from_bytes(file_reader.read(4), "little") - chunk_to_offset["SOND"]
            file_reader.seek(sound_offset)
            name = game_strings[int.from_bytes(file_reader.read(4), "little")]
            file_reader.read(0xC)
            effects = int.from_bytes(file_reader.read(4), "little")
            volume = struct.unpack('!f', bytes.fromhex("{:08x}".format(int.from_bytes(file_reader.read(4), "little"))))[0]
            pitch = struct.unpack('!f', bytes.fromhex("{:08x}".format(int.from_bytes(file_reader.read(4), "little"))))[0]
            file_reader.read(4)
            audio_id = int.from_bytes(file_reader.read(4), "little")
            game_sounds[name] = Sound(effects, volume, pitch, audio_id)
    #Page item data
    with open("Game\\TPAG", "rb") as file_reader:
        file_reader.seek(8)
        page_item_list_length = int.from_bytes(file_reader.read(4), "little")
        for page_item_index in range(page_item_list_length):
            file_reader.seek(12 + page_item_index*4)
            page_item_offset = int.from_bytes(file_reader.read(4), "little")
            file_reader.seek(page_item_offset - chunk_to_offset["TPAG"])
            source_pos_x  = int.from_bytes(file_reader.read(2), "little")
            source_pos_y  = int.from_bytes(file_reader.read(2), "little")
            source_size_x = int.from_bytes(file_reader.read(2), "little")
            source_size_y = int.from_bytes(file_reader.read(2), "little")
            target_pos_x  = int.from_bytes(file_reader.read(2), "little")
            target_pos_x  = -(target_pos_x & 0x8000) | (target_pos_x & 0x7FFF)
            target_pos_y  = int.from_bytes(file_reader.read(2), "little")
            target_pos_y  = -(target_pos_y & 0x8000) | (target_pos_y & 0x7FFF)
            target_size_x = int.from_bytes(file_reader.read(2), "little")
            target_size_y = int.from_bytes(file_reader.read(2), "little")
            bound_size_x  = int.from_bytes(file_reader.read(2), "little")
            bound_size_y  = int.from_bytes(file_reader.read(2), "little")
            texture_id    = int.from_bytes(file_reader.read(2), "little")
            game_page_items[page_item_offset] = PageItem(source_pos_x, source_pos_y, source_size_x, source_size_y, target_pos_x, target_pos_y, target_size_x, target_size_y, bound_size_x, bound_size_y, texture_id)
    #Sprite data
    with open("Game\\SPRT", "rb") as file_reader:
        file_reader.seek(8)
        sprite_list_length = int.from_bytes(file_reader.read(4), "little")
        for sprite_index in range(sprite_list_length):
            file_reader.seek(12 + sprite_index*4)
            sprite_offset = int.from_bytes(file_reader.read(4), "little") - chunk_to_offset["SPRT"]
            file_reader.seek(sprite_offset)
            name = game_strings[int.from_bytes(file_reader.read(4), "little")]
            file_reader.read(0x48)
            if game == WonderLab:
                file_reader.read(8)
            page_item_list = []
            page_item_list_length = int.from_bytes(file_reader.read(4), "little")
            for page_item_index in range(page_item_list_length):
                page_item_offset = int.from_bytes(file_reader.read(4), "little")
                page_item_list.append(list(game_page_items).index(page_item_offset))
            game_sprites[name] = Sprite(page_item_list)
    #Tileset data
    with open("Game\\BGND", "rb") as file_reader:
        file_reader.seek(8)
        tileset_list_length = int.from_bytes(file_reader.read(4), "little")
        for tileset_index in range(tileset_list_length):
            file_reader.seek(12 + tileset_index*4)
            tileset_offset = int.from_bytes(file_reader.read(4), "little") - chunk_to_offset["BGND"]
            file_reader.seek(tileset_offset)
            name = game_strings[int.from_bytes(file_reader.read(4), "little")]
            file_reader.read(0xC)
            page_item_offset = int.from_bytes(file_reader.read(4), "little")
            game_tilesets[name] = TileSet(list(game_page_items).index(page_item_offset))
    #Object data
    with open("Game\\OBJT", "rb") as file_reader:
        file_reader.seek(8)
        object_list_length = int.from_bytes(file_reader.read(4), "little")
        for object_index in range(object_list_length):
            file_reader.seek(12 + object_index*4)
            #Object
            object_offset = int.from_bytes(file_reader.read(4), "little") - chunk_to_offset["OBJT"]
            file_reader.seek(object_offset)
            name            = game_strings[int.from_bytes(file_reader.read(4), "little")]
            sprite          = int.from_bytes(file_reader.read(4), "little")
            sprite          = -(sprite & 0x80000000) | (sprite & 0x7FFFFFFF)
            sprite          = None if sprite < 0 else list(game_sprites)[sprite]
            visible         = bool(int.from_bytes(file_reader.read(4), "little"))
            solid           = bool(int.from_bytes(file_reader.read(4), "little"))
            unknown         = bool(int.from_bytes(file_reader.read(4), "little"))
            persistent      = bool(int.from_bytes(file_reader.read(4), "little"))
            parent          = int.from_bytes(file_reader.read(4), "little")
            parent          = -(parent & 0x80000000) | (parent & 0x7FFFFFFF)
            texture_mask_id = int.from_bytes(file_reader.read(4), "little")
            texture_mask_id = -(texture_mask_id & 0x80000000) | (texture_mask_id & 0x7FFFFFFF)
            uses_physics    = bool(int.from_bytes(file_reader.read(4), "little"))
            is_sensor       = bool(int.from_bytes(file_reader.read(4), "little"))
            collision_shape = int.from_bytes(file_reader.read(4), "little")
            #Events
            events = {}
            events_backup = {}
            event_list_offset = object_offset + 0x50
            file_reader.seek(event_list_offset)
            event_list_length = int.from_bytes(file_reader.read(4), "little")
            for event_index in range(event_list_length):
                events[event_types[event_index]] = []
                events_backup[event_types[event_index]] = []
                file_reader.seek(event_list_offset + 4 + event_index*4)
                subevent_list_offset = int.from_bytes(file_reader.read(4), "little") - chunk_to_offset["OBJT"]
                file_reader.seek(subevent_list_offset)
                subevent_list_length = int.from_bytes(file_reader.read(4), "little")
                for subevent_index in range(subevent_list_length):
                    file_reader.seek(subevent_list_offset + 4 + subevent_index*4)
                    subevent_offset = int.from_bytes(file_reader.read(4), "little") - chunk_to_offset["OBJT"]
                    file_reader.seek(subevent_offset)
                    subtype_id = int.from_bytes(file_reader.read(4), "little")
                    file_reader.read(0x28)
                    action = int.from_bytes(file_reader.read(4), "little")
                    action = -(action & 0x80000000) | (action & 0x7FFFFFFF)
                    events[event_types[event_index]].append(Event(subtype_id, action))
                    events_backup[event_types[event_index]].append(Event(subtype_id, action))
            game_objects[name] = Object(sprite, visible, solid, unknown, persistent, parent, texture_mask_id, uses_physics, is_sensor, collision_shape, events)
            game_objects_backup[name] = Object(sprite, visible, solid, unknown, persistent, parent, texture_mask_id, uses_physics, is_sensor, collision_shape, events_backup)
    #Room data
    with open("Game\\ROOM", "rb") as file_reader:
        file_reader.seek(8)
        room_list_length = int.from_bytes(file_reader.read(4), "little")
        for room_index in range(room_list_length):
            file_reader.seek(12 + room_index*4)
            room_offset = int.from_bytes(file_reader.read(4), "little") - chunk_to_offset["ROOM"]
            file_reader.seek(room_offset)
            room_name = game_strings[int.from_bytes(file_reader.read(4), "little")]
            file_reader.read(0x2C)
            entity_list_offset = int.from_bytes(file_reader.read(4), "little") - chunk_to_offset["ROOM"]
            file_reader.read(0x24)
            layer_list_offset = int.from_bytes(file_reader.read(4), "little") - chunk_to_offset["ROOM"]
            #Entity data
            file_reader.seek(entity_list_offset)
            entity_list_length = int.from_bytes(file_reader.read(4), "little")
            for entity_index in range(entity_list_length):
                file_reader.seek(entity_list_offset + 4 + entity_index*4)
                entity_offset = int.from_bytes(file_reader.read(4), "little") - chunk_to_offset["ROOM"]
                file_reader.seek(entity_offset)
                x_pos           = int.from_bytes(file_reader.read(4), "little")
                y_pos           = int.from_bytes(file_reader.read(4), "little")
                type            = list(game_objects)[int.from_bytes(file_reader.read(4), "little")]
                instance_id     = int.from_bytes(file_reader.read(4), "little")
                creation_code   = int.from_bytes(file_reader.read(4), "little")
                creation_code   = -(creation_code & 0x80000000) | (creation_code & 0x7FFFFFFF)
                scale_x         = struct.unpack('!f', bytes.fromhex("{:08x}".format(int.from_bytes(file_reader.read(4), "little"))))[0]
                scale_y         = struct.unpack('!f', bytes.fromhex("{:08x}".format(int.from_bytes(file_reader.read(4), "little"))))[0]
                image_speed     = struct.unpack('!f', bytes.fromhex("{:08x}".format(int.from_bytes(file_reader.read(4), "little"))))[0]
                frame_index     = int.from_bytes(file_reader.read(4), "little")
                color           = "{:08x}".format(int.from_bytes(file_reader.read(4), "little")).upper()
                rotation        = struct.unpack('!f', bytes.fromhex("{:08x}".format(int.from_bytes(file_reader.read(4), "little"))))[0]
                pre_create_code = int.from_bytes(file_reader.read(4), "little")
                pre_create_code = -(pre_create_code & 0x80000000) | (pre_create_code & 0x7FFFFFFF)
                game_entities[instance_id] = Entity(x_pos, y_pos, type, creation_code, scale_x, scale_y, image_speed, frame_index, color, rotation, pre_create_code)
            #Tilemap data
            file_reader.seek(layer_list_offset)
            layer_list_length = int.from_bytes(file_reader.read(4), "little")
            for layer_index in range(layer_list_length):
                file_reader.seek(layer_list_offset + 4 + layer_index*4)
                layer_offset = int.from_bytes(file_reader.read(4), "little") - chunk_to_offset["ROOM"]
                file_reader.seek(layer_offset)
                layer_name = game_strings[int.from_bytes(file_reader.read(4), "little")]
                file_reader.read(4)
                layer_type = int.from_bytes(file_reader.read(4), "little")
                if layer_type != 4:
                    continue
                layer_z = int.from_bytes(file_reader.read(4), "little")
                file_reader.read(0x18)
                size_x  = int.from_bytes(file_reader.read(4), "little")
                size_y  = int.from_bytes(file_reader.read(4), "little")
                tile_data = []
                for tile_index in range(size_x*size_y):
                    tile_data.append(int.from_bytes(file_reader.read(4), "little"))
                game_tilemaps["_".join([room_name, layer_name])] = TileMap(layer_z, size_x, size_y, tile_data)

def write_game_data():
    #Page item data
    with open("Game\\TPAG", "r+b") as file_writer:
        file_writer.seek(8)
        page_item_list_length = int.from_bytes(file_writer.read(4), "little")
        for page_item_index in range(page_item_list_length):
            file_writer.seek(12 + page_item_index*4)
            page_item_offset = int.from_bytes(file_writer.read(4), "little")
            file_writer.seek(page_item_offset - chunk_to_offset["TPAG"])
            file_writer.write(game_page_items[page_item_offset].source_pos_x.to_bytes(2, "little"))
            file_writer.write(game_page_items[page_item_offset].source_pos_y.to_bytes(2, "little"))
            file_writer.write(game_page_items[page_item_offset].source_size_x.to_bytes(2, "little"))
            file_writer.write(game_page_items[page_item_offset].source_size_y.to_bytes(2, "little"))
            file_writer.write((game_page_items[page_item_offset].target_pos_x & 0xFFFF).to_bytes(2, "little"))
            file_writer.write((game_page_items[page_item_offset].target_pos_y & 0xFFFF).to_bytes(2, "little"))
            file_writer.write(game_page_items[page_item_offset].target_size_x.to_bytes(2, "little"))
            file_writer.write(game_page_items[page_item_offset].target_size_y.to_bytes(2, "little"))
            file_writer.write(game_page_items[page_item_offset].bound_size_x.to_bytes(2, "little"))
            file_writer.write(game_page_items[page_item_offset].bound_size_y.to_bytes(2, "little"))
            file_writer.write(game_page_items[page_item_offset].texture_id.to_bytes(2, "little"))
    #Sound data
    with open("Game\\SOND", "r+b") as file_writer:
        file_writer.seek(8)
        sound_list_length = int.from_bytes(file_writer.read(4), "little")
        for sound_index in range(sound_list_length):
            file_writer.seek(12 + sound_index*4)
            sound_offset = int.from_bytes(file_writer.read(4), "little") - chunk_to_offset["SOND"]
            file_writer.seek(sound_offset)
            name = game_strings[int.from_bytes(file_writer.read(4), "little")]
            file_writer.read(0xC)
            file_writer.write(game_sounds[name].effects.to_bytes(4, "little"))
            file_writer.write(struct.unpack('<I', struct.pack('<f', game_sounds[name].volume))[0].to_bytes(4, "little"))
            file_writer.write(struct.unpack('<I', struct.pack('<f', game_sounds[name].pitch))[0].to_bytes(4, "little"))
            file_writer.read(0x4)
            file_writer.write(game_sounds[name].audio_id.to_bytes(4, "little"))
    #Sprite data
    with open("Game\\SPRT", "r+b") as file_writer:
        file_writer.seek(8)
        sprite_list_length = int.from_bytes(file_writer.read(4), "little")
        for sprite_index in range(sprite_list_length):
            file_writer.seek(12 + sprite_index*4)
            sprite_offset = int.from_bytes(file_writer.read(4), "little") - chunk_to_offset["SPRT"]
            file_writer.seek(sprite_offset)
            name = game_strings[int.from_bytes(file_writer.read(4), "little")]
            file_writer.read(0x48)
            if game == WonderLab:
                file_writer.read(8)
            page_item_list_length = int.from_bytes(file_writer.read(4), "little")
            for page_item_index in range(page_item_list_length):
                page_item_offset = list(game_page_items)[game_sprites[name].page_items[page_item_index]]
                file_writer.write(page_item_offset.to_bytes(4, "little"))
    #Tileset data
    with open("Game\\BGND", "r+b") as file_writer:
        file_writer.seek(8)
        tileset_list_length = int.from_bytes(file_writer.read(4), "little")
        for tileset_index in range(tileset_list_length):
            file_writer.seek(12 + tileset_index*4)
            tileset_offset = int.from_bytes(file_writer.read(4), "little") - chunk_to_offset["BGND"]
            file_writer.seek(tileset_offset)
            name = game_strings[int.from_bytes(file_writer.read(4), "little")]
            file_writer.read(0xC)
            page_item_offset = list(game_page_items)[game_tilesets[name].page_item]
            file_writer.write(page_item_offset.to_bytes(4, "little"))
    #Object data
    with open("Game\\OBJT", "r+b") as file_writer:
        file_writer.seek(8)
        object_list_length = int.from_bytes(file_writer.read(4), "little")
        for object_index in range(object_list_length):
            file_writer.seek(12 + object_index*4)
            #Object
            object_offset = int.from_bytes(file_writer.read(4), "little") - chunk_to_offset["OBJT"]
            file_writer.seek(object_offset)
            name = game_strings[int.from_bytes(file_writer.read(4), "little")]
            sprite = game_objects[name].sprite
            sprite = list(game_sprites).index(sprite) if sprite in game_sprites else -1
            file_writer.write((sprite & 0xFFFFFFFF).to_bytes(4, "little"))
            file_writer.write(int(game_objects[name].visible).to_bytes(4, "little"))
            file_writer.write(int(game_objects[name].solid).to_bytes(4, "little"))
            file_writer.write(int(game_objects[name].unknown).to_bytes(4, "little"))
            file_writer.write(int(game_objects[name].persistent).to_bytes(4, "little"))
            file_writer.write((game_objects[name].parent & 0xFFFFFFFF).to_bytes(4, "little"))
            file_writer.write((game_objects[name].texture_mask_id & 0xFFFFFFFF).to_bytes(4, "little"))
            file_writer.write(int(game_objects[name].uses_physics).to_bytes(4, "little"))
            file_writer.write(int(game_objects[name].is_sensor).to_bytes(4, "little"))
            file_writer.write(game_objects[name].collision_shape.to_bytes(4, "little"))
            #Events
            event_list_offset = object_offset + 0x50
            file_writer.seek(event_list_offset)
            event_list_length = int.from_bytes(file_writer.read(4), "little")
            for event_index in range(event_list_length):
                file_writer.seek(event_list_offset + 4 + event_index*4)
                subevent_list_offset = int.from_bytes(file_writer.read(4), "little") - chunk_to_offset["OBJT"]
                file_writer.seek(subevent_list_offset)
                subevent_list_length = int.from_bytes(file_writer.read(4), "little")
                for subevent_index in range(subevent_list_length):
                    file_writer.seek(subevent_list_offset + 4 + subevent_index*4)
                    subevent_offset = int.from_bytes(file_writer.read(4), "little") - chunk_to_offset["OBJT"]
                    file_writer.seek(subevent_offset)
                    file_writer.write(game_objects[name].events[event_types[event_index]][subevent_index].subtype_id.to_bytes(4, "little"))
                    file_writer.read(0x28)
                    file_writer.write((game_objects[name].events[event_types[event_index]][subevent_index].action & 0xFFFFFFFF).to_bytes(4, "little"))
    #Room data
    with open("Game\\ROOM", "r+b") as file_writer:
        file_writer.seek(8)
        room_list_length = int.from_bytes(file_writer.read(4), "little")
        for room_index in range(room_list_length):
            file_writer.seek(12 + room_index*4)
            room_offset = int.from_bytes(file_writer.read(4), "little") - chunk_to_offset["ROOM"]
            file_writer.seek(room_offset)
            room_name = game_strings[int.from_bytes(file_writer.read(4), "little")]
            file_writer.read(0x2C)
            entity_list_offset = int.from_bytes(file_writer.read(4), "little") - chunk_to_offset["ROOM"]
            file_writer.read(0x24)
            layer_list_offset = int.from_bytes(file_writer.read(4), "little") - chunk_to_offset["ROOM"]
            #Entity data
            file_writer.seek(entity_list_offset)
            entity_list_length = int.from_bytes(file_writer.read(4), "little")
            for entity_index in range(entity_list_length):
                file_writer.seek(entity_list_offset + 4 + entity_index*4)
                entity_offset = int.from_bytes(file_writer.read(4), "little") - chunk_to_offset["ROOM"]
                file_writer.seek(entity_offset + 0xC)
                instance_id = int.from_bytes(file_writer.read(4), "little")
                file_writer.seek(entity_offset)
                file_writer.write(game_entities[instance_id].x_pos.to_bytes(4, "little"))
                file_writer.write(game_entities[instance_id].y_pos.to_bytes(4, "little"))
                file_writer.write(list(game_objects).index(game_entities[instance_id].type).to_bytes(4, "little"))
                file_writer.read(4)
                file_writer.write((game_entities[instance_id].creation_code & 0xFFFFFFFF).to_bytes(4, "little"))
                file_writer.write(struct.unpack('<I', struct.pack('<f', game_entities[instance_id].scale_x))[0].to_bytes(4, "little"))
                file_writer.write(struct.unpack('<I', struct.pack('<f', game_entities[instance_id].scale_y))[0].to_bytes(4, "little"))
                file_writer.write(struct.unpack('<I', struct.pack('<f', game_entities[instance_id].image_speed))[0].to_bytes(4, "little"))
                file_writer.write(game_entities[instance_id].frame_index.to_bytes(4, "little"))
                file_writer.write(int(game_entities[instance_id].color, 16).to_bytes(4, "little"))
                file_writer.write(struct.unpack('<I', struct.pack('<f', game_entities[instance_id].rotation))[0].to_bytes(4, "little"))
                file_writer.write((game_entities[instance_id].pre_create_code & 0xFFFFFFFF).to_bytes(4, "little"))
            #Tilemap data
            file_writer.seek(layer_list_offset)
            layer_list_length = int.from_bytes(file_writer.read(4), "little")
            for layer_index in range(layer_list_length):
                file_writer.seek(layer_list_offset + 4 + layer_index*4)
                layer_offset = int.from_bytes(file_writer.read(4), "little") - chunk_to_offset["ROOM"]
                file_writer.seek(layer_offset)
                layer_name = game_strings[int.from_bytes(file_writer.read(4), "little")]
                file_writer.read(4)
                layer_type = int.from_bytes(file_writer.read(4), "little")
                if layer_type != 4:
                    continue
                tilemap_name = "_".join([room_name, layer_name])
                file_writer.write(game_tilemaps[tilemap_name].layer_z.to_bytes(4, "little"))
                file_writer.read(0x18)
                size_x = game_tilemaps[tilemap_name].size_x
                size_y = game_tilemaps[tilemap_name].size_y
                file_writer.write(size_x.to_bytes(4, "little"))
                file_writer.write(size_y.to_bytes(4, "little"))
                for tile_index in range(size_x*size_y):
                    tile_id = game_tilemaps[tilemap_name].tile_data[tile_index]
                    file_writer.write(tile_id.to_bytes(4, "little"))

def get_page_item_by_index(index):
    if not type(index) is int:
        raise Exception(f"Page item index invalid: {index}")
    return game_page_items[list(game_page_items)[index]]

def get_save_file_path():
    global save_file_path
    appdata = os.getenv("LOCALAPPDATA")
    folder = game.save_directory
    used_index = []
    for file_path in glob.glob(os.path.join(appdata, folder, "*.sav")):
        file_name = os.path.split(os.path.splitext(file_path)[0])[-1]
        used_index.append(int(file_name[-1]))
    used_index.sort()
    save_index = None
    for index in range(3):
        if not index in used_index:
            save_index = index
            break
    if not save_index:
        raise Exception("No free save data slots found, please delete at least one of your in-game save files")
    save_name = f"game{save_index}.sav"
    save_file_path = os.path.join(appdata, folder, save_name)
    
def get_save_info_list():
    appdata = os.getenv("LOCALAPPDATA")
    folder = game.save_directory
    return glob.glob(os.path.join(appdata, folder, "*.txt"))
    
def get_save_file_list():
    save_file_list = []
    appdata = os.getenv("LOCALAPPDATA")
    folder = game.save_directory
    for file_path in glob.glob(os.path.join(appdata, folder, "*.sav")):
        with open(file_path, "r", encoding="utf8") as file_reader:
            save_data = file_reader.readlines()
        encoded_signature = string_to_base64(save_signature)
        if encoded_signature + "\n" in save_data:
            save_file_list.append(file_path)
    return save_file_list

def remove_entity(instance):
    game_entities[instance].x_pos = 0
    game_entities[instance].y_pos = 0
    game_entities[instance].scale_x = 0
    game_entities[instance].scale_y = 0

def transfer_object_code(recipient, giver):
    game_objects[recipient].sprite = game_objects_backup[giver].sprite
    for event_type in game_objects[recipient].events:
        for subevent in game_objects[recipient].events[event_type]:
            for subevent_backup in game_objects_backup[giver].events[event_type]:
                if subevent.subtype_id == subevent_backup.subtype_id:
                    subevent.action = subevent_backup.action

def convert_tilemaps_to_patches():
    for folder in os.listdir(f"Data\\{game_name}\\TileMap"):
        if os.path.isdir(f"Data\\{game_name}\\TileMap\\{folder}"):
            with open(f"Data\\{game_name}\\TileMap\\{folder}.tmp", "wb") as file_writer:
                for file in os.listdir(f"Data\\{game_name}\\TileMap\\{folder}"):
                    file_name = os.path.splitext(file)[0]
                    with open(f"Data\\{game_name}\\TileMap\\{folder}\\{file}") as file_reader:
                        new_tile_data = file_reader.read().strip().replace("\n", ",").split(",")
                    new_tile_data = [int(tile_id) for tile_id in new_tile_data]
                    old_tile_data = game_tilemaps[file_name].tile_data
                    for tile_index in range(len(old_tile_data)):
                        if old_tile_data[tile_index] != new_tile_data[tile_index]:
                            file_writer.write(list(game_tilemaps).index(file_name).to_bytes(4, "little"))
                            file_writer.write(tile_index.to_bytes(4, "little"))
                            file_writer.write(new_tile_data[tile_index].to_bytes(4, "little"))

def apply_tilemap_patch(patch):
    with open(f"Data\\{game_name}\\TileMap\\{patch}.tmp", "rb") as file_reader:
        file_reader.seek(0, os.SEEK_END)
        data_size = file_reader.tell()
        current_offset = 0
        while current_offset < data_size:
            file_reader.seek(current_offset)
            tilemap_index = int.from_bytes(file_reader.read(4), "little")
            tile_index = int.from_bytes(file_reader.read(4), "little")
            tile_id = int.from_bytes(file_reader.read(4), "little")
            game_tilemaps[list(game_tilemaps)[tilemap_index]].tile_data[tile_index] = tile_id
            current_offset += 0xC

def replace_tile_id(tilemap, coordinates, new_id):
    coordinates = re.match(r"([A-Z]+)([0-9]+)", coordinates, re.I).groups()
    x_pos = 0
    y_pos = int(coordinates[1])
    for char_index in range(len(coordinates[0])):
        depth = len(coordinates[0]) - 1 - char_index
        x_pos += (string.ascii_uppercase.index(coordinates[0][char_index]) + 1)*(26**depth)
    x_pos -= 1
    y_pos -= 1
    tile_index = x_pos + y_pos*game_tilemaps[tilemap].size_x
    game_tilemaps[tilemap].tile_data[tile_index] = new_id

def read_save_value(data_type, line_index, value):
    match data_type.lower():
        case 'l':
            return int(value) == line_index
        case 'b':
            return bool(int(value)) if value.isdigit() else True
        case 'i':
            return int(value) if value.isdigit() else value
        case 'f':
            return float(value)
        case 's':
            return value
        case _:
            raise Exception("Unknown data type")

def write_save_value(data_type, line_index, value):
    match data_type.lower():
        case 'l':
            return str(line_index) if value else "0"
        case 'b':
            return str(int(value))
        case 'i':
            return str(value)
        case 'f':
            return str(value)
        case 's':
            return value
        case _:
            raise Exception("Unknown data type")

def base64_to_string(base_64):
    return base64.b64decode(base_64).decode("utf-8")

def string_to_base64(string):
    return base64.b64encode(string.encode("utf-8")).decode("utf-8")