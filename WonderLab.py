import Manager
import Cosmetic

def init():
    global instance_to_offset_up
    instance_to_offset_up = {
        100050:  24,
        100051:  56,
        100098:  96,
        100132:  88,
        100137:   0,
        100142: 112,
        100143: 112,
        100155:  96,
        100206:  80,
        100207:  32,
        100208:  96,
        100214:  96,
        100216: 104,
        100257:  80,
        100258: 104,
        100267:  80,
        100359:   0,
        100362: 120,
        100363:  80,
        100377:  64,
        100432:  48,
        100433:  64,
        100434:  96,
        100435: 104,
        100436:  56,
        100483:  72,
        100488:  80,
        100502:  88,
        100510:  64,
        100511:   0,
        100583:  72,
        100584:   0,
        100716:  40,
        100717:  40,
        100718:  40,
        100719:  40,
        100720:  40,
        100732:  72,
        100733: 120,
        100734:  32,
        100735: 104,
        100741:  32,
        100765:  96,
        100859:  88,
        100860:  56,
        100861:  48,
        100862:   0,
        100865:  80,
        100866:  96,
        100867:  64,
        100870:   0,
        100873:  56,
        100932:  88,
        100933: 112,
        100977:  64,
        101004:   0,
        101012:  88,
        101013:  48,
        101014:  88,
        101015: 112,
        101094:  48,
        101095:  48,
        101096:  72,
        101097: 120,
        101131:   0,
        101183: 176,
        101184: 152,
        101290:  56
    }
    global instance_exception_to_position
    instance_exception_to_position = {
        100511: (2736, 3856),
        100870: (9504, 2016)
    }
    global hardcoded_instance_to_item
    hardcoded_instance_to_item = {}
    global grounded_item_to_offset_up
    grounded_item_to_offset_up = {
        "rock_switch_ob": 0,
        "NSitem_0_91": 40
    }
    global floating_item_offset_up
    floating_item_offset_up = 56
    global ability_order
    ability_order = [
        "NSitem_0_81",
        "NSitem_0_82",
        "NSitem_0_83",
        "NSitem_0_84",
        "NSitem_0_85"
    ]
    global special_check_to_requirement
    special_check_to_requirement = {
        "Stage_00_18_0_0_Bottom": "Stage_02_47_0_1_Right",
        "Stage_02_21_0_0_Left":   "Stage_02_47_0_1_Right"
    }
    global macro_to_requirements
    macro_to_requirements = {
        "Height": ["NSitem_0_83", "NSitem_0_85"],
        "FSlide": [["NSitem_0_81", "NSitem_0_82"]],
        "SoulsK": [["NSitem_0_91.288", "NSitem_0_91.289", "NSitem_0_91.290", "NSitem_0_91.291", "NSitem_0_91.292"]]
    }
    global map_colors
    map_colors = [
        "#71a839",
        "#a83939",
        "#3971a8",
        "#a88d39",
        "#7139a8",
        "#1a805d"
    ]
    global tileset_to_tile_blacklist
    tileset_to_tile_blacklist = {}
    global dialogue_skip
    dialogue_skip = [
        "#s0a",
        "#s0b",
        "#s94",
        "#s99"
    ]

def apply_default_tweaks():
    pass

def apply_key_logic_tweaks():
    #Remove the early fire barrels
    Manager.remove_entity(100102)
    Manager.remove_entity(100103)
    #Remove boss doors to prevent softlocks
    Manager.game_objects["boss_brock_ob"].sprite = -1
    #Replace the stage 1 50x jumps platform by a soul key gate
    Manager.game_entities[100124].y_pos += 16
    Manager.game_entities[100124].type = "stage02_fifthkey_move_platform"
    
    Manager.game_entities[100050].x_pos = 7520
    Manager.game_entities[100050].y_pos = 2336
    instance_to_offset_up[100050] += 40
    
    Manager.apply_tilemap_patch("Stage1SoulGate")
    
    Cosmetic.import_texture(7932)
    Cosmetic.import_texture(7933)
    #Edit stage 4 to work around the parn kill cutscene crash
    Manager.apply_tilemap_patch("ParnKillCrashFix")
    
    Manager.game_entities[100860].x_pos = 10528
    instance_to_offset_up[100860] += 64
    
    Manager.game_entities[100858].x_pos = 6352
    Manager.game_entities[100858].y_pos = 1920
    Manager.game_entities[100858].type = "rock_door_ob"
    Manager.game_entities[100858].creation_code = 328
    
    Manager.game_entities[100877].x_pos = 7600
    Manager.game_entities[100877].y_pos = 2688
    Manager.game_entities[100877].type = "gimmick_shutter"
    Manager.game_entities[100877].creation_code = 136
    
    Manager.game_entities[100791].x_pos = 7600
    Manager.game_entities[100791].y_pos = 3744
    Manager.game_entities[100791].type = "gimmick_shutter"
    Manager.game_entities[100791].creation_code = 136
    #Add a platform to the stage 5 high jump check
    Manager.apply_tilemap_patch("HighJumpAntiSoftlock")
    #Add a platform to the stage 6 bow check
    Manager.apply_tilemap_patch("ApollonAntiSoftlock")
    #Block off the stage 6 teal gate shortcut
    Manager.apply_tilemap_patch("TealShortcutRemoval")

def apply_progressive_ability_tweaks():
    #Update textures
    page_item = Manager.get_page_item_by_index(3655)
    page_item.source_pos_x  = 14
    page_item.source_pos_y  = 767
    page_item.source_size_x = 32
    page_item.source_size_y = 32
    page_item.target_pos_x  = 0
    page_item.target_pos_y  = 0
    page_item.target_size_x = 32
    page_item.target_size_y = 32
    Cosmetic.import_texture(3655)
    
    page_item = Manager.get_page_item_by_index(3513)
    page_item.source_pos_x  = 14
    page_item.source_pos_y  = 803
    page_item.source_size_x = 240
    page_item.source_size_y = 50
    page_item.target_pos_x  = 0
    page_item.target_pos_y  = 0
    page_item.target_size_x = 240
    page_item.target_size_y = 50
    Cosmetic.import_texture(3513)
    
    page_item = Manager.get_page_item_by_index(3551)
    page_item.source_pos_x  = 50
    page_item.source_pos_y  = 767
    page_item.source_size_x = 32
    page_item.source_size_y = 32
    page_item.target_pos_x  = 0
    page_item.target_pos_y  = 0
    page_item.target_size_x = 32
    page_item.target_size_y = 32
    Cosmetic.import_texture(3551)
    
    page_item = Manager.get_page_item_by_index(3507)
    page_item.source_pos_x  = 258
    page_item.source_pos_y  = 777
    page_item.source_size_x = 240
    page_item.source_size_y = 50
    page_item.target_pos_x  = 0
    page_item.target_pos_y  = 0
    page_item.target_size_x = 240
    page_item.target_size_y = 50
    Cosmetic.import_texture(3507)
    #Update texture pointers
    Manager.game_objects["NSitem_0_81"].sprite = "item_sliding"
    Manager.game_objects["NSitem_0_83"].sprite = "item_sliding"
    Manager.game_objects["NSitem_0_84"].sprite = "item_sliding"
    
    Manager.game_sprites["item_vision"].page_items[15] = 3513
    Manager.game_sprites["item_vision"].page_items[17] = 3513
    Manager.game_sprites["item_vision"].page_items[18] = 3513
    #Update descriptions
    skill_up_text = "Ability Upgrade\nYou can now use a new ability."
    final_up_text = "Final Ability\nYou can now use every ability."
    Cosmetic.set_text_entry("@80", skill_up_text)
    Cosmetic.set_text_entry("@81", skill_up_text)
    Cosmetic.set_text_entry("@82", skill_up_text)
    Cosmetic.set_text_entry("@83", skill_up_text)
    Cosmetic.set_text_entry("@84", final_up_text)

def apply_world_color_rando_tweaks():
    #Expand background textures to cover the whole view
    page_item = Manager.get_page_item_by_index(7011)
    page_item.source_pos_y  += 364
    page_item.source_size_x += 160
    page_item.target_size_x += 160
    page_item.bound_size_x  += 160
    page_item.target_pos_x  -= 80
    Cosmetic.import_texture(7011)
    
    page_item = Manager.get_page_item_by_index(7920)
    page_item.source_pos_x   = 962
    page_item.source_pos_y   = 1094
    page_item.source_size_x += 160
    page_item.target_size_x += 160
    page_item.bound_size_x  += 160
    page_item.target_pos_x  -= 80
    page_item.texture_id     = 49
    Cosmetic.import_texture(7920)
    
    page_item = Manager.get_page_item_by_index(8834)
    page_item.source_pos_x   = 266
    page_item.source_pos_y   = 1352
    page_item.source_size_x += 160
    page_item.source_size_y += 60
    page_item.target_size_x += 160
    page_item.target_size_y += 60
    page_item.bound_size_x  += 160
    page_item.bound_size_y  += 60
    page_item.target_pos_x  -= 80
    page_item.target_pos_y  -= 60
    Cosmetic.import_texture(8834)
    
    page_item = Manager.get_page_item_by_index(9478)
    page_item.source_pos_x   = 234
    page_item.source_pos_y   = 2962
    page_item.source_size_x += 203
    page_item.target_size_x += 203
    page_item.bound_size_x  += 203
    page_item.target_pos_x  -= 203
    Cosmetic.import_texture(9478)
    #Override background effects with hardcoded colors
    Cosmetic.import_texture(8836)
    Cosmetic.import_texture(8838)
    Cosmetic.import_texture(9527)
    Cosmetic.import_texture(9528)

def apply_enemy_color_rando_tweaks():
    pass

def apply_chara_color_rando_tweaks():
    #Neutralize the soul crusher effect color
    Cosmetic.import_texture(1062)

def skip_boss_rush():
    Manager.apply_tilemap_patch("SkipBossRush")