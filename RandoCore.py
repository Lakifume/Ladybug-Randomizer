import Manager
import MapHelper
import LunaNights
import WonderLab

import json
import random
import os
import copy

def init():
    global previous_available_checks
    previous_available_checks = []
    global current_available_doors
    current_available_doors = ["Stage_00_00_Start"]
    global current_available_checks
    current_available_checks = []
    global all_available_doors
    all_available_doors = copy.deepcopy(current_available_doors)
    global all_available_checks
    all_available_checks = []
    global check_to_requirement
    check_to_requirement = {}
    global key_item_to_location
    key_item_to_location = {}
    global next_ability_index
    next_ability_index = 0
    global special_check_doors
    special_check_doors = []
    global type_to_items
    type_to_items = {}
    global item_list
    item_list = []
    global item_pool
    item_pool = []
    global key_items
    key_items = []
    global requirement_macro
    requirement_macro = "Height"

def set_logic_complexity(complexity):
    global logic_complexity
    logic_complexity = (complexity - 1)/2

def set_enemy_type_wheight(wheight):
    global enemy_type_wheight
    enemy_type_wheight = wheight*2

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

def remove_ice_magatama():
    if "NSitem_0_95" in item_list:
        item_list.remove("NSitem_0_95")
        key_items.remove("NSitem_0_95")
        key_item_to_location["NSitem_0_95"] = 101175

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
    if requirement == requirement_macro:
        return satisfies_requirement(Manager.game.macro_requirements)
    return requirement in key_item_to_location

def check_unreachable_ability(requirement):
    if requirement == requirement_macro:
        return has_unreachable_ability(Manager.game.macro_requirements)
    if requirement in Manager.game.ability_order:
        return Manager.game.ability_order.index(requirement) > next_ability_index
    return False

def process_key_logic():
    while True:
        #Move through rooms
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
                if check == Manager.game.special_check:
                    special_check_doors.append(door)
                    continue
                analyse_check(check, requirement)
        #Keep going until stuck
        if current_available_doors:
            continue
        #Check special requirements
        if special_check_doors and Manager.game.special_check_requirement in all_available_doors:
            for door in special_check_doors:
                room = MapHelper.get_door_room(door)
                short_door = door.replace(room + "_", "")
                analyse_check(Manager.game.special_check, Manager.constant["RoomLogic"][room][short_door][Manager.game.special_check.replace(room + "_", "")])
            special_check_doors.clear()
        #Keep going until stuck
        if current_available_doors:
            continue
        #Place key item
        if check_to_requirement:
            #Weight checks
            requirement_list_list = []
            for check in check_to_requirement:
                requirement_list = check_to_requirement[check]
                if not requirement_list in requirement_list_list:
                    requirement_list_list.append(requirement_list)
            chosen_requirement_list = random.choice(requirement_list_list)
            while has_unreachable_ability(chosen_requirement_list):
                chosen_requirement_list = random.choice(requirement_list_list)
            #Don't pick unreachable abilities
            chosen_requirement = random.choice(chosen_requirement_list)
            while has_unreachable_ability([chosen_requirement]):
                chosen_requirement = random.choice(chosen_requirement_list)
            #Choose requirement and key item
            if type(chosen_requirement) is list:
                for item in chosen_requirement:
                    if satisfies_requirement([item]):
                        continue
                    chosen_item = pick_next_key(item)
                    place_next_key(chosen_item)
            else:
                chosen_item = pick_next_key(chosen_requirement)
                place_next_key(chosen_item)
            previous_available_checks.clear()
            previous_available_checks.extend(current_available_checks)
            current_available_checks.clear()
            #Check which obstacles were lifted
            for check in list(check_to_requirement):
                if not check in check_to_requirement:
                    continue
                requirement = check_to_requirement[check]
                analyse_check(check, requirement)
        #Place last unecessary keys
        elif key_items:
            place_next_key(random.choice(key_items))
            current_available_checks.clear()
        #Stop when all keys are placed and all doors are explored
        else:
            break

def pick_next_key(chosen_requirement):
    if chosen_requirement == requirement_macro:
        chosen_item = random.choice(Manager.game.macro_requirements)
        while has_unreachable_ability([chosen_item]):
            chosen_item = random.choice(Manager.game.macro_requirements)
        return chosen_item
    return chosen_requirement

def analyse_check(check, requirement):
    #If accessible try to remove it from requirement list no matter what
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
    global next_ability_index
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
                    raise RuntimeError
    else:
        try:
            chosen_check = pick_key_check(all_available_checks)
        except IndexError:
            raise RuntimeError
    key_item_to_location[chosen_item] = chosen_check
    key_items.remove(chosen_item)
    if chosen_item in Manager.game.ability_order:
        next_ability_index += 1

def pick_key_check(available_checks):
    possible_checks = []
    for check in available_checks:
        if not check in list(key_item_to_location.values()) and not check in Manager.game.keyless_checks and is_entity_in_item_pool(check):
            possible_checks.append(check)
    return random.choice(possible_checks)

def is_entity_in_item_pool(instance):
    if Manager.game_entities[instance].type in item_list:
        return True
    return ".".join([Manager.game_entities[instance].type, str(Manager.game_entities[instance].creation_code)]) in item_list

def is_entity_a_key_item(instance):
    if Manager.game_entities[instance].type in Manager.constant["ItemInfo"]:
        return Manager.constant["ItemInfo"][Manager.game_entities[instance].type]["Type"] == "Key"
    return Manager.constant["ItemInfo"][".".join([Manager.game_entities[instance].type, str(Manager.game_entities[instance].creation_code)])]["Type"] == "Key"

def randomize_items():
    #Gather data
    location_to_key_item = {value: key for key, value in key_item_to_location.items()}
    item_to_codes = {}
    for instance in Manager.game.instance_to_offset_up:
        if not Manager.game_entities[instance].type in item_to_codes:
            item_to_codes[Manager.game_entities[instance].type] = []
        item_to_codes[Manager.game_entities[instance].type].append(Manager.game_entities[instance].creation_code)
    #Start with game-specific edge cases
    magatama_replacement = None
    if "NSitem_0_95" in item_list:
        if 101175 in location_to_key_item:
            magatama_replacement = location_to_key_item[101175]                             
        else:
            magatama_replacement = random.choice(item_pool)
            while not -1 in item_to_codes[magatama_replacement]:
                magatama_replacement = random.choice(item_pool)
            item_pool.remove(magatama_replacement)
            item_to_codes[magatama_replacement].remove(-1)
        Manager.transfer_object_code("NSitem_0_95", magatama_replacement)
        Manager.transfer_object_code(magatama_replacement, "NSitem_0_95")
        del Manager.game.instance_to_offset_up[101175]
    if "bow_item_ob" in item_list:
        Manager.game_entities[100051].creation_code = pick_and_remove(item_to_codes["bow_item_ob"])
        item_pool.remove("bow_item_ob")
        del Manager.game.instance_to_offset_up[100051]
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
        if new_item in Manager.game_objects:
            new_code = pick_and_remove(item_to_codes[new_item])
        else:
            profile = new_item.split(".")
            new_item = profile[0]
            new_code = int(profile[-1])
            item_to_codes[new_item].remove(new_code)
        #Override the hardcoded item
        if new_item == "NSitem_0_95":
            new_item = magatama_replacement
        elif new_item == magatama_replacement:
            new_item = "NSitem_0_95"
        Manager.game_entities[instance].type = new_item
        Manager.game_entities[instance].creation_code = new_code
        #Correct position
        if new_item in Manager.game.grounded_item_to_offset_up:
            if instance in Manager.game.instance_exception_to_position:
                Manager.game_entities[instance].x_pos = Manager.game.instance_exception_to_position[instance][0]
                Manager.game_entities[instance].y_pos = Manager.game.instance_exception_to_position[instance][1] - Manager.game.grounded_item_to_offset_up[new_item]
            else:
                floor_offset = Manager.game.instance_to_offset_up[instance]
                direction = 1
                if floor_offset != 0:
                    direction = floor_offset/abs(floor_offset)
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
            if enemy_replacement[enemy] in Manager.game_objects:
                Manager.transfer_object_code(enemy, enemy_replacement[enemy])
            else:
                Manager.transfer_object_code(enemy, enemy_replacement[enemy] + "l")
            #Neutralize destroy code to avoid crashes
            if Manager.game == LunaNights and Manager.game_objects[enemy].events["Destroy"]:
                Manager.game_objects[enemy].events["Destroy"][0].action = Manager.game_objects["NSenemy_0_02"].events["Destroy"][0].action
        else:
            #Adapt for left and right variants
            for direction in ["l", "r"]:
                if enemy_replacement[enemy] in Manager.game_objects:
                    Manager.transfer_object_code(enemy + direction, enemy_replacement[enemy])
                else:
                    Manager.transfer_object_code(enemy + direction, enemy_replacement[enemy] + direction)

def pick_and_remove(array):
    item = random.choice(array)
    array.remove(item)
    return item

def write_spoiler_log(seed):
    if not os.path.isdir("Spoiler"):
        os.makedirs("Spoiler")
    with open("Spoiler\\" + Manager.game_name + " - " + str(seed) + ".json", "w") as file_writer:
        file_writer.write(json.dumps(key_item_to_location, indent=2))