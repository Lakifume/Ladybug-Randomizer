import Manager
import LunaNights
import WonderLab

import random
import copy
import os
import re
import colorsys
from PIL import Image
from enum import Enum

class ShiftType(Enum):
    Simple = 1
    RGB    = 3
    RGBCMY = 6

def init():
    global music_replacement
    music_replacement = {}
    global music_to_name
    music_to_name = {}
    global texture_to_image
    texture_to_image = {}
    global page_items_done
    page_items_done = []
    global starting_words
    starting_words = []
    global previous_to_next_words
    previous_to_next_words = {}
    global texture_padding
    texture_padding = 2

def randomize_background_music(game_path):
    for group in Manager.constant["MusicGroup"]:
        new_list = copy.deepcopy(group)
        random.shuffle(new_list)
        new_dict = dict(zip(group, new_list))
        music_replacement.update(new_dict)
    for item in music_replacement:
        os.rename(game_path + "\\data\\" + music_replacement[item] + ".ogg", game_path + "\\data\\" + item + ".bak")
    for item in music_replacement:
        os.rename(game_path + "\\data\\" + item + ".bak", game_path + "\\data\\" + item + ".ogg")

def update_music_names():
    for item in music_replacement:
        if is_text_entry(item):
            music_to_name[item] = get_text_entry(item)
    for item in music_to_name:
        set_text_entry(item, music_to_name[music_replacement[item]])

def randomize_texture_colors(texture_type):
    for group in Manager.constant[texture_type]:
        shift_type = ShiftType[group["ShiftType"]]
        #Reroll color schemes
        color_scheme = []
        for index in range(shift_type.value):
            color_scheme.append(random.random())
        color_blacklist = group["Blacklist"]
        for item in group["Textures"]:
            #Handle multiple types of texture pointers
            if item in Manager.game_tilesets:
                tile_blacklist = []
                if item in Manager.game.tileset_to_tile_blacklist:
                    tile_blacklist = Manager.game.tileset_to_tile_blacklist[item]
                apply_scheme_to_page_item(Manager.game_tilesets[item].page_item, color_scheme, color_blacklist + tile_blacklist) 
            elif item in Manager.game_sprites:
                for page_item in Manager.game_sprites[item].page_items:
                    apply_scheme_to_page_item(page_item, color_scheme, color_blacklist) 
            else:
                apply_scheme_to_page_item(item, color_scheme, color_blacklist)

def import_texture(page_item_index):
    page_item = Manager.get_page_item_by_index(page_item_index)
    source_pos_x  = page_item.source_pos_x
    source_pos_y  = page_item.source_pos_y
    source_size_x = page_item.source_size_x
    source_size_y = page_item.source_size_y
    texture_id    = page_item.texture_id
    #Load images
    old_image, old_pixels = load_game_texture(texture_id)
    new_image  = Image.open("Data\\" + Manager.game_name + "\\Texture\\" + str(page_item_index) + ".png")
    if new_image.size != (source_size_x, source_size_y):
        raise Exception("Texture size mismatches page item: " + str(page_item_index))
    new_pixels = new_image.load()
    #Target specific region
    for x in range(source_pos_x - texture_padding, source_pos_x + source_size_x + texture_padding):
        for y in range(source_pos_y - texture_padding, source_pos_y + source_size_y + texture_padding):
            new_x = min(max(x - source_pos_x, 0), source_size_x - 1)
            new_y = min(max(y - source_pos_y, 0), source_size_y - 1)
            old_pixels[x, y] = new_pixels[new_x, new_y]

def apply_scheme_to_page_item(page_item_index, color_scheme, blacklist):
    page_item     = Manager.get_page_item_by_index(page_item_index)
    source_pos_x  = page_item.source_pos_x
    source_pos_y  = page_item.source_pos_y
    source_size_x = page_item.source_size_x
    source_size_y = page_item.source_size_y
    texture_id    = page_item.texture_id
    color_depth   = len(color_scheme)
    #Check page item list
    if (source_pos_x, source_pos_y, source_size_x, source_size_y, texture_id) in page_items_done:
        return
    image, pixels = load_game_texture(texture_id)
    #Target specific region
    for x in range(source_pos_x - texture_padding, source_pos_x + source_size_x + texture_padding):
        for y in range(source_pos_y - texture_padding, source_pos_y + source_size_y + texture_padding):
            #Check padding
            try:
                pixels[x, y]
            except IndexError:
                continue
            #Check opcaity
            if pixels[x, y][3] == 0:
                continue
            #Check tile blacklist
            if (x - source_pos_x)//36 + (y - source_pos_y)//36*(source_size_x//36) in blacklist:
                continue
            old_rgb = (pixels[x, y][0]/255, pixels[x, y][1]/255, pixels[x, y][2]/255)
            #Check color blacklist
            if rgb_to_hex(old_rgb) in blacklist:
                continue
            old_hsv = colorsys.rgb_to_hsv(old_rgb[0], old_rgb[1], old_rgb[2])
            #Check saturation
            if old_hsv[1] == 0:
                continue
            hue_360 = old_hsv[0]*360
            for index in range(color_depth):
                #Select by hue components
                if index*(360/color_depth) <= (hue_360 + 180/color_depth)%360 < (index + 1)*(360/color_depth):
                    new_rgb = colorsys.hsv_to_rgb((old_hsv[0] + color_scheme[index])%1, old_hsv[1], old_hsv[2])
                    pixels[x,y] = (round(new_rgb[0]*255), round(new_rgb[1]*255), round(new_rgb[2]*255), pixels[x, y][3])
                    break
    #Update page item list
    page_items_done.append((source_pos_x, source_pos_y, source_size_x, source_size_y, texture_id))

def load_game_texture(texture_id):
    if not texture_id in texture_to_image:
        image = Image.open("Game\\Export\\" + str(texture_id) + ".png")
        texture_to_image[texture_id] = (image, image.load())
    return texture_to_image[texture_id]

def save_game_textures():
    for texture_id in texture_to_image:
        texture_to_image[texture_id][0].save("Game\\Export\\" + str(texture_id) + ".png")
    texture_to_image.clear()

def rgb_to_hex(rgb):
    hex_string = "#"
    for comp in rgb:
        comp = round(comp*255)
        hex_string += "{:02x}".format(comp)
    return hex_string

def randomize_dialogues():
    #Gather indexes of dialogue lines
    dialogue_line_indexes = []
    is_dialogue_range = False
    for line_index in range(len(Manager.game_text)):
        line = Manager.game_text[line_index].strip()
        if line in Manager.game.dialogue_skip:
            continue
        if line[0:4] == "#end":
            is_dialogue_range = False
        if is_dialogue_range and line[0] != "$":
            dialogue_line_indexes.append(line_index)
        if line[0:2] in ["#s", "#t"]:
            try:
                int(line[2])
            except ValueError:
                continue
            is_dialogue_range = True
    #Gather info about the sentence structure
    for line_index in dialogue_line_indexes:
        line = Manager.game_text[line_index].strip()
        sentences = string_to_sentences(line)
        for sentence in sentences:
            words = sentence_to_words(sentence)
            for word_index in range(len(words)):
                if word_index == 0:
                    starting_words.append(words[word_index])
                previous_words = []
                for num in range(min(word_index, 2)):
                    previous_words.insert(0, words[word_index - (num + 1)])
                if previous_words:
                    previous_words = "_".join(previous_words)
                    if not previous_words in previous_to_next_words:
                        previous_to_next_words[previous_words] = []
                    previous_to_next_words[previous_words].append(words[word_index])
    #Backup lists
    global starting_words_backup
    starting_words_backup = copy.deepcopy(starting_words)
    global previous_to_next_words_backup
    previous_to_next_words_backup = copy.deepcopy(previous_to_next_words)
    #Create new dialogue lines
    dialogue_lines = []
    while len(dialogue_lines) < len(dialogue_line_indexes):
        sentence = generate_sentence()
        if len(sentence) <= 5 and random.random() <= 0.25:
            sentence.extend(generate_sentence())
        for num in range(len(sentence)//7):
            sentence.insert((num + 1)*7 - 1, "*")
        sentence = " ".join(sentence)
        sentence = sentence.replace(" * ", "*")
        dialogue_lines.append(sentence)
    #Apply new dialogue to the game text
    for line_index in dialogue_line_indexes:
        line = dialogue_lines[0]
        dialogue_lines.remove(line)
        Manager.game_text[line_index] = line + "\n"
    #Ensure that Nitrori gives the item in the first encounter as it checks for specific text
    if Manager.game == LunaNights:
        nitori_dialogue = get_text_entry("#s05")
        nitori_dialogue += "\n$0303#nitori_ob\nYup, business."
        set_text_entry("#s05", nitori_dialogue)

def generate_sentence():
    if not starting_words:
        starting_words.extend(starting_words_backup)
    starting_word = random.choice(starting_words)
    starting_words.remove(starting_word)
    sentence = [starting_word]
    while True:
        if sentence[-1][-1] in [".", "!", "?", "~", ")", "]"]:
            if sentence[0][0] == "(":
                sentence[-1] = sentence[-1][:-1] + ")"
            elif sentence[-1][-1] == ")":
                sentence[-1] = sentence[-1][:-1] + "."
            break
        previous_words = []
        for num in range(min(len(sentence), 2)):
            previous_words.insert(0, sentence[- (num + 1)])
        previous_words = "_".join(previous_words)
        if not previous_words in previous_to_next_words:
            if not sentence[-1][-1] in [",", ":", ";"]:
                sentence[-1] += "."
            break
        if not previous_to_next_words[previous_words]:
            previous_to_next_words[previous_words].extend(previous_to_next_words_backup[previous_words])
        next_word = random.choice(previous_to_next_words[previous_words])
        previous_to_next_words[previous_words].remove(next_word)
        sentence.append(next_word)
    return sentence

def string_to_sentences(string):
    capitals = "([A-Z])"
    punctuation = "(\.|\!|\?|\~|\)|\])"
    string = re.sub(punctuation + " " + capitals, "\\1<stop> \\2", string)
    sentences = string.split("<stop>")
    sentences = [s.strip() for s in sentences]
    return sentences

def sentence_to_words(sentence):
    sentence = sentence.replace("*", " ")
    sentence = sentence.split(" ")
    words = []
    for word in sentence:
        if word:
            words.append(word)
    return words

def is_text_entry(string):
    if Manager.game_text.count(string + "\n") != 1:
        return False
    if string[0] in ["@", "#", "+", "="]:
        return True
    if string[0:3] == "bgm":
        return True
    if string[0:4] == "boss":
        return True
    return False

def get_text_entry(entry):
    if not is_text_entry(entry):
        raise Exception("Text entry invalid")
    start_index = Manager.game_text.index(entry + "\n") + 1
    text = ""
    while start_index < len(Manager.game_text):
        current_text = Manager.game_text[start_index].strip()
        if not current_text or current_text == "#end" or is_text_entry(current_text):
            break
        text += current_text + "\n"
        start_index += 1
    return text.strip()

def set_text_entry(entry, new_text):
    if not is_text_entry(entry):
        raise Exception("Text entry invalid")
    start_index = Manager.game_text.index(entry + "\n") + 1
    while start_index < len(Manager.game_text):
        current_text = Manager.game_text[start_index].strip()
        if not current_text or current_text == "#end" or is_text_entry(current_text):
            break
        Manager.game_text.pop(start_index)
    text_lines = new_text.split("\n")
    for line_index in range(len(text_lines) -1, -1, -1):
        line = text_lines[line_index] + "\n"
        Manager.game_text.insert(start_index, line)