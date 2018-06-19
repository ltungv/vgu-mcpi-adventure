import mcpi.block as block
import random
import os
import time
import numpy as np
import math
from shapes import Point
from constants import PUZZLE_ROOMS, STAGE_POS, TRAP_ROOMS, CHEAT_ROOMS
from dungeon import DIRECTIONS
from mcpi.vec3 import Vec3


def build_door(mc, tile_pos, stage_pos, door_type, difficulty):
    if difficulty == 'easy':
        rooms = [PUZZLE_ROOMS['Quack'], PUZZLE_ROOMS['FirstPassage'],
                 TRAP_ROOMS['Easy1'], TRAP_ROOMS['Easy2']]
    elif difficulty == 'medium':
        rooms = [PUZZLE_ROOMS['SecondPassage'], PUZZLE_ROOMS['Red'],
                 CHEAT_ROOMS['Medium'], TRAP_ROOMS['Medium1'],
                 TRAP_ROOMS['Medium2'], TRAP_ROOMS['Medium3']]
    elif difficulty == 'hard':
        rooms = [PUZZLE_ROOMS['Quiz'], PUZZLE_ROOMS['Chess'], PUZZLE_ROOMS['Water'],
                 CHEAT_ROOMS['Hard'], TRAP_ROOMS['Hard1'],
                 TRAP_ROOMS['Hard2'], TRAP_ROOMS['Hard3']]

    for room in rooms:
        for dir_index, direction in enumerate(DIRECTIONS):
            tile2d_offset = Point(tile_pos.x, tile_pos.z) + direction
            if room.contains(
                    tile2d_offset,
                    -stage_pos.x, -stage_pos.z):
                door_data_val = dir_index
                mc.setBlock(
                    tile_pos.x, tile_pos.y, tile_pos.z,
                    door_type, door_data_val
                )
                mc.setBlock(
                    tile_pos.x, tile_pos.y + 1, tile_pos.z,
                    door_type, door_data_val + 8
                )
                break


def build_dungeon(mc, stage_pos, difficulty):
    path = os.path.join('layout', difficulty)
    layouts = [f for f in os.listdir(path)]
    random.shuffle(layouts)
    selected_layout = random.choice(layouts)
    tiles = np.genfromtxt(
        os.path.join(path, selected_layout),
        delimiter=',', dtype=None
    )
    # Go through every tiles in the map
    # and use setBlock() to set that tile in MineCraft
    for posx, row in enumerate(tiles):
        for posz, tile in enumerate(row):
            tile_pos = Vec3(posx + stage_pos.x, stage_pos.y, posz + stage_pos.z)
            if (tile == block.DOOR_WOOD.id or tile == block.DOOR_IRON.id):
                mc.setBlock(tile_pos.x, tile_pos.y - 1, tile_pos.z, block.SANDSTONE.id)
                build_door(mc, tile_pos, stage_pos, tile, difficulty)
                if (PUZZLE_ROOMS['Water'].inflate(1).contains(Point(posx, posz)) and
                        difficulty == 'hard'):
                    mc.setBlocks(tile_pos.x, tile_pos.y + 2, tile_pos.z,
                                 tile_pos.x, tile_pos.y + 14, tile_pos.z,
                                 block.SANDSTONE.id)
            elif (PUZZLE_ROOMS['Water'].inflate(1).contains(Point(posx, posz)) and
                  difficulty == 'hard'):
                mc.setBlocks(tile_pos.x, tile_pos.y, tile_pos.z,
                             tile_pos.x, tile_pos.y + 14, tile_pos.z,
                             tile)
            else:
                mc.setBlocks(tile_pos.x, tile_pos.y, tile_pos.z,
                             tile_pos.x, tile_pos.y + 1, tile_pos.z,
                             tile)


def build_inversed_pyramid(mc, pos_start, height, size_offset=0, block_type=block.SANDSTONE.id):
    '''
        Build an hollowed upside-down pyramid
    '''
    for yy in range(height):
        distance_from_center = size_offset + yy
        pos_y = pos_start.y + yy

        bound_left = pos_start.x - distance_from_center
        bound_right = pos_start.x + distance_from_center
        bound_top = pos_start.z - distance_from_center
        bound_bottom = pos_start.z + distance_from_center

        mc.setBlocks(bound_left, pos_y, bound_top, bound_right, pos_y, bound_top, block_type)
        time.sleep(0.25)
        mc.setBlocks(bound_left, pos_y, bound_bottom, bound_right, pos_y, bound_bottom, block_type)
        time.sleep(0.25)
        mc.setBlocks(bound_left, pos_y, bound_top, bound_left, pos_y, bound_bottom, block_type)
        time.sleep(0.25)
        mc.setBlocks(bound_right, pos_y, bound_top, bound_right, pos_y, bound_bottom, block_type)
        time.sleep(0.25)


def build_quack_a_mole(mc):
    '''
        Build quack a mole (with tnt) room in Minecraft Pi
    '''
    current_room = PUZZLE_ROOMS['Quack']
    # Build the platform
    stage_posy = STAGE_POS[0].y
    stage_posx = int(current_room.left + (current_room.width - 10) / 2) + STAGE_POS[0].x
    stage_posz = int(current_room.top + (current_room.height - 10) / 2) + STAGE_POS[0].z
    mc.setBlocks(stage_posx, stage_posy, stage_posz,
                 stage_posx + 10, stage_posy, stage_posz + 10,
                 block.WOOL.id, 1)


def build_water(mc):
    '''
        Build the water room in Minecraft Pi
    '''
    current_room = PUZZLE_ROOMS['Water']
    # Fill the space inside with air then with water
    mc.setBlocks(current_room.left + STAGE_POS[2].x,
                 STAGE_POS[2].y,
                 current_room.top + STAGE_POS[2].z,
                 current_room.right + STAGE_POS[2].x - 1,
                 STAGE_POS[2].y + 14,
                 current_room.bottom + STAGE_POS[2].z - 1,
                 block.AIR.id)
    mc.setBlocks(current_room.left + STAGE_POS[2].x,
                 STAGE_POS[2].y,
                 current_room.top + STAGE_POS[2].z,
                 current_room.right + STAGE_POS[2].x - 1,
                 STAGE_POS[2].y + 10,
                 current_room.bottom + STAGE_POS[2].z - 1,
                 block.WATER.id)


def build_first_passage(mc):
    '''
        Build the "First Passage" room in Minecraft Pi
    '''
    current_room = PUZZLE_ROOMS['FirstPassage']
    # Fill the room with air
    mc.setBlocks(current_room.left + STAGE_POS[0].x,
                 STAGE_POS[0].y,
                 current_room.top + STAGE_POS[0].z,
                 current_room.right + STAGE_POS[0].x - 1,
                 STAGE_POS[0].y + 13,
                 current_room.bottom + STAGE_POS[0].z - 1,
                 block.AIR.id)

    # Fill the block in side with lava
    game_room = current_room.inflate(-3)
    mc.setBlocks(game_room.left+STAGE_POS[0].x, STAGE_POS[0].y, game_room.top+STAGE_POS[0].z,
                 game_room.right+STAGE_POS[0].x, STAGE_POS[0].y+13, game_room.top+STAGE_POS[0].z,
                 block.SANDSTONE.id)
    mc.setBlocks(game_room.left+STAGE_POS[0].x, STAGE_POS[0].y, game_room.bottom+STAGE_POS[0].z,
                 game_room.right+STAGE_POS[0].x, STAGE_POS[0].y+13, game_room.bottom+STAGE_POS[0].z,
                 block.SANDSTONE.id)
    mc.setBlocks(game_room.left+STAGE_POS[0].x, STAGE_POS[0].y, game_room.top+STAGE_POS[0].z,
                 game_room.left+STAGE_POS[0].x, STAGE_POS[0].y+13, game_room.bottom+STAGE_POS[0].z,
                 block.SANDSTONE.id)
    mc.setBlocks(game_room.right+STAGE_POS[0].x, STAGE_POS[0].y, game_room.top+STAGE_POS[0].z,
                 game_room.right+STAGE_POS[0].x, STAGE_POS[0].y+13, game_room.bottom+STAGE_POS[0].z,
                 block.SANDSTONE.id)

    # Build the surrounded wall of the room
    mc.setBlocks(current_room.inflate(-4).left + STAGE_POS[0].x,
                 STAGE_POS[0].y,
                 current_room.inflate(-4).top + STAGE_POS[0].z,
                 current_room.inflate(-4).right + STAGE_POS[0].x,
                 STAGE_POS[0].y + 3,
                 current_room.inflate(-4).bottom + STAGE_POS[0].z,
                 block.LAVA.id)

    all_pillars = []
    while len(all_pillars) < 7:
        is_valid = True
        # Randomly placed pillars
        x_target = random.randint(
                            current_room.left+STAGE_POS[0].x+4,
                            current_room.right+STAGE_POS[0].x-5,
                        )
        y_target = random.randint(STAGE_POS[0].y, STAGE_POS[0].y+5)
        z_target = random.randint(
                            current_room.top+STAGE_POS[0].z+4,
                            current_room.bottom+STAGE_POS[0].z-5,
                        )
        # Each pillars distance from each other is > 3
        for pillar in all_pillars:
            distance = math.sqrt((x_target - pillar.x) ** 2 +
                                 (z_target - pillar.z) ** 2)
            if distance < 3:
                is_valid = False
                break
        if is_valid:
            all_pillars.append(Vec3(x_target, y_target, z_target))
            mc.setBlocks(x_target, y_target, z_target,
                         x_target, y_target+5, z_target,
                         block.SANDSTONE.id)
            break
    return all_pillars


def remove_block(mc, pos):
    mc.setBlock(pos.x, pos.y, pos.z, block.AIR.id)
