import Manager

def init():
    global object_list_pointer
    object_list_pointer = 0x581DA8
    global room_list_pointer
    room_list_pointer = 0x5C65C8
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
    global keyless_checks
    keyless_checks = [
        100051
    ]
    global special_check
    special_check = "Stage_02_21_0_0_Left"
    global special_check_requirement
    special_check_requirement = "Stage_02_47_0_1_Right"
    global macro_requirements
    macro_requirements = ["NSitem_0_83", "NSitem_0_85"]
    global map_colors
    map_colors = [
        "#71a839",
        "#a83939",
        "#3971a8",
        "#a88d39",
        "#7139a8",
        "#1a805d"
    ]

def apply_default_tweaks():
    pass

def fix_progression_obstacles():
    #Remove the early fire barrels
    Manager.remove_entity(100102)
    Manager.remove_entity(100103)
    #Remove boss doors to prevent softlocks
    Manager.game_objects["boss_brock_ob"].sprite = -1
    #Add a platform to the stage 5 high jump check
    Manager.game_data.seek(0xB51EDC)
    Manager.game_data.write((0x12).to_bytes(4, "little"))
    
    Manager.game_data.seek(0xB94F8C)
    Manager.game_data.write((0x4F).to_bytes(4, "little"))
    Manager.game_data.seek(0xB9566C)
    Manager.game_data.write((0x63).to_bytes(4, "little"))
    Manager.game_data.seek(0xB95D4C)
    Manager.game_data.write((0x1C).to_bytes(4, "little"))
    #Add a platform to the stage 6 bow check
    Manager.game_data.seek(0xC5D870)
    Manager.game_data.write((0x07).to_bytes(4, "little"))
    Manager.game_data.seek(0xC5D874)
    Manager.game_data.write((0x06).to_bytes(4, "little"))
    Manager.game_data.seek(0xC5DF50)
    Manager.game_data.write((0x14).to_bytes(4, "little"))
    Manager.game_data.seek(0xC5DF54)
    Manager.game_data.write((0x13).to_bytes(4, "little"))
    
    Manager.game_data.seek(0xCA16E0)
    Manager.game_data.write((0x15).to_bytes(4, "little"))
    Manager.game_data.seek(0xCA16E4)
    Manager.game_data.write((0x1A).to_bytes(4, "little"))
    Manager.game_data.seek(0xCA1DC0)
    Manager.game_data.write((0x20000015).to_bytes(4, "little"))
    Manager.game_data.seek(0xCA1DC4)
    Manager.game_data.write((0x2000001A).to_bytes(4, "little"))
    
    Manager.game_data.seek(0xD6D38C)
    Manager.game_data.write((0x15).to_bytes(4, "little"))
    Manager.game_data.seek(0xD6D390)
    Manager.game_data.write((0x1A).to_bytes(4, "little"))
    Manager.game_data.seek(0xD6DA6C)
    Manager.game_data.write((0x20000015).to_bytes(4, "little"))
    Manager.game_data.seek(0xD6DA70)
    Manager.game_data.write((0x2000001A).to_bytes(4, "little"))
    #Make a few changes for the stage 4 cutscene crash workaround
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

def update_ability_description():
    skill_up_text = "Ability Upgrade\nYou can now use a new ability."
    final_up_text = "Final Ability\nYou can now use every ability."
    Manager.replace_text_entry("@80", skill_up_text)
    Manager.replace_text_entry("@81", skill_up_text)
    Manager.replace_text_entry("@82", skill_up_text)
    Manager.replace_text_entry("@83", skill_up_text)
    Manager.replace_text_entry("@84", final_up_text)