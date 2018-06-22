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
                mc.setBlocks(tile_pos.x, tile_pos.y + 2, tile_pos.z,
                             tile_pos.x, tile_pos.y + 13, tile_pos.z,
                             block.SANDSTONE.id)
            elif (PUZZLE_ROOMS['Water'].inflate(1).contains(Point(posx, posz)) and
                  difficulty == 'hard'):
                mc.setBlocks(tile_pos.x, tile_pos.y, tile_pos.z,
                             tile_pos.x, tile_pos.y + 13, tile_pos.z,
                             tile)
            else:
                mc.setBlocks(tile_pos.x, tile_pos.y, tile_pos.z,
                             tile_pos.x, tile_pos.y + 10, tile_pos.z,
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
        mc.setBlocks(bound_left, pos_y, bound_bottom, bound_right, pos_y, bound_bottom, block_type)
        mc.setBlocks(bound_left, pos_y, bound_top, bound_left, pos_y, bound_bottom, block_type)
        mc.setBlocks(bound_right, pos_y, bound_top, bound_right, pos_y, bound_bottom, block_type)


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
        if is_valid:
            all_pillars.append(Vec3(x_target, y_target, z_target))
            mc.setBlocks(x_target, y_target, z_target,
                         x_target, y_target+5, z_target,
                         block.SANDSTONE.id)
    return all_pillars


def build_red(mc):
    '''
        Build the "red" room in Minecraft Pi
    '''
    width = 26
    height = 13
    depth = 34

    current_room = PUZZLE_ROOMS['Red']
    x = current_room.left + STAGE_POS[1].x-3
    z = current_room.top + STAGE_POS[1].z
    y = STAGE_POS[1].y

    # room
    mc.setBlocks(x+3, y, z, x+3+depth, y+height, z+width, block.BRICK_BLOCK.id)
    mc.setBlocks(x+4, y, z+1, x+2+depth, y+height-1, z+width-1, block.AIR.id)

    # floor
    mc.setBlocks(x+2, y-1, z-1, x+4+depth, y-1, z+1+width, block.COBBLESTONE.id)

    # Torch
    mc.setBlocks(x+4, y+2, z+1, x+2+depth, y+2, z+1, 50, 1)
    mc.setBlocks(x+4, y+2, z+width-1, x+2+depth, y+2, z+width-1, 50, 2)

    # Bulding the R
    # first character
    mc.setBlocks(x+3+depth-1, y, z+width-3, x+3+depth-1, y+5, z+width-3, block.GLOWSTONE_BLOCK.id)
    # else
    mc.setBlocks(x+3+depth-1, y+5, z+width-3, x+3+depth-1, y+3, z+width-8, block.GLOWSTONE_BLOCK.id)
    mc.setBlock(x+3+depth-1, y+2, z+width-6,  block.GLOWSTONE_BLOCK.id)
    mc.setBlock(x+3+depth-1, y+1, z+width-7,  block.GLOWSTONE_BLOCK.id)
    mc.setBlock(x+3+depth-1, y, z+width-8,  block.GLOWSTONE_BLOCK.id)
    # Bulding the E
    mc.setBlocks(x+3+depth-1, y, z+width-10, x+3+depth-1, y+5, z+width-10, block.GLOWSTONE_BLOCK.id)
    mc.setBlocks(x+3+depth-1, y+5, z+width-10, x+3+depth-1, y+5, z+width-15, block.GLOWSTONE_BLOCK.id)
    mc.setBlocks(x+3+depth-1, y+3, z+width-10, x+3+depth-1, y+3, z+width-15, block.GLOWSTONE_BLOCK.id)
    mc.setBlocks(x+3+depth-1, y, z+width-10, x+3+depth-1, y, z+width-15, block.GLOWSTONE_BLOCK.id)
    # Bulding the D
    mc.setBlocks(x+3+depth-1, y, z+width-17, x+3+depth-1, y+5, z+width-22, block.GLOWSTONE_BLOCK.id)
    mc.setBlocks(x+3+depth-1, y+5, z+width-20, x+3+depth-1, y+5, z+width-22, 0)
    mc.setBlocks(x+3+depth-1, y, z+width-20, x+3+depth-1, y, z+width-22, 0)
    mc.setBlock(x+3+depth-1, y+4, z+width-22, 0)
    mc.setBlock(x+3+depth-1, y, z+width-22, 0)
    mc.setBlocks(x+3+depth-1, y+2, z+width-18, x+3+depth-1, y+3, z+width-20, 0)


def build_chess(mc):
    '''
        Build the Chess room in Minecraft Pi
    '''
    current_room = PUZZLE_ROOMS['Chess']

    x = current_room.left + STAGE_POS[2].x-3
    z = current_room.top + STAGE_POS[2].z
    y = STAGE_POS[2].y

    width = 49
    height = 13
    depth = 49

    # room
    mc.setBlocks(x+3, y, z, x+3+depth, y+height, z+width, block.BRICK_BLOCK.id)
    mc.setBlocks(x+4, y, z+1, x+2+depth, y+height-1, z+width-1, block.AIR.id)

    # Chess table Building
    # First ROW of Chess
    mc.setBlocks(x+4, y, z+1,  x+4+5, y, z+6,   block.WOOL.id, 0)
    mc.setBlocks(x+4, y, z+7,  x+4+5, y, z+12,  block.WOOL.id, 15)
    mc.setBlocks(x+4, y, z+13, x+4+5, y, z++18, block.WOOL.id, 0)
    mc.setBlocks(x+4, y, z+19, x+4+5, y, z++24, block.WOOL.id, 15)
    mc.setBlocks(x+4, y, z+25, x+4+5, y, z++30, block.WOOL.id, 0)
    mc.setBlocks(x+4, y, z+31, x+4+5, y, z++36, block.WOOL.id, 15)
    mc.setBlocks(x+4, y, z+37, x+4+5, y, z++42, block.WOOL.id, 0)
    mc.setBlocks(x+4, y, z+43, x+4+5, y, z++48, block.WOOL.id, 15)

    # Second ROW of Chess
    mc.setBlocks(x+4+6, y, z+1,  x+4+11, y, z+6,  block.WOOL.id, 15)
    mc.setBlocks(x+4+6, y, z+7,  x+4+11, y, z+12, block.WOOL.id, 0)
    mc.setBlocks(x+4+6, y, z+13, x+4+11, y, z+18, block.WOOL.id, 15)
    mc.setBlocks(x+4+6, y, z+19, x+4+11, y, z+24, block.WOOL.id, 0)
    mc.setBlocks(x+4+6, y, z+25, x+4+11, y, z+30, block.WOOL.id, 15)
    mc.setBlocks(x+4+6, y, z+31, x+4+11, y, z+36, block.WOOL.id, 0)
    mc.setBlocks(x+4+6, y, z+37, x+4+11, y, z+42, block.WOOL.id, 15)
    mc.setBlocks(x+4+6, y, z+43, x+4+11, y, z+48, block.WOOL.id, 0)

    # Third ROW of Chess
    mc.setBlocks(x+4+12, y, z+1,  x+4+17, y, z+6,  block.WOOL.id, 0)
    mc.setBlocks(x+4+12, y, z+7,  x+4+17, y, z+12, block.WOOL.id, 15)
    mc.setBlocks(x+4+12, y, z+13, x+4+17, y, z+18, block.WOOL.id, 0)
    mc.setBlocks(x+4+12, y, z+19, x+4+17, y, z+24, block.WOOL.id, 15)
    mc.setBlocks(x+4+12, y, z+25, x+4+17, y, z+30, block.WOOL.id, 0)
    mc.setBlocks(x+4+12, y, z+31, x+4+17, y, z+36, block.WOOL.id, 15)
    mc.setBlocks(x+4+12, y, z+37, x+4+17, y, z+42, block.WOOL.id, 0)
    mc.setBlocks(x+4+12, y, z+43, x+4+17, y, z+48, block.WOOL.id, 15)

    # Forth ROW of Chess
    mc.setBlocks(x+4+18, y, z+1,  x+4+23, y, z+6,  block.WOOL.id, 15)
    mc.setBlocks(x+4+18, y, z+7,  x+4+23, y, z+12,  block.WOOL.id, 0)
    mc.setBlocks(x+4+18, y, z+13, x+4+23, y, z+18, block.WOOL.id, 15)
    mc.setBlocks(x+4+18, y, z+19, x+4+23, y, z+24, block.WOOL.id, 0)
    mc.setBlocks(x+4+18, y, z+25, x+4+23, y, z+30, block.WOOL.id, 15)
    mc.setBlocks(x+4+18, y, z+31, x+4+23, y, z+36, block.WOOL.id, 0)
    mc.setBlocks(x+4+18, y, z+37, x+4+23, y, z+42, block.WOOL.id, 15)
    mc.setBlocks(x+4+18, y, z+43, x+4+23, y, z+48, block.WOOL.id, 0)

    # Fifth ROW of Chess
    mc.setBlocks(x+4+24, y, z+1,  x+4+29, y, z+6,  block.WOOL.id, 0)
    mc.setBlocks(x+4+24, y, z+7,  x+4+29, y, z+12, block.WOOL.id, 15)
    mc.setBlocks(x+4+24, y, z+13, x+4+29, y, z+18, block.WOOL.id, 0)
    mc.setBlocks(x+4+24, y, z+19, x+4+29, y, z+24, block.WOOL.id, 15)
    mc.setBlocks(x+4+24, y, z+25, x+4+29, y, z+30, block.WOOL.id, 0)
    mc.setBlocks(x+4+24, y, z+31, x+4+29, y, z+36, block.WOOL.id, 15)
    mc.setBlocks(x+4+24, y, z+37, x+4+29, y, z+42, block.WOOL.id, 0)
    mc.setBlocks(x+4+24, y, z+43, x+4+29, y, z+48, block.WOOL.id, 15)

    # Sixth ROW of Chess
    mc.setBlocks(x+4+30, y, z+1,  x+4+35, y, z+6,  block.WOOL.id, 15)
    mc.setBlocks(x+4+30, y, z+7,  x+4+35, y, z+12, block.WOOL.id, 0)
    mc.setBlocks(x+4+30, y, z+13, x+4+35, y, z+18, block.WOOL.id, 15)
    mc.setBlocks(x+4+30, y, z+19, x+4+35, y, z+24, block.WOOL.id, 0)
    mc.setBlocks(x+4+30, y, z+25, x+4+35, y, z+30, block.WOOL.id, 15)
    mc.setBlocks(x+4+30, y, z+31, x+4+35, y, z+36, block.WOOL.id, 0)
    mc.setBlocks(x+4+30, y, z+37, x+4+35, y, z+42, block.WOOL.id, 15)
    mc.setBlocks(x+4+30, y, z+43, x+4+35, y, z+48, block.WOOL.id, 0)

    # Seventh ROW of Chess
    mc.setBlocks(x+4+36, y, z+1,  x+4+41, y, z+6,  block.WOOL.id, 0)
    mc.setBlocks(x+4+36, y, z+7,  x+4+41, y, z+12, block.WOOL.id, 15)
    mc.setBlocks(x+4+36, y, z+13, x+4+41, y, z+18, block.WOOL.id, 0)
    mc.setBlocks(x+4+36, y, z+19, x+4+41, y, z+24, block.WOOL.id, 15)
    mc.setBlocks(x+4+36, y, z+25, x+4+41, y, z+30, block.WOOL.id, 0)
    mc.setBlocks(x+4+36, y, z+31, x+4+41, y, z+36, block.WOOL.id, 15)
    mc.setBlocks(x+4+36, y, z+37, x+4+41, y, z+42, block.WOOL.id, 0)
    mc.setBlocks(x+4+36, y, z+43, x+4+41, y, z+48, block.WOOL.id, 15)

    # Eighth ROW of Chess
    mc.setBlocks(x+4+42, y, z+1,  x+4+47, y, z+6,  block.WOOL.id, 15)
    mc.setBlocks(x+4+42, y, z+7,  x+4+47, y, z+12, block.WOOL.id, 0)
    mc.setBlocks(x+4+42, y, z+13, x+4+47, y, z+18, block.WOOL.id, 15)
    mc.setBlocks(x+4+42, y, z+19, x+4+47, y, z+24, block.WOOL.id, 0)
    mc.setBlocks(x+4+42, y, z+25, x+4+47, y, z+30, block.WOOL.id, 15)
    mc.setBlocks(x+4+42, y, z+31, x+4+47, y, z+36, block.WOOL.id, 0)
    mc.setBlocks(x+4+42, y, z+37, x+4+47, y, z+42, block.WOOL.id, 15)
    mc.setBlocks(x+4+42, y, z+43, x+4+47, y, z+48, block.WOOL.id, 0)

    # Make the DOOR
    mc.setBlocks(x+3, y, z+4, x+3, y+2, z+4, 0)

    # Torch for lighting
    for i in range(1, depth, +3):
        for k in range(4, height, +3):
            mc.setBlock(x+3+i, y+k, z+1, 50, 1)
            mc.setBlock(x+3+i, y+k, z+width-1, 50, 2)


def build_second_passage(mc):
    current_room = PUZZLE_ROOMS['SecondPassage']

    x = current_room.left + STAGE_POS[1].x-3
    z = current_room.top + STAGE_POS[1].z
    y = STAGE_POS[1].y
    width = 14
    height = 13
    depth = 44

    # room
    mc.setBlocks(x+3, y, z, x+3+depth, y+height, z+width, block.BRICK_BLOCK.id)
    mc.setBlocks(x+4, y, z+1, x+2+depth, y+height-1, z+width-1, block.AIR.id)

    # floor
    mc.setBlocks(x+2, y-1, z-1, x+4+depth, y-1, z+1+width, block.COBBLESTONE.id)

    # door
    mc.setBlock(x+3, y, z+1, 0)
    mc.setBlock(x+3, y+1, z+1, 0)

    # doorpassage
    mc.setBlocks(x+3, y+height-2, z+4, x+3, y+height-3, z+4, 0)
    mc.setBlocks(x+3, y+height-4, z, x+3+10, y+height-4, z+width, block.COBBLESTONE.id)

    # door to out
    mc.setBlocks(x+3+depth-3, y+height-4, z+width, x+3+depth, y+height-3, z+width, 0)

    # Lava
    mc.setBlocks(x+4, y, z+1, x+3+depth-1, y+height-6, z+width-1, 11)
    mc.setBlocks(x+3, y, z+1, x+3, y+1, z+1, block.BRICK_BLOCK.id)


def remove_block(mc, pos):
    mc.setBlock(pos.x, pos.y, pos.z, block.AIR.id)
