from game import play_quackamole
from game import play_water
from game import play_first_passage
from game import trap_box
from builders import build_inversed_pyramid
from shapes import Point
from helpers import enter_dungeon
from helpers import tts_chat
from mcpi.minecraft import Minecraft
from mcpi import block
from helpers import game_reset
from layout import create_dungeon_layouts
from constants import (
        PYRAMID_HEIGHT,
        PYRAMID_POS,
        STAGE_POS,
        EASY_MAZE_HEIGHT,
        EASY_MAZE_WIDTH,
        MEDIUM_MAZE_HEIGHT,
        MEDIUM_MAZE_WIDTH,
        HARD_MAZE_HEIGHT,
        HARD_MAZE_WIDTH,
        PUZZLE_ROOMS,
        TRAP_ROOMS,
        CHEAT_ROOMS
    )
import time


def game_init():
    '''
        Build basic structure of the game in Minecraft Pi
    '''
    mc = Minecraft.create()

    # World Initialization
    print("[INFO] GENERATING WORLD! PLEASE WAIT")
    mc.setBlocks(PYRAMID_POS.x, PYRAMID_POS.y-2, PYRAMID_POS.z,
                 PYRAMID_POS.x, PYRAMID_POS.y-3, PYRAMID_POS.z,
                 block.AIR.id)
    # Settings and clear to flat
    # mc.setting('world_immutable', True)
    # mc.setBlocks(-128, -64, -128, 128, 64, 128, block.AIR.id)
    # mc.setBlocks(-128, -64, -128, 128, -60, 128, block.SANDSTONE.id)
    mc.setBlocks(-128, 0, -128, 128, 64, 128, block.AIR.id)
    mc.setBlocks(-128, 0, -128, 128, -3, 128, block.LAVA.id)

    # Build pyramid
    print("[INFO] BUIDLING PYRAMID")
    build_inversed_pyramid(
                    mc, pos_start=PYRAMID_POS,
                    height=PYRAMID_HEIGHT, size_offset=30,
                    block_type=block.SANDSTONE.id
                )

    print("[INFO] ADDING FLOORS")
    mc.setBlocks(
            STAGE_POS[0].x + 2,
            STAGE_POS[0].y - 1,
            STAGE_POS[0].z + 2,
            STAGE_POS[0].x + EASY_MAZE_WIDTH - 3,
            STAGE_POS[0].y - 1,
            STAGE_POS[0].z + EASY_MAZE_HEIGHT - 3,
            block.GLOWSTONE_BLOCK.id
        )
    mc.setBlocks(
            STAGE_POS[1].x + 2,
            STAGE_POS[1].y - 1,
            STAGE_POS[1].z + 2,
            STAGE_POS[1].x + MEDIUM_MAZE_WIDTH - 3,
            STAGE_POS[1].y - 1,
            STAGE_POS[1].z + MEDIUM_MAZE_HEIGHT - 3,
            block.GLOWSTONE_BLOCK.id
        )
    mc.setBlocks(
            STAGE_POS[2].x + 2,
            STAGE_POS[2].y - 1,
            STAGE_POS[2].z + 2,
            STAGE_POS[2].x + HARD_MAZE_WIDTH - 3,
            STAGE_POS[2].y - 1,
            STAGE_POS[2].z + HARD_MAZE_HEIGHT - 3,
            block.GLOWSTONE_BLOCK.id
        )
    mc.setBlocks(-75, PYRAMID_POS.y + PYRAMID_HEIGHT, -75,
                 75, PYRAMID_POS.y + PYRAMID_HEIGHT, 75,
                 block.GLOWSTONE_BLOCK.id)

    # Generating dungeon state to a .csv file
    create_dungeon_layouts(block_type=block.SANDSTONE.id)

    print("[INFO] FINISHED GENERATING WORLD")


def game_play():
    mc = Minecraft.create()
    player = mc.player

    player_connected = False
    # TODO: Restart dungeon when puzzle failed
    while True:
        # Exception when player on RaspberrJuice plugin
        # has not connected to the server
        try:
            player_pos = player.getTilePos()
            player_pos_2d = Point(player_pos.x, player_pos.z)
        except Exception:
            print("[ERROR] Player not connected")
            print("[INFO] RETRYING IN 10 SECONDS")
            time.sleep(10)
            continue
        # TODO: Add draw_map() to game.py
        # draw_map(player_pos)

        # Start game if player connects
        if not player_connected:
            entered_room, completed, all_pillars = game_reset(mc)
            player_connected = True

        # Checking the player postion and start the room's puzzle
        # based on his / her postion
        # The game is totally reset when the player fails a puzzle
        if player_pos.y >= STAGE_POS[0].y and player_pos.y <= STAGE_POS[0].y + 14:
            if (PUZZLE_ROOMS['Quack'].contains(player_pos_2d, -STAGE_POS[0].x, -STAGE_POS[0].z)
                    and not entered_room['Quack']):
                entered_room['Quack'] = True
                tts_chat(mc, "ENTER THE RED STAGE!")
                tts_chat(mc, "DESTROY THE TNTS BEFORE THEY DETONATE", prefix="[RULES]")
                tts_chat(mc, "DO NOT LEAVE THE ROOM BEFORE FINISHING THE GAME", prefix="[RULES]")
                exit_code = play_quackamole(mc, player)
                if exit_code == 0:
                    tts_chat(mc, 'PUZZLE COMPLETED')
                    completed['Quack'] = True
                else:
                    if exit_code == 1:
                        tts_chat(mc, 'PUZZLE FAILED')
                    elif exit_code == 2:
                        tts_chat(mc, 'YOU LEFT THE ROOM BEFORE FINISHING THE PUZZLE')
                    entered_room, completed = game_reset(mc)

            if (PUZZLE_ROOMS['FirstPassage'].contains(player_pos_2d, -STAGE_POS[0].x, -STAGE_POS[0].z)
                    and not entered_room['FirstPassage']):
                entered_room['FirstPassage'] = True
                tts_chat(mc, "PLACE GLOWSTONES ONTOP OF THE 7 PILLARS", prefix="[RULES]")
                tts_chat(mc, "THE LAVA WITH RAISE EVERY 5 SECONDS", prefix="[RULES]")
                tts_chat(mc, "DO NOT LEAVE THE ROOM BEFORE FINISHING THE GAME", prefix="[RULES]")
                exit_code = play_first_passage(mc, player, all_pillars)
                if exit_code == 0:
                    tts_chat(mc, 'PUZZLE COMPLETED')
                    completed['FirstPassage'] = True
                else:
                    if exit_code == 1:
                        tts_chat(mc, 'PUZZLE FAILED')
                    elif exit_code == 2:
                        tts_chat(mc, 'YOU LEFT THE ROOM BEFORE FINISHING THE PUZZLE')
                    entered_room, completed = game_reset(mc)

            if (TRAP_ROOMS['Easy1'].contains(player_pos_2d, -STAGE_POS[0].x, -STAGE_POS[0].z)):
                trap_box(mc, TRAP_ROOMS['Easy1'], STAGE_POS[0])

            if (TRAP_ROOMS['Easy1'].contains(player_pos_2d, -STAGE_POS[0].x, -STAGE_POS[0].z)):
                current_room = TRAP_ROOMS['Easy2']

            if completed['Quack'] and completed['FirstPassage']:
                tts_chat(mc, "YOU NOW ADVANCE TO THE SECOND DUNGEON")
                enter_dungeon(mc, 1)

        if player_pos.y >= STAGE_POS[1].y and player_pos.y <= STAGE_POS[1].y + 14:
            if (PUZZLE_ROOMS['SecondPassage'].contains(player_pos_2d)
                    and not entered_room['SecondPassage']):
                pass

            if (PUZZLE_ROOMS['Red'].contains(player_pos_2d)
                    and not entered_room['Red']):
                pass

            if (TRAP_ROOMS['Medium1'].contains(player_pos_2d, -STAGE_POS[1].x, -STAGE_POS[1].z)):
                current_room = TRAP_ROOMS['Medium1']

            if (TRAP_ROOMS['Medium2'].contains(player_pos_2d, -STAGE_POS[1].x, -STAGE_POS[1].z)):
                current_room = TRAP_ROOMS['Medium2']

            if (TRAP_ROOMS['Medium3'].contains(player_pos_2d, -STAGE_POS[1].x, -STAGE_POS[1].z)):
                current_room = TRAP_ROOMS['Medium3']

            if completed['SecondPassage'] and completed['Red']:
                tts_chat(mc, "YOU NOW ADVANCE TO THE THIRD DUNGEON")
                enter_dungeon(mc, 1)

        if player_pos.y >= STAGE_POS[2].y and player_pos.y <= STAGE_POS[2].y + 14:
            if (PUZZLE_ROOMS['Quiz'].contains(player_pos_2d)
                    and not entered_room['Quiz']):
                pass

            if (PUZZLE_ROOMS['Chess'].contains(player_pos_2d)
                    and not entered_room['Chess']):
                pass

            if (PUZZLE_ROOMS['Water'].contains(player_pos_2d, -STAGE_POS[2].x, -STAGE_POS[2].z)
                    and not entered_room['Water']):
                entered_room['Water'] = True
                tts_chat(mc, "YOU ENTER THE WATER Room")
                tts_chat(mc, "SWIM TO THE SURFACE To receive further instructions")
                tts_chat(mc, "DO NOT LEAVE THE ROOM BEFORE FINISHING THE GAME")
                exit_code = play_water(mc, player)
                if exit_code == 0:
                    tts_chat(mc, 'PUZZLE COMPLETED')
                    completed['Water'] = True
                else:
                    if exit_code == 1:
                        tts_chat(mc, 'PUZZLE FAILED')
                    elif exit_code == 2:
                        tts_chat(mc, 'YOU LEFT THE ROOM BEFore finishing the puzzle')
                    entered_room, completed = game_reset(mc)

            if (TRAP_ROOMS['Hard1'].contains(player_pos_2d, -STAGE_POS[2].x, -STAGE_POS[2].z)):
                current_room = TRAP_ROOMS['Hard1']

            if (TRAP_ROOMS['Hard2'].contains(player_pos_2d, -STAGE_POS[2].x, -STAGE_POS[2].z)):
                current_room = TRAP_ROOMS['Hard2']

            if (TRAP_ROOMS['Hard3'].contains(player_pos_2d, -STAGE_POS[2].x, -STAGE_POS[2].z)):
                current_room = TRAP_ROOMS['Hard3']

            if completed['Water'] and completed['Chess'] and completed['Quiz']:
                pass


def main():
    game_init()
    game_play()


if __name__ == '__main__':
    main()
