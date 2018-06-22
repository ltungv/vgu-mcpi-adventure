from game import play_quackamole
from game import play_water
from game import play_first_passage
from game import trap_box
from game import play_second_passage
from game import play_red
from builders import build_inversed_pyramid
from shapes import Point
from helpers import enter_dungeon
from helpers import tts_chat
from mcpi.minecraft import Minecraft
from mcpi import block
from helpers import game_reset, reset_dungeon
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
        CHEAT_ROOMS,
        LEDs
    )
import RPi.GPIO as GPIO
import time


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
for led in LEDs:
    GPIO.setup(led, GPIO.OUT)


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
    mc.setBlocks(-128, -64, -128, 128, 64, 128, block.AIR.id)
    mc.setBlocks(-128, -64, -128, 128, -60, 128, block.SANDSTONE.id)

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
    mc.setBlocks(-75, PYRAMID_POS.y + PYRAMID_HEIGHT - 1, -75,
                 75, PYRAMID_POS.y + PYRAMID_HEIGHT - 1, 75,
                 block.GLOWSTONE_BLOCK.id)

    # Generating dungeon state to a .csv file
    # create_dungeon_layouts(block_type=block.SANDSTONE.id)

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
        if player_pos.y >= STAGE_POS[0].y and player_pos.y <= STAGE_POS[0].y + 13:
            if (PUZZLE_ROOMS['Quack'].contains(player_pos_2d, -STAGE_POS[0].x, -STAGE_POS[0].z)
                    and not entered_room['Quack']):
                entered_room['Quack'] = True
                tts_chat(mc, "Enter the red stage!")
                tts_chat(mc, "Destroy the tnts before they detonate", prefix="[rules]")
                tts_chat(mc, "Do not leave the room before finishing the game", prefix="[rules]")
                exit_code = play_quackamole(mc, player)
                if exit_code == 0:
                    tts_chat(mc, 'Puzzle completed')
                    completed['Quack'] = True
                else:
                    if exit_code == 1:
                        tts_chat(mc, 'Puzzle failed')
                    elif exit_code == 2:
                        tts_chat(mc, 'You left the room before finishing the puzzle')
                    tts_chat(mc, "The game will reset in 5 seconds")
                    time.sleep(5)
                    entered_room, completed, all_pillars = game_reset(mc)

            if (PUZZLE_ROOMS['FirstPassage'].contains(player_pos_2d, -STAGE_POS[0].x, -STAGE_POS[0].z)
                    and not entered_room['FirstPassage']):
                entered_room['FirstPassage'] = True
                exit_code = play_first_passage(mc, player, all_pillars)
                if exit_code == 0:
                    tts_chat(mc, 'Puzzle completed')
                    completed['FirstPassage'] = True
                else:
                    if exit_code == 1:
                        tts_chat(mc, 'Puzzle failed')
                    elif exit_code == 2:
                        tts_chat(mc, 'You left the room before finishing the puzzle')
                    tts_chat(mc, "The game will reset in 5 seconds")
                    time.sleep(5)
                    entered_room, completed, all_pillars = game_reset(mc)

            if (TRAP_ROOMS['Easy1'].contains(player_pos_2d, -STAGE_POS[0].x, -STAGE_POS[0].z)):
                trap_box(mc, TRAP_ROOMS['Easy1'], STAGE_POS[0])
                tts_chat(mc, "You will now be teleported to a diffrent location")
                enter_dungeon(mc)
                inflated_room = TRAP_ROOMS['Easy1'].inflate(-1)
                mc.setBlocks(inflated_room.left+STAGE_POS[0].x, STAGE_POS[0].y, inflated_room.top+STAGE_POS[0].z,
                             inflated_room.right+STAGE_POS[0].x, STAGE_POS[0].y+13, inflated_room.bottom+STAGE_POS[0].z,
                             block.AIR.id)

            if (TRAP_ROOMS['Easy2'].contains(player_pos_2d, -STAGE_POS[0].x, -STAGE_POS[0].z)):
                trap_box(mc, TRAP_ROOMS['Easy2'], STAGE_POS[0])
                tts_chat(mc, "You will now be teleported to a diffrent location")
                enter_dungeon(mc)
                inflated_room = TRAP_ROOMS['Easy2'].inflate(-1)
                mc.setBlocks(inflated_room.left+STAGE_POS[0].x, STAGE_POS[0].y, inflated_room.top+STAGE_POS[0].z,
                             inflated_room.right+STAGE_POS[0].x, STAGE_POS[0].y+13, inflated_room.bottom+STAGE_POS[0].z,
                             block.AIR.id)

            if completed['Quack'] and completed['FirstPassage']:
                tts_chat(mc, "You now advance to the second dungeon")
                enter_dungeon(mc, 1)

        if player_pos.y >= STAGE_POS[1].y and player_pos.y <= STAGE_POS[1].y + 13:
            if (PUZZLE_ROOMS['SecondPassage'].inflate(1).contains(player_pos_2d, -STAGE_POS[1].x, -STAGE_POS[1].z)
                    and not entered_room['SecondPassage']):
                entered_room['SecondPassage'] = True
                exit_code = play_second_passage(mc)
                if exit_code == 0:
                    tts_chat(mc, 'Puzzle completed')
                    completed['SecondPassage'] = True
                else:
                    if exit_code == 1:
                        tts_chat(mc, 'Puzzle failed')
                    elif exit_code == 2:
                        tts_chat(mc, 'You left the room before finishing the puzzle')
                    tts_chat(mc, "The game will reset in 5 seconds")
                    time.sleep(5)
                    entered_room, completed, all_pillars = game_reset(mc)

            if (PUZZLE_ROOMS['Red'].inflate(1).contains(player_pos_2d, -STAGE_POS[1].x, -STAGE_POS[1].z)
                    and not entered_room['Red']):
                entered_room['Red'] = True
                exit_code = play_red(mc)
                if exit_code == 0:
                    tts_chat(mc, 'Puzzle completed')
                    completed['Red'] = True
                else:
                    if exit_code == 1:
                        tts_chat(mc, 'Puzzle failed')
                    elif exit_code == 2:
                        tts_chat(mc, 'You left the room before finishing the puzzle')
                    tts_chat(mc, "The game will reset in 5 seconds")
                    time.sleep(5)
                    entered_room, completed, all_pillars = game_reset(mc)

            if (TRAP_ROOMS['Medium1'].contains(player_pos_2d, -STAGE_POS[1].x, -STAGE_POS[1].z)):
                trap_box(mc, TRAP_ROOMS['Medium1'], STAGE_POS[1])
                tts_chat(mc, "You will now be teleported to a diffrent location")
                enter_dungeon(mc,1)
                inflated_room = TRAP_ROOMS['Medium1'].inflate(-1)
                mc.setBlocks(inflated_room.left+STAGE_POS[1].x, STAGE_POS[1].y, inflated_room.top+STAGE_POS[1].z,
                             inflated_room.right+STAGE_POS[1].x, STAGE_POS[1].y+13, inflated_room.bottom+STAGE_POS[1].z,
                             block.AIR.id)

            if (TRAP_ROOMS['Medium2'].contains(player_pos_2d, -STAGE_POS[1].x, -STAGE_POS[1].z)):
                trap_box(mc, TRAP_ROOMS['Medium2'], STAGE_POS[1])
                tts_chat(mc, "You will now be teleported to a diffrent location")
                enter_dungeon(mc,1)
                inflated_room = TRAP_ROOMS['Medium2'].inflate(-1)
                mc.setBlocks(inflated_room.left+STAGE_POS[1].x, STAGE_POS[1].y, inflated_room.top+STAGE_POS[1].z,
                             inflated_room.right+STAGE_POS[1].x, STAGE_POS[1].y+13, inflated_room.bottom+STAGE_POS[1].z,
                             block.AIR.id)

            if (TRAP_ROOMS['Medium3'].contains(player_pos_2d, -STAGE_POS[1].x, -STAGE_POS[1].z)):
                trap_box(mc, TRAP_ROOMS['Medium3'], STAGE_POS[1])
                tts_chat(mc, "You will now be teleported to a diffrent location")
                enter_dungeon(mc,1)
                inflated_room = TRAP_ROOMS['Medium3'].inflate(-1)
                mc.setBlocks(inflated_room.left+STAGE_POS[1].x, STAGE_POS[1].y, inflated_room.top+STAGE_POS[1].z,
                             inflated_room.right+STAGE_POS[1].x, STAGE_POS[1].y+13, inflated_room.bottom+STAGE_POS[1].z,
                             block.AIR.id)

            if completed['SecondPassage'] and completed['Red']:
                tts_chat(mc, "You now advance to the third dungeon")
                enter_dungeon(mc, 2)

        if player_pos.y >= STAGE_POS[2].y and player_pos.y <= STAGE_POS[2].y + 13:
            if (PUZZLE_ROOMS['Quiz'].contains(player_pos_2d, -STAGE_POS[2].x, -STAGE_POS[2].z)
                    and not entered_room['Quiz']):
                pass

            if (PUZZLE_ROOMS['Chess'].contains(player_pos_2d, -STAGE_POS[2].x, -STAGE_POS[2].z)
                    and not entered_room['Chess']):
                pass

            if (PUZZLE_ROOMS['Water'].contains(player_pos_2d, -STAGE_POS[2].x, -STAGE_POS[2].z)
                    and not entered_room['Water']):
                entered_room['Water'] = True
                tts_chat(mc, "You enter the water room")
                tts_chat(mc, "Swim to the surface to receive further instructions")
                tts_chat(mc, "Do not leave the room before finishing the game")
                exit_code = play_water(mc, player)
                if exit_code == 0:
                    tts_chat(mc, 'Puzzle completed')
                    completed['Water'] = True
                else:
                    if exit_code == 1:
                        tts_chat(mc, 'Puzzle failed')
                    elif exit_code == 2:
                        tts_chat(mc, 'You left the room before finishing the puzzle')
                    tts_chat(mc, "The game will reset in 5 seconds")
                    time.sleep(5)
                    entered_room, completed, all_pillars = game_reset(mc)

            if (TRAP_ROOMS['Hard1'].contains(player_pos_2d, -STAGE_POS[2].x, -STAGE_POS[2].z)):
                trap_box(mc, TRAP_ROOMS['Hard1'], STAGE_POS[2])
                tts_chat(mc, "You will now be teleported to a diffrent location")
                enter_dungeon(mc, 2)
                inflated_room = TRAP_ROOMS['Hard1'].inflate(-1)
                mc.setBlocks(inflated_room.left+STAGE_POS[2].x, STAGE_POS[2].y, inflated_room.top+STAGE_POS[2].z,
                             inflated_room.right+STAGE_POS[2].x, STAGE_POS[2].y+13, inflated_room.bottom+STAGE_POS[2].z,
                             block.AIR.id)

            if (TRAP_ROOMS['Hard2'].contains(player_pos_2d, -STAGE_POS[2].x, -STAGE_POS[2].z)):
                trap_box(mc, TRAP_ROOMS['Hard2'], STAGE_POS[2])
                tts_chat(mc, "You will now be teleported to a diffrent location")
                enter_dungeon(mc, 2)
                inflated_room = TRAP_ROOMS['Hard2'].inflate(-1)
                mc.setBlocks(inflated_room.left+STAGE_POS[2].x, STAGE_POS[2].y, inflated_room.top+STAGE_POS[2].z,
                             inflated_room.right+STAGE_POS[2].x, STAGE_POS[2].y+13, inflated_room.bottom+STAGE_POS[2].z,
                             block.AIR.id)

            if (TRAP_ROOMS['Hard3'].contains(player_pos_2d, -STAGE_POS[2].x, -STAGE_POS[2].z)):
                trap_box(mc, TRAP_ROOMS['Hard2'], STAGE_POS[2])
                tts_chat(mc, "You will now be teleported to a diffrent location")
                enter_dungeon(mc, 2)
                inflated_room = TRAP_ROOMS['Hard2'].inflate(-1)
                mc.setBlocks(inflated_room.left+STAGE_POS[2].x, STAGE_POS[2].y, inflated_room.top+STAGE_POS[2].z,
                             inflated_room.right+STAGE_POS[2].x, STAGE_POS[2].y+13, inflated_room.bottom+STAGE_POS[2].z,
                             block.AIR.id)

            if completed['Water'] and completed['Chess'] and completed['Quiz']:
                pass


def main():
    game_init()
    game_play()


if __name__ == '__main__':
    main()
