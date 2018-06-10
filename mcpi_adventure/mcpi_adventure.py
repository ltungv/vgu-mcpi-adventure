from game import play_quackamole
from shapes import Point
from mcpi.minecraft import Minecraft
from mcpi.vec3 import Vec3
from mcpi import block
from helpers import build_inversed_pyramid
from helpers import build_dungeon
from helpers import build_quack_a_mole
from layout import create_dungeon_layouts
from constants import (
        PYRAMID_HEIGHT,
        STAGE_POS,
        EASY_MAZE_HEIGHT,
        EASY_MAZE_WIDTH,
        MEDIUM_MAZE_HEIGHT,
        MEDIUM_MAZE_WIDTH,
        HARD_MAZE_HEIGHT,
        HARD_MAZE_WIDTH,
        PUZZLE_ROOMS
    )


def world_init():
    mc = Minecraft.create()

    # World Initialization
    print("[INFO] GENERATING WORLD! PLEASE WAIT")
    mc.setting('world_immutable', True)
    mc.setBlocks(-128, -64, -128, 128, 64, 128, block.AIR.id)
    mc.setBlocks(-128, -64, -128, 128, -60, 128, block.SANDSTONE.id)

    # Build pyramid
    print("[INFO] BUIDLING PYRAMID")
    build_inversed_pyramid(
                    mc, pos_start=Vec3(0, 0, 0),
                    height=PYRAMID_HEIGHT, size_offset=30,
                    block_type=block.SANDSTONE.id
                )

    print("[INFO] ADDING FLOORS")
    mc.setBlocks(
            STAGE_POS[0].x + 1,
            STAGE_POS[0].y - 1,
            STAGE_POS[0].z + 1,
            STAGE_POS[0].x + EASY_MAZE_WIDTH - 2,
            STAGE_POS[0].y - 1,
            STAGE_POS[0].z + EASY_MAZE_HEIGHT - 2,
            block.GLOWSTONE_BLOCK.id
        )
    mc.setBlocks(
            STAGE_POS[1].x + 1,
            STAGE_POS[1].y - 1,
            STAGE_POS[1].z + 1,
            STAGE_POS[1].x + MEDIUM_MAZE_WIDTH - 2,
            STAGE_POS[1].y - 1,
            STAGE_POS[1].z + MEDIUM_MAZE_HEIGHT - 2,
            block.GLOWSTONE_BLOCK.id
        )
    mc.setBlocks(
            STAGE_POS[2].x + 1,
            STAGE_POS[2].y - 1,
            STAGE_POS[2].z + 1,
            STAGE_POS[2].x + HARD_MAZE_WIDTH - 2,
            STAGE_POS[2].y - 1,
            STAGE_POS[2].z + HARD_MAZE_HEIGHT - 2,
            block.GLOWSTONE_BLOCK.id
        )

    # # Generating dungeon state to a .csv file
    # create_dungeon_layouts(block_type=block.SANDSTONE.id)

    print("[INFO] Building easy dungeon")
    build_dungeon(mc, STAGE_POS[0], path='layout/easy')

    print("[INFO] Building medium dungeon")
    build_dungeon(mc, STAGE_POS[1], path='layout/medium')

    print("[INFO] Building hard dungeon")
    build_dungeon(mc, STAGE_POS[2], path='layout/hard')

    print("[INFO] Building quack a mole room")
    build_quack_a_mole(mc)

    print("[INFO] FINISHED GENERATING WORLD")


def main():
    mc = Minecraft.create()
    completed = {
            'QuackAMole': False,
            'FirstPassage': False,
            'SecondPassage': False,
            'RedRoom': False,
            'Quiz': False,
            'Chess': False,
            'WaterRoom': False
            }
    player_dungeon = 0

    player = mc.player
    while True:
        player_pos = player.getTilePos()
        player_pos_2d = Point(player_pos.x, player_pos.z)
        # TODO: Add draw_map() to game.py
        # draw_map(player_pos)

        if player_dungeon == 0:
            if (PUZZLE_ROOMS['QuackAMole'].contains(player_pos_2d)
                    and not completed['QuackAMole']):
                mc.postToChat("Destroy the TNTs as fast as you can")
                mc.postToChat("DO NOT LEAVE THE ROOM BEFORE FINISHING THE GAME")
                # exit_code = play_quackamole(mc, player)
                # if exit_code == 0:
                #     mc.posToChat('Puzzle completed')
                #     completed['QuackAMole'] = True
                # elif exit_code == 1:
                #     mc.posToChat('Puzzle failed')
                # elif exit_code == 2:
                #     mc.posToChat('You left the room before finishing the puzzle')
            if (PUZZLE_ROOMS['FirstPassage'].contains(player_pos_2d)
                    and not completed['FirstPassage']):
                mc.postToChat("Find your way to the other side of the room")
                mc.postToChat("DO NOT LEAVE THE ROOM BEFORE FINISHING THE GAME")
        elif player_dungeon == 1:
            if (PUZZLE_ROOMS['SecondPassage'].contains(player_pos_2d)
                    and not completed['SecondPassage']):
                pass
            if (PUZZLE_ROOMS['RedRoom'].contains(player_pos_2d)
                    and not completed['RedRoom']):
                pass
        elif player_dungeon == 2:
            if (PUZZLE_ROOMS['Quiz'].contains(player_pos_2d)
                    and not completed['Quiz']):
                pass
            if (PUZZLE_ROOMS['Chess'].contains(player_pos_2d)
                    and not completed['Chess']):
                pass
            if (PUZZLE_ROOMS['WaterRoom'].contains(player_pos_2d)
                    and not completed['WaterRoom']):
                pass
            pass


if __name__ == '__main__':
    world_init()
    # main()
