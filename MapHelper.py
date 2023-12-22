import Manager

class Room:
    def __init__(self, name, offset_x, offset_y, width, height, icon, doors):
        self.name = name
        self.stage_id = int(name.split("_")[1])
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.width = width
        self.height = height
        self.icon = icon
        self.doors = doors

class Door:
    def __init__(self, x_block, y_block, direction):
        self.x_block = x_block
        self.y_block = y_block
        self.direction = direction

def init():
    global door_connections
    door_connections = {}
    global direction_to_opposite
    direction_to_opposite = {
        "Left":   "Right",
        "Bottom": "Top",
        "Right":  "Left",
        "Top":    "Bottom"
    }
    global check_to_room
    check_to_room = {}

def get_map_info():
    for room_1 in Manager.constant["RoomLayout"]:
        for room_2 in Manager.constant["RoomLayout"]:
            is_room_adjacent(room_to_object(room_1), room_to_object(room_2))

def fill_check_to_room():
    for room in Manager.constant["CasualLogic"]:
        for door in Manager.constant["CasualLogic"][room]:
            for check in Manager.constant["CasualLogic"][room][door]:
                try:
                    check = int(check)
                except ValueError:
                    continue
                check_to_room[check] = room
    
def room_to_object(room):
    offset_x    = Manager.constant["RoomLayout"][room]["OffsetX"]
    offset_y    = Manager.constant["RoomLayout"][room]["OffsetY"]
    width       = Manager.constant["RoomLayout"][room]["Width"]
    height      = Manager.constant["RoomLayout"][room]["Height"]
    icon        = Manager.constant["RoomLayout"][room]["Icon"]
    doors       = []
    for door in Manager.constant["RoomLayout"][room]["Doors"]:
        param = door.split("_")
        doors.append(Door(int(param[0]), int(param[1]), param[2]))
    return Room(room, offset_x, offset_y, width, height, icon, doors)

def is_room_adjacent(room_1, room_2):
    if left_room_check(room_1, room_2):
        door_vertical_check(room_1, room_2, "Left")
    if bottom_room_check(room_1, room_2):
        door_horizontal_check(room_1, room_2, "Bottom")
    if right_room_check(room_1, room_2):
        door_vertical_check(room_1, room_2, "Right")
    if top_room_check(room_1, room_2):
        door_horizontal_check(room_1, room_2, "Top")
    return False

def left_room_check(room_1, room_2):
    return bool(room_2.offset_x == room_1.offset_x - 1 * room_2.width and room_1.offset_y - 1 * (room_2.height - 1) <= room_2.offset_y <= room_1.offset_y + 1 * (room_1.height - 1))

def bottom_room_check(room_1, room_2):
    return bool(room_1.offset_x - 1 * (room_2.width - 1) <= room_2.offset_x <= room_1.offset_x + 1 * (room_1.width - 1) and room_2.offset_y == room_1.offset_y - 1 * room_2.height)

def right_room_check(room_1, room_2):
    return bool(room_2.offset_x == room_1.offset_x + 1 * room_1.width and room_1.offset_y - 1 * (room_2.height - 1) <= room_2.offset_y <= room_1.offset_y + 1 * (room_1.height - 1))

def top_room_check(room_1, room_2):
    return bool(room_1.offset_x - 1 * (room_2.width - 1) <= room_2.offset_x <= room_1.offset_x + 1 * (room_1.width - 1) and room_2.offset_y == room_1.offset_y + 1 * room_1.height)

def door_vertical_check(room_1, room_2, direction):
    for door_1 in room_1.doors:
        if door_1.direction == direction:
            for door_2 in room_2.doors:
                if door_2.direction == direction_to_opposite[direction] and door_1.y_block == (door_2.y_block + (room_2.offset_y - room_1.offset_y)):
                    door_connections[door_to_string(room_1, door_1)] = door_to_string(room_2, door_2)

def door_horizontal_check(room_1, room_2, direction):
    for door_1 in room_1.doors:
        if door_1.direction == direction:
            for door_2 in room_2.doors:
                if door_2.direction == direction_to_opposite[direction] and door_1.x_block == (door_2.x_block + (room_2.offset_x - room_1.offset_x)):
                    door_connections[door_to_string(room_1, door_1)] = door_to_string(room_2, door_2)

def door_to_string(room, door):
    return "_".join([room.name, str(door.x_block), str(door.y_block), str(door.direction)])

def get_door_destination(door):
    if door in door_connections:
        return door_connections[door]
    elif door.split("_")[0] == "To":
        split_door = door.split("_")
        split_door.pop(0)
        return "_".join(split_door)
    else:
        return None

def get_door_room(door):
    split_door = door.split("_")
    return "_".join([split_door[0], split_door[1], split_door[2]])