import Manager

def init():
    global object_list_pointer
    object_list_pointer = 0x2D61D8
    global room_list_pointer
    room_list_pointer = 0x30B2E8
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
        101175:  112,
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
    global keyless_checks
    keyless_checks = []
    global special_check
    special_check = "To_Stage_05_00_Start"
    global special_check_requirement
    special_check_requirement = "Stage_04_30_1_0_Right"
    global macro_requirements
    macro_requirements = ["NSitem_0_81", "NSitem_0_82"]
    global map_colors
    map_colors = [
        "#71a839",
        "#a83939",
        "#a88d39",
        "#3971a8",
        "#7139a8",
        "#a83971"
    ]

def apply_default_tweaks():
    pass

def fix_progression_obstacles():
    #Add a platform to the stage 2 blue door
    Manager.game_data.seek(0x3BFFE0)
    Manager.game_data.write((0x12).to_bytes(4, "little"))
    
    Manager.game_data.seek(0x3D8110)
    Manager.game_data.write((0x8E).to_bytes(4, "little"))
    Manager.game_data.seek(0x3D8480)
    Manager.game_data.write((0x10000146).to_bytes(4, "little"))
    #Add a block to the stage 5 purple key check
    Manager.game_data.seek(0x574DF8)
    Manager.game_data.write((0x01).to_bytes(4, "little"))
    
    Manager.game_data.seek(0x597298)
    Manager.game_data.write((0x64).to_bytes(4, "little"))

def update_ability_description():
    skill_up_text = "You got SKILL UP\nYou can now use a new ability."
    Manager.replace_text_entry("@79", skill_up_text)
    Manager.replace_text_entry("@80", skill_up_text)
    Manager.replace_text_entry("@81", skill_up_text)
    Manager.replace_text_entry("@82", skill_up_text)
    Manager.replace_text_entry("@83", skill_up_text)