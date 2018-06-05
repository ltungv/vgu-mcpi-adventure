import mcpi.block as block
import random
import os
import time
import numpy as np


def build_dungeon(mc, pos, path):
    print("[INFO] Generating dungeons layouts")
    layouts = [f for f in os.listdir(path)]
    selected_layout = random.choice(layouts)
    tiles = np.genfromtxt(
                    os.path.join(path, selected_layout),
                    delimiter=',', dtype=None
                )
    for posz, row in enumerate(tiles):
        for posx, tile in enumerate(row):
            mc.setBlocks(posx + pos.x, pos.y, posz + pos.z,
                         posx + pos.z, pos.y + 1, posz + pos.z,
                         tile)
            time.sleep(0.05)


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


def remove_block(mc, pos):
    mc.setBlock(pos.x, pos.y, pos.z, block.AIR.id)
