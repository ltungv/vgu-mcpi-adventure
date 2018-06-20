from constants import EASY_MAZE_WIDTH, EASY_MAZE_HEIGHT
from constants import MEDIUM_MAZE_WIDTH, MEDIUM_MAZE_HEIGHT
from constants import HARD_MAZE_WIDTH, HARD_MAZE_HEIGHT
from constants import TRAP_ROOMS, CHEAT_ROOMS, PUZZLE_ROOMS
from constants import STAGE_POS, PYRAMID_POS
from builders import build_dungeon, build_quack_a_mole, build_water, build_first_passage
import random
import time
import os


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
        pos_x = random.randint(STAGE_POS[lvl].x + 1, STAGE_POS[lvl].x + height)
        pos_z = random.randint(STAGE_POS[lvl].x + 1, STAGE_POS[lvl].x + width)
        pos_y = STAGE_POS[lvl].y
        if (mc.getBlock(pos_x, pos_y, pos_z) == 0):
            for room in rooms:
                # Checking if the space is in a room or of a wall
                if room.contains(Point(pos_x, pos_z), -STAGE_POS[lvl].x, -STAGE_POS[lvl].y):
                    is_valid = False
                    break
        else:
            is_valid = False

        if is_valid:
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
    return build_first_passage(mc)


def game_reset(mc):
    '''
        Reset game state and rebuild the level with a different maze
    '''
    mc.player.setTilePos(PYRAMID_POS.x, PYRAMID_POS.y-3, PYRAMID_POS.z)
    tts_chat(mc, "THE PATH TO HEAVEN IS BEING BUILT UPON YOU")
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
    time.sleep(10)
    # TODO: Write intro
    enter_dungeon(mc)
    return entered_room, completed, all_pillars


def tts_chat(mc, text, prefix=None, speed=None, voice=None):
    args = ''
    if speed is not None:
        args += '-s %d' % (speed)
    if voice is not None:
        args += '-v %s' % (voice)
    if prefix is not None:
        msg = "%s %s" % (prefix, text)
    else:
        msg = text

    mc.postToChat(msg)
    os.system('espeak %s "%s"' % (args, text))
