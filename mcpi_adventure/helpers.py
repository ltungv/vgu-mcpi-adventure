import mcpi.block as block
import random
import os
import time
import numpy as np
from constants import PUZZLE_ROOMS, STAGE_POS


def build_dungeon(mc, pos, path):
    layouts = [f for f in os.listdir(path)]
    selected_layout = random.choice(layouts)
    tiles = np.genfromtxt(
                    os.path.join(path, selected_layout),
                    delimiter=',', dtype=None
                )
    for posz, row in enumerate(tiles):
        for posx, tile in enumerate(row):
            print("[DEBUG] x=%d, y=%d, z=%d, tile=%d"
                  % (posx + pos.x, pos.y, posz + pos.z, tile))
            mc.setBlocks(posx + pos.x, pos.y, posz + pos.z,
                         posx + pos.z, pos.y + 1, posz + pos.z,
                         tile)


def build_inversed_pyramid(mc, pos_start, height, size_offset=0, block_type=block.SANDSTONE.id):
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
    current_room = PUZZLE_ROOMS['QuackAMole']
    stage_posy = STAGE_POS[0].y
    stage_posx = int(current_room.left + (current_room.width - 10) / 2)
    stage_posz = int(current_room.top + (current_room.height - 10) / 2)
    mc.setBlocks(stage_posx, stage_posy, stage_posz,
                 stage_posx + 10, stage_posy, stage_posz + 10,
                 block.WOOL.id, 14)


def remove_block(mc, pos):
    mc.setBlock(pos.x, pos.y, pos.z, block.AIR.id)
