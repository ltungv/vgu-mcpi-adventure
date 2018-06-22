from constants import EASY_MAZE_WIDTH, EASY_MAZE_HEIGHT
from constants import MEDIUM_MAZE_WIDTH, MEDIUM_MAZE_HEIGHT
from constants import HARD_MAZE_WIDTH, HARD_MAZE_HEIGHT
from constants import TRAP_ROOMS, CHEAT_ROOMS, PUZZLE_ROOMS
from constants import STAGE_POS, PYRAMID_POS
from constants import LEDs
from builders import build_dungeon, build_quack_a_mole, build_water, build_first_passage
from builders import build_red, build_second_passage, build_chess
from shapes import Point
import RPi.GPIO as GPIO
import random
import time
import os


def led_timer(end_time, duration):
    # Rescale remaining time because we only have 10 LEDs
    timeleft = end_time - time.time()
    timeleft = int(timeleft * 10 / duration)
    # Turn off LEDs according the the remaining time
    for i in range(9, timeleft, -1):
        GPIO.output(LEDs[i], GPIO.LOW)


def reset_led_timer():
    # Turn all LEDs on
    for led in LEDs:
        GPIO.output(led, GPIO.HIGH)


def enter_dungeon(mc, lvl=0):
    # Rooms in each dungeon
    if lvl == 0:
        rooms = [PUZZLE_ROOMS['Quack'], PUZZLE_ROOMS['FirstPassage'],
                 TRAP_ROOMS['Easy1'], TRAP_ROOMS['Easy2']]
        height = EASY_MAZE_HEIGHT
        width = EASY_MAZE_WIDTH
    elif lvl == 1:
        rooms = [PUZZLE_ROOMS['SecondPassage'], PUZZLE_ROOMS['Red'],
                 CHEAT_ROOMS['Medium'], TRAP_ROOMS['Medium1'],
                 TRAP_ROOMS['Medium2'], TRAP_ROOMS['Medium3']]
        height = MEDIUM_MAZE_HEIGHT
        width = MEDIUM_MAZE_WIDTH
    elif lvl == 2:
        rooms = [PUZZLE_ROOMS['Quiz'], PUZZLE_ROOMS['Chess'], PUZZLE_ROOMS['Water'],
                 CHEAT_ROOMS['Hard'], TRAP_ROOMS['Hard1'],
                 TRAP_ROOMS['Hard2'], TRAP_ROOMS['Hard3']]
        height = HARD_MAZE_HEIGHT
        width = HARD_MAZE_WIDTH

    # Choosing a random position in the dungeon to teleport the player to
    while True:
        is_valid = True
        pos_x = random.randint(STAGE_POS[lvl].x + 1, STAGE_POS[lvl].x + height - 1)
        pos_z = random.randint(STAGE_POS[lvl].z + 1, STAGE_POS[lvl].z + width - 1)
        pos_y = STAGE_POS[lvl].y
        if (mc.getBlock(pos_x, pos_y, pos_z) == 0):
            for room in rooms:
                # Checking if the space is in a room or of a wall
                if room.contains(Point(pos_z, pos_x), -STAGE_POS[lvl].x, -STAGE_POS[lvl].z):
                    is_valid = False
                    break
        else:
            is_valid = False

        if is_valid:
            tts_chat(mc, "YOU'LL NOW BE TELEPORTED TO THE DUNGEON")
            mc.player.setTilePos(pos_x, pos_y, pos_z)
            break


def reset_dungeon(mc):
    print("[INFO] Building easy level")
    build_dungeon(mc, STAGE_POS[0], difficulty='easy')

    print("[INFO] Building medium level")
    build_dungeon(mc, STAGE_POS[1], difficulty='medium')

    print("[INFO] Building hard level")
    build_dungeon(mc, STAGE_POS[2], difficulty='hard')

    print("[INFO] Building quack a mole room")
    build_quack_a_mole(mc)

    print("[INFO] Building water room")
    build_water(mc)

    print("[INFO] Building first passage")
    all_pillars = build_first_passage(mc)

    print("[INFO] Building red room")
    build_red(mc)

    print("[INFO] Building chess room")
    build_chess(mc)

    print("[INFO] Building second passage")
    build_second_passage(mc)

    return all_pillars


def game_reset(mc):
    '''
        Reset game state and rebuild the level with a different maze
    '''
    mc.player.setTilePos(PYRAMID_POS.x, PYRAMID_POS.y-3, PYRAMID_POS.z)
    tts_chat(mc, "THE PATH TO HEAVEN IS BEING BUILT UPON YOU")
    tts_chat(mc, "PLEASE WAIT")
    all_pillars = reset_dungeon(mc)
    entered_room = {
            'Quack': False,
            'FirstPassage': False,
            'SecondPassage': False,
            'Red': False,
            'Quiz': False,
            'Chess': False,
            'Water': False
            }

    completed = {
            'Quack': False,
            'FirstPassage': False,
            'SecondPassage': False,
            'Red': False,
            'Quiz': False,
            'Chess': False,
            'Water': False
            }
    # TODO: Write intro
    enter_dungeon(mc)
    return entered_room, completed, all_pillars


def tts_chat(mc, text, prefix=None, speed=None, voice=None):
    args = '-a 20'
    if speed is not None:
        args += ' -s %d' % (speed)
    if voice is not None:
        args += ' -v %s' % (voice)
    if prefix is not None:
        msg = "%s %s" % (prefix, text)
    else:
        msg = text

    mc.postToChat(msg)
    os.system('espeak %s "%s"' % (args, text))
