import Manager
import Cosmetic

def init():
    global instance_to_offset_up
    instance_to_offset_up = {
        100191:   64,
        100192:   48,
        100193:   56,
        100200:   56,
        100201:   64,
        100215:   56,
        100244: -144,
        100252:   48,
        100279:   64,
        100283:  104,
        100284:   48,
        100285:   48,
        100286:   72,
        100287:  -40,
        100322:   56,
        100457:  112,
        100461:  -72,
        100462:   88,
        100463:   72,
        100464:   40,
        100465:   72,
        100596:   64,
        100597:   48,
        100682:   72,
        100689:   56,
        100690:   72,
        100691:  272,
        100711:   48,
        100715:   32,
        100807:   80,
        100809:   56,
        100810:   96,
        100811:   96,
        100812:   32,
        100908:   48,
        100909:   48,
        100910:   48,
        101003:   96,
        101176:   48,
        101183:   48,
        101184:   48,
        101185:   48,
        101316:   32
    }
    global instance_exception_to_position
    instance_exception_to_position = {
        100691: (1952, 576)
    }
    global hardcoded_instance_to_item
    hardcoded_instance_to_item = {
        900000: "NSitem_0_70.-1",
        101175: "NSitem_0_95"
    }
    global grounded_item_to_offset_up
    grounded_item_to_offset_up = {
        "NSenemy_b_01": 48
    }
    global floating_item_offset_up
    floating_item_offset_up = 56
    global ability_order
    ability_order = [
        "NSitem_0_80",
        "NSitem_0_81",
        "NSitem_0_82",
        "NSitem_0_83",
        "NSitem_0_84"
    ]
    global special_check_to_requirement
    special_check_to_requirement = {
        "To_Stage_05_00_Start": "Stage_04_30_1_0_Right"
    }
    global macro_to_requirements
    macro_to_requirements = {
        "Height": ["NSitem_0_81", "Flight"],
        "Flight": [["NSitem_0_70.-1", "NSitem_0_82"]]
    }
    global map_colors
    map_colors = [
        "#71a839",
        "#a83939",
        "#a88d39",
        "#3971a8",
        "#7139a8",
        "#a83971"
    ]
    global tileset_to_tile_blacklist
    tileset_to_tile_blacklist = {
        "stage01_map":  [275, 276, 609, 610, 626, 627, 645, 646, 647, 648, 665, 666, 667, 668],
        "stage01_map2": [275, 276, 609, 610, 626, 627, 645, 646, 647, 648, 665, 666, 667, 668],
        "stage02_map":  [262, 263],
        "stage02_map2": [262, 263],
        "stage04_map":  [ 56,  57, 351, 352, 370, 371, 372, 373, 390, 391, 392, 393],
        "stage04_map2": [ 56,  57, 351, 352, 370, 371, 372, 373, 390, 391, 392, 393]
    }
    global dialogue_skip
    dialogue_skip = [
        "#s73",
        "#s74"
    ]

def apply_default_tweaks():
    pass

def apply_key_logic_tweaks():
    #Work around the invisible bathtub wall in stage 1
    Manager.apply_tilemap_patch("TimestopWallFix")
    
    Manager.game_entities[100126].x_pos = 6219
    Manager.game_entities[100126].y_pos = 1552
    Manager.game_entities[100126].scale_x = 1/3
    Manager.game_entities[100126].scale_y = 1.5
    Manager.game_entities[100126].type = "boss_brock_ob"
    Manager.game_entities[100126].creation_code = -1
    #Add a platform to the stage 2 blue door
    Manager.apply_tilemap_patch("BlueDoorShortcut")
    #Create a work around for the Nitori cutscene softlock
    Manager.apply_tilemap_patch("LibraryNitoriFix")
    
    Manager.game_entities[100513].x_pos = 4128
    Manager.game_entities[100513].y_pos = 1312
    Manager.game_entities[100513].type = "collision_viewout"
    Manager.game_entities[100512].x_pos = 4160
    Manager.game_entities[100512].y_pos = 1312
    Manager.game_entities[100512].type = "collision_viewout"
    #Add a block to the stage 5 purple key check
    Manager.apply_tilemap_patch("PurpleKeyAntiSoftlock")

def apply_progressive_ability_tweaks():
    #Update textures
    page_item = Manager.get_page_item_by_index(1415)
    page_item.source_pos_x  = 138
    page_item.source_pos_y  = 616
    page_item.source_size_x = 32
    page_item.source_size_y = 32
    page_item.target_pos_x  = 0
    page_item.target_pos_y  = 0
    page_item.target_size_x = 32
    page_item.target_size_y = 32
    Cosmetic.import_texture(1415)
    
    page_item = Manager.get_page_item_by_index(1315)
    page_item.source_pos_x  = 174
    page_item.source_pos_y  = 627
    page_item.source_size_x = 240
    page_item.source_size_y = 50
    page_item.target_pos_x  = 0
    page_item.target_pos_y  = 0
    page_item.target_size_x = 240
    page_item.target_size_y = 50
    Cosmetic.import_texture(1315)
    #Update texture pointers
    Manager.game_objects["NSitem_0_81"].sprite = "item_sliding"
    Manager.game_objects["NSitem_0_82"].sprite = "item_sliding"
    Manager.game_objects["NSitem_0_83"].sprite = "item_sliding"
    Manager.game_objects["NSitem_0_84"].sprite = "item_sliding"
    
    Manager.game_sprites["item_vision"].page_items[15] = 1315
    Manager.game_sprites["item_vision"].page_items[16] = 1315
    Manager.game_sprites["item_vision"].page_items[17] = 1315
    Manager.game_sprites["item_vision"].page_items[18] = 1315
    #Update descriptions
    skill_up_text = "You got SKILL UP\nYou can now use a new ability."
    Cosmetic.set_text_entry("@79", skill_up_text)
    Cosmetic.set_text_entry("@80", skill_up_text)
    Cosmetic.set_text_entry("@81", skill_up_text)
    Cosmetic.set_text_entry("@82", skill_up_text)
    Cosmetic.set_text_entry("@83", skill_up_text)

def apply_world_color_rando_tweaks():
    pass

def apply_enemy_color_rando_tweaks():
    pass

def apply_chara_color_rando_tweaks():
    Cosmetic.import_texture(6643)

def swap_skeleton_sprites():
    Manager.game_sprites["skeleton_run"].page_items    = Manager.game_sprites["skeleton_run_china"].page_items
    Manager.game_sprites["skeleton_bullet"].page_items = Manager.game_sprites["skeleton_bullet_china"].page_items
    Manager.game_sprites["skeleton_chage"].page_items  = Manager.game_sprites["skeleton_chage_china"].page_items
    Manager.game_sprites["skeleton_attack"].page_items = Manager.game_sprites["skeleton_attack_china"].page_items
    Manager.game_sprites["skeleton_attack"].page_items.append(Manager.game_sprites["skeleton_attack"].page_items[-1])
    Manager.game_sprites["skeleton_stand"].page_items  = Manager.game_sprites["skeleton_stand_china"].page_items
    Manager.game_sounds["s1021_dokuro"].audio_id = 141