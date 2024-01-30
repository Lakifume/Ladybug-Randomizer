import Manager
import MapHelper
import LunaNights
import WonderLab

import json
import random
import os
import copy

class CompletionError(Exception):
    pass

def init():
    global previous_available_checks
    previous_available_checks = []
    global current_available_doors
    current_available_doors = ["Stage_00_00_Start"]
    global current_available_checks
    current_available_checks = []
    global all_available_doors
    all_available_doors = []
    global all_available_checks
    all_available_checks = []
    global check_to_requirement
    check_to_requirement = {}
    global key_item_to_location
    key_item_to_location = {}
    global starting_items
    starting_items = []
    global next_ability_index
    next_ability_index = 0
    global special_check_to_door
    special_check_to_door = {}
    global type_to_items
    type_to_items = {}
    global item_list
    item_list = []
    global item_pool
    item_pool = []
    global key_items
    key_items = []
    global hardcoded_item_replacement
    hardcoded_item_replacement = {}

def set_logic_complexity(complexity):
    global logic_complexity
    logic_complexity = (complexity - 1)/2

def set_enemy_type_wheight(wheight):
    global enemy_type_wheight
    enemy_type_wheight = wheight*2

def apply_extra_logic(logic_name):
    for room in Manager.constant[logic_name]:
        for door in Manager.constant[logic_name][room]:
            for check in Manager.constant[logic_name][room][door]:
                Manager.constant["RoomLogic"][room][door][check] = Manager.constant[logic_name][room][door][check]

def categorize_items():
    for item in Manager.constant["ItemInfo"]:
        if not Manager.constant["ItemInfo"][item]["Type"] in type_to_items:
            type_to_items[Manager.constant["ItemInfo"][item]["Type"]] = []
        for num in range(Manager.constant["ItemInfo"][item]["Count"]):
            type_to_items[Manager.constant["ItemInfo"][item]["Type"]].append(item)

def add_item_type(type):
    if not type in type_to_items:
        return
    for item in type_to_items[type]:
        if not item in item_list:
            item_list.append(item)
        if type == "Key":
            key_items.append(item)
        else:
            item_pool.append(item)

def remove_hardcoded_items():
    for instance in Manager.game.hardcoded_instance_to_item:
        item = Manager.game.hardcoded_instance_to_item[instance]
        if item in item_list:
            item_list.remove(item)
        if item in key_items:
            key_items.remove(item)
            key_item_to_location[item] = instance
        if item in item_pool:
            item_pool.remove(item)

def satisfies_requirement(requirement):
    check = True
    for req in requirement:
        #AND
        if type(req) is list:
            for subreq in req:
                check = check_requirement(subreq)
                if not check:
                    break
            if check:
                break
        #OR  
        else:
            check = check_requirement(req)
            if check:
                break
    return check

def has_unreachable_ability(requirement):
    check = False
    for req in requirement:
        #AND
        if type(req) is list:
            for subreq in req:
                check = check_unreachable_ability(subreq)
                if check:
                    break
            if not check:
                break
        #OR  
        else:
            check = check_unreachable_ability(req)
            if not check:
                break
    return check

def check_requirement(requirement):
    if requirement in Manager.game.macro_to_requirements:
        return satisfies_requirement(Manager.game.macro_to_requirements[requirement])
    return requirement in key_item_to_location or requirement in starting_items

def check_unreachable_ability(requirement):
    if requirement in Manager.game.macro_to_requirements:
        return has_unreachable_ability(Manager.game.macro_to_requirements[requirement])
    if requirement in Manager.game.ability_order:
        return Manager.game.ability_order.index(requirement) > next_ability_index
    return False

def process_key_logic():
    move_through_rooms()
    while True:
        #Place key item
        if check_to_requirement:
            #Weight checks
            requirement_list_list = []
            for check in check_to_requirement:
                requirement_list = check_to_requirement[check]
                if not requirement_list in requirement_list_list and not has_unreachable_ability(requirement_list):
                    requirement_list_list.append(requirement_list)
            #If unable to proceed force placing the next ability
            if not requirement_list_list:
                place_next_key(Manager.game.ability_order[next_ability_index])
                continue
            chosen_requirement_list = random.choice(requirement_list_list)
            #Choose requirement and key item
            pick_next_key(chosen_requirement_list)
        #Place last unecessary keys
        elif key_items:
            place_next_key(random.choice(key_items))
        #Stop when all keys are placed and all doors are explored
        else:
            break

def move_through_rooms():
    #Move through each door
    while True:
        for door in copy.deepcopy(current_available_doors):
            current_available_doors.remove(door)
            room = MapHelper.get_door_room(door)
            short_door = door.replace(room + "_", "")
            for check, requirement in Manager.constant["RoomLogic"][room][short_door].items():
                #Convert check
                try:
                    check = int(check)
                except ValueError:
                    if not "Stage" in check:
                        check = "_".join([room, check])
                #Don't automatically unlock the special check
                if check in Manager.game.special_check_to_requirement:
                    if not check in special_check_to_door:
                        special_check_to_door[check] = []
                    special_check_to_door[check].append(door)
                    continue
                analyse_check(check, requirement)
        #Keep going until stuck
        if current_available_doors:
            continue
        #Check special requirements
        for special_check in Manager.game.special_check_to_requirement:
            if special_check in special_check_to_door and Manager.game.special_check_to_requirement[special_check] in all_available_doors:
                for door in special_check_to_door[special_check]:
                    room = MapHelper.get_door_room(door)
                    short_door = door.replace(room + "_", "")
                    analyse_check(special_check, Manager.constant["RoomLogic"][room][short_door][special_check.replace(room + "_", "")])
                del special_check_to_door[special_check]
        #Stop if no more doors are found
        if not current_available_doors:
            break

def check_lifted_obstacles():
    for check in list(check_to_requirement):
        if not check in check_to_requirement:
            continue
        requirement = check_to_requirement[check]
        analyse_check(check, requirement)

def reset_available_checks():
    previous_available_checks.clear()
    previous_available_checks.extend(current_available_checks)
    current_available_checks.clear()

def pick_next_key(requirement):
    chosen_requirement = random.choice(requirement)
    while has_unreachable_ability([chosen_requirement]):
        chosen_requirement = random.choice(requirement)
    if type(chosen_requirement) is list:
        for req in chosen_requirement:
            check_next_key(req)
    else:
        check_next_key(chosen_requirement)

def check_next_key(item):
    if satisfies_requirement([item]):
        return
    if item in Manager.game.macro_to_requirements:
        pick_next_key(Manager.game.macro_to_requirements[item])
    else:
        place_next_key(item)

def analyse_check(check, requirement):
    #If accessible remove it from the requirement list
    accessible = satisfies_requirement(requirement)
    if accessible:
        if check in check_to_requirement:
            del check_to_requirement[check]
    #Handle each check type differently
    is_door = not type(check) is int
    if is_door:
        if check in all_available_doors:
            return
    else:
        if check in all_available_checks:
            return
    #Set check as available
    if accessible:
        if is_door:
            all_available_doors.append(check)
            destination = MapHelper.get_door_destination(check)
            if destination:
                current_available_doors.append(destination)
                all_available_doors.append(destination)
                if destination in check_to_requirement:
                    del check_to_requirement[destination]
        else:
            current_available_checks.append(check)
            all_available_checks.append(check)
    #Add to requirement list
    else:
        if check in check_to_requirement:
            add_requirement_to_check(check, requirement)
        else:
            check_to_requirement[check] = requirement

def add_requirement_to_check(check, requirement):
    old_list = check_to_requirement[check] + requirement
    new_list = []
    for req in old_list:
        to_add = not req in new_list
        if type(req) is list:
            for subreq in old_list:
                if subreq in req:
                    to_add = False
        if to_add:
            new_list.append(req)
    check_to_requirement[check] = new_list

def place_next_key(chosen_item):
    if random.random() < logic_complexity:
        try:
            chosen_check = pick_key_check(current_available_checks)
        except IndexError:
            try:
                chosen_check = pick_key_check(previous_available_checks)
            except IndexError:
                try:
                    chosen_check = pick_key_check(all_available_checks)
                except IndexError:
                    raise CompletionError
    elif random.random() < logic_complexity:
        try:
            chosen_check = pick_key_check(previous_available_checks)
        except IndexError:
            try:
                chosen_check = pick_key_check(all_available_checks)
            except IndexError:
                raise CompletionError
    else:
        try:
            chosen_check = pick_key_check(all_available_checks)
        except IndexError:
            raise CompletionError
    key_item_to_location[chosen_item] = chosen_check
    key_items.remove(chosen_item)
    #Increment ability index
    global next_ability_index
    if chosen_item in Manager.game.ability_order:
        next_ability_index += 1
    #Analyse the game again
    reset_available_checks()
    check_lifted_obstacles()
    move_through_rooms()

def pick_key_check(available_checks):
    possible_checks = []
    for check in available_checks:
        if not check in list(key_item_to_location.values()) and is_entity_in_item_pool(check):
            possible_checks.append(check)
    return random.choice(possible_checks)

def is_entity_in_item_pool(instance):
    if instance in Manager.game.hardcoded_instance_to_item:
        return Manager.game.hardcoded_instance_to_item[instance] in item_list
    full_name = ".".join([Manager.game_entities[instance].type, str(Manager.game_entities[instance].creation_code)])
    if full_name in Manager.constant["ItemInfo"]:
        return full_name in item_list
    return Manager.game_entities[instance].type in item_list

def is_entity_a_key_item(instance):
    if instance in Manager.game.hardcoded_instance_to_item:
        return Manager.constant["ItemInfo"][Manager.game.hardcoded_instance_to_item[instance]]["Type"] == "Key"
    full_name = ".".join([Manager.game_entities[instance].type, str(Manager.game_entities[instance].creation_code)])
    if full_name in Manager.constant["ItemInfo"]:
        return Manager.constant["ItemInfo"][full_name]["Type"] == "Key"
    return Manager.constant["ItemInfo"][Manager.game_entities[instance].type]["Type"] == "Key"

def split_item_profile(item):
    item_split = item.split(".")
    if len(item_split) == 1:
        return (item_split[0], None)
    elif len(item_split) == 2:
        return (item_split[0], int(item_split[1]))
    raise Exception(f"Item name invalid: {item}")

def randomize_items():
    #Gather data
    location_to_key_item = {value: key for key, value in key_item_to_location.items()}
    item_to_codes = {}
    for instance in list(Manager.game.instance_to_offset_up) + list(Manager.game.hardcoded_instance_to_item):
        if not instance in Manager.game_entities:
            continue
        if not Manager.game_entities[instance].type in item_to_codes:
            item_to_codes[Manager.game_entities[instance].type] = []
        item_to_codes[Manager.game_entities[instance].type].append(Manager.game_entities[instance].creation_code)
    for item in Manager.constant["ItemInfo"]:
        item_name, item_code = split_item_profile(item)
        if item_code in item_to_codes[item_name]:
            item_to_codes[item_name].remove(item_code)
    #Start with hardcoded instances
    for instance in Manager.game.hardcoded_instance_to_item:
        if not is_entity_in_item_pool(instance):
            continue
        if instance in location_to_key_item:
            chosen = location_to_key_item[instance]
        else:
            chosen = random.choice(item_pool)
            while True:
                if chosen in item_to_codes:
                    if -1 in item_to_codes[chosen]:
                        item_to_codes[chosen].remove(-1)
                        break
                if split_item_profile(chosen)[1] == -1:
                    break
                chosen = random.choice(item_pool)
            item_pool.remove(chosen)
        hardcoded_item = split_item_profile(Manager.game.hardcoded_instance_to_item[instance])[0]
        chosen_item = split_item_profile(chosen)[0]
        hardcoded_item_replacement[hardcoded_item] = chosen_item
        Manager.transfer_object_code(hardcoded_item, chosen_item)
        Manager.transfer_object_code(chosen_item, hardcoded_item)
    hardcoded_item_replacement_invert = {value: key for key, value in hardcoded_item_replacement.items()}
    #Apply changes to the rest
    for instance in Manager.game.instance_to_offset_up:
        if is_entity_a_key_item(instance) and not is_entity_in_item_pool(instance):
            continue
        old_item = Manager.game_entities[instance].type
        if instance in location_to_key_item:
            new_item = location_to_key_item[instance]
        else:
            if is_entity_in_item_pool(instance):
                new_item = pick_and_remove(item_pool)
            else:
                new_item = pick_and_remove(type_to_items[Manager.constant["ItemInfo"][old_item]["Type"]])
        #Pick the correct creation code
        new_item, new_code = split_item_profile(new_item)
        if not new_code:
            new_code = random.choice(item_to_codes[new_item])
            item_to_codes[new_item].remove(new_code)
        #Override the hardcoded item
        if new_item in hardcoded_item_replacement:
            new_item = hardcoded_item_replacement[new_item]
        elif new_item in hardcoded_item_replacement_invert:
            new_item = hardcoded_item_replacement_invert[new_item]
        #Change parameters
        Manager.game_entities[instance].type = new_item
        Manager.game_entities[instance].creation_code = new_code
        #Correct position
        if new_item in Manager.game.grounded_item_to_offset_up:
            if instance in Manager.game.instance_exception_to_position:
                Manager.game_entities[instance].x_pos = Manager.game.instance_exception_to_position[instance][0]
                Manager.game_entities[instance].y_pos = Manager.game.instance_exception_to_position[instance][1] - Manager.game.grounded_item_to_offset_up[new_item]
            else:
                floor_offset = Manager.game.instance_to_offset_up[instance]
                direction = floor_offset/abs(floor_offset) if floor_offset != 0 else 1
                Manager.game_entities[instance].y_pos -= int(direction*Manager.game.grounded_item_to_offset_up[new_item] - floor_offset)
                Manager.game_entities[instance].rotation = 90 - direction*90
        elif old_item in Manager.game.grounded_item_to_offset_up:
            Manager.game_entities[instance].y_pos -= Manager.game.floating_item_offset_up - Manager.game.grounded_item_to_offset_up[old_item]

def randomize_enemies():
    #Randomize in a dictionary
    weight_to_enemy = {}
    for enemy in Manager.constant["EnemyInfo"]:
        weight = Manager.constant["EnemyInfo"][enemy]["Weight"]
        if not weight in weight_to_enemy:
            weight_to_enemy[weight] = []
        weight_to_enemy[weight].append(enemy)
    #Shuffle enemies within each weight
    enemy_replacement = {}
    for enemy in Manager.constant["EnemyInfo"]:
        weight = Manager.constant["EnemyInfo"][enemy]["Weight"]
        valid_enemy_list = []
        for possible_enemy in weight_to_enemy[weight]:
            if abs(Manager.constant["EnemyInfo"][enemy]["StageID"] - Manager.constant["EnemyInfo"][possible_enemy]["StageID"]) < enemy_type_wheight:
                valid_enemy_list.append(possible_enemy)
        if valid_enemy_list:
            chosen = random.choice(valid_enemy_list)
            weight_to_enemy[weight].remove(chosen)
        else:
            chosen = pick_and_remove(weight_to_enemy[weight])
        enemy_replacement[enemy] = chosen
    #Apply
    for enemy in enemy_replacement:
        if enemy in Manager.game_objects:
            suffix = "" if enemy_replacement[enemy] in Manager.game_objects else "l"
            Manager.transfer_object_code(enemy, enemy_replacement[enemy] + suffix)
            #Neutralize destroy code to avoid crashes
            if Manager.game == LunaNights and Manager.game_objects[enemy].events["Destroy"]:
                Manager.game_objects[enemy].events["Destroy"][0].action = Manager.game_objects["NSenemy_0_02"].events["Destroy"][0].action
        else:
            #Adapt for left and right variants
            for direction in ["l", "r"]:
                suffix = "" if enemy_replacement[enemy] in Manager.game_objects else direction
                Manager.transfer_object_code(enemy + direction, enemy_replacement[enemy] + suffix)

def pick_and_remove(array):
    item = random.choice(array)
    array.remove(item)
    return item

def write_spoiler_log(seed):
    if not os.path.isdir("Spoiler"):
        os.makedirs("Spoiler")
    spoiler = {}
    spoiler["Start"] = MapHelper.get_door_room(all_available_doors[0])
    spoiler["Key"] = copy.deepcopy(key_item_to_location)
    with open(f"Spoiler\\{Manager.game_name} - {seed}.json", "w") as file_writer:
        file_writer.write(json.dumps(spoiler, indent=2))

def write_save_info():
    save_info_path = os.path.splitext(Manager.save_file_path)[0] + ".txt"
    save_info = [
        str(Manager.game_save["iSpawnPosX"]) + "\n",
        str(Manager.game_save["iSpawnPosY"]) + "\n",
        str(Manager.game_save["iSpawnStage"])+ "\n"
    ]
    with open(save_info_path, "w") as file_writer:
        file_writer.writelines(save_info)