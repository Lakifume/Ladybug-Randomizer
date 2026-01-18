import Manager
import Gameplay
import Cosmetic

def init():
    global save_directory
    save_directory = "touhou_luna_nights"
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
    global map_colors
    map_colors = [
        "#71a839",
        "#a83939",
        "#a88d39",
        "#3971a8",
        "#7139a8",
        "#a83971"
    ]
    global tracker_to_save_watch
    tracker_to_save_watch = {
        "NSitem_0_70.-1": "iTimeBonus",
        "NSitem_0_80":    "iAbilityIndex",
        "NSitem_0_81":    "iAbilityIndex",
        "NSitem_0_82":    "iAbilityIndex",
        "NSitem_0_83":    "iAbilityIndex",
        "NSitem_0_84":    "iSpecialMode",
        "NSitem_0_90":    "lHasRedKey",
        "NSitem_0_91":    "lHasYellowKey",
        "NSitem_0_92":    "lHasGreenKey",
        "NSitem_0_93":    "lHasBlueKey",
        "NSitem_0_94":    "lHasPurpleKey",
        "NSitem_0_95":    "lHasIceMagatama",
        "NSenemy_0_08":   "bMeilingDefeatedFlag",
        "NSenemy_0_12":   "bMarisaDefeatedFlag",
        "NSenemy_0_28":   "bPatchouliDefeatedFlag",
        "NSenemy_0_46":   "bRemiliaDefeatedFlag",
        "NSenemy_0_75":   "bFileClearFlag",
        "NSenemy_0_3a":   "bCirnoDefeatedFlag",
        "NSenemy_0_0a":   "bFileAllClearFlag"
    }

def apply_default_tweaks():
    #Fix the purple key typo
    Cosmetic.set_text_entry("@93", "You got PURPLE KEY\nYou can now open doors with a purple aura.")

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
    #Disable the library Nitori cutscene
    Manager.game_save["bGemPowerTutorialFlag"] = True
    #Add a block to the stage 5 purple key check
    Manager.apply_tilemap_patch("PurpleKeyReturn")

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
    Manager.game_objects_backup["NSitem_0_81"].sprite = "item_sliding"
    Manager.game_objects_backup["NSitem_0_82"].sprite = "item_sliding"
    Manager.game_objects_backup["NSitem_0_83"].sprite = "item_sliding"
    Manager.game_objects_backup["NSitem_0_84"].sprite = "item_sliding"
    
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
    #Neutralize the fog color of the Flandre fight
    Cosmetic.import_texture(6643)

def set_reverse_start():
    Manager.game_save["iSpawnPosX"]     = 6496
    Manager.game_save["iSpawnPosY"]     = 1296
    Manager.game_save["iSpawnStage"]    = 9
    Gameplay.current_available_doors[0] = "Stage_04_19_Start"
    #Disable some flags
    Manager.game_save["bNitoriShipIntroFlag"] = True
    Manager.game_save["bAkyuuIntroFlag"]      = True
    Manager.game_save["bNitoriIntroFlag"]     = True
    Manager.game_save["bShopTutorialFlag"]    = True
    Manager.game_save["bStage1FirstLoadFlag"] = True
    Manager.game_save["bStage2FirstLoadFlag"] = True
    Manager.game_save["bStage3FirstLoadFlag"] = True
    Manager.game_save["bStage4FirstLoadFlag"] = True
    Manager.game_save["bStage5FirstLoadFlag"] = True
    Manager.game_save["bStage6FirstLoadFlag"] = True
    #Add Nitori's item in front of the shop
    Manager.game_entities[100028].x_pos = 4256
    Manager.game_entities[100028].y_pos = 1024
    Manager.game_entities[100028].type = "NSitem_0_70"
    Manager.game_entities[100028].creation_code = -1
    #Allow going from the save back up to Remilia
    Manager.apply_tilemap_patch("SavePointToRemilia")
    #Allow going from the chainsaw check to Marisa
    Manager.apply_tilemap_patch("LowerFloorToMarisa")
    #Add a fake slide requirement
    for door in Manager.constant["RoomLogic"]["Stage_04_19"]:
        if "0_0_Right" in Manager.constant["RoomLogic"]["Stage_04_19"][door]:
            Manager.constant["RoomLogic"]["Stage_04_19"][door]["0_0_Right"] = ["NSitem_0_80"]

def set_all_keys_required():
    Manager.apply_tilemap_patch("AllKeysRequired")
    #Add 1 of each door back-to-back
    Manager.game_entities[101295].x_pos = 3146
    Manager.game_entities[101295].y_pos = 576
    Manager.game_entities[101295].type = "door00"
    Manager.game_entities[101295].creation_code = -1
    
    Manager.game_entities[101308].x_pos = 3170
    Manager.game_entities[101308].y_pos = 576
    Manager.game_entities[101308].type = "door00"
    Manager.game_entities[101308].creation_code = 1850
    
    Manager.game_entities[101311].x_pos = 3194
    Manager.game_entities[101311].y_pos = 576
    Manager.game_entities[101311].type = "door00"
    Manager.game_entities[101311].creation_code = 1884
    
    Manager.game_entities[101307].x_pos = 3218
    Manager.game_entities[101307].y_pos = 576
    Manager.game_entities[101307].type = "door00"
    Manager.game_entities[101307].creation_code = 1847
    
    Manager.game_entities[101296].x_pos = 3242
    Manager.game_entities[101296].y_pos = 576
    Manager.game_entities[101296].type = "door00"
    Manager.game_entities[101296].creation_code = 2035

def unlock_extra_stage():
    Manager.game_save["bFileClearFlag"] = True
    special_check_to_requirement.clear()

def set_one_hit_ko_mode():
    Manager.game_save["iSpecialMode"] = 2

def set_dash_spike_start():
    Manager.game_save["lHasDashSpike"]        = True
    Manager.game_save["bStage1FirstLoadFlag"] = True
    Manager.game_save["iSpecialMode"]         = 1
    Gameplay.starting_items.append("NSitem_0_84")

def swap_skeleton_sprites():
    Manager.game_sprites["skeleton_run"].page_items    = Manager.game_sprites["skeleton_run_china"].page_items
    Manager.game_sprites["skeleton_bullet"].page_items = Manager.game_sprites["skeleton_bullet_china"].page_items
    Manager.game_sprites["skeleton_chage"].page_items  = Manager.game_sprites["skeleton_chage_china"].page_items
    Manager.game_sprites["skeleton_attack"].page_items = Manager.game_sprites["skeleton_attack_china"].page_items
    Manager.game_sprites["skeleton_attack"].page_items.append(Manager.game_sprites["skeleton_attack"].page_items[-1])
    Manager.game_sprites["skeleton_stand"].page_items  = Manager.game_sprites["skeleton_stand_china"].page_items
    Manager.game_sounds["s1021_dokuro"].audio_id = 141