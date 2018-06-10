from constants import PUZZLE_ROOMS
from shapes import Point
from mcpi import block
import math
import random
import time


def play_quackamole(mc, player):
    current_room = PUZZLE_ROOMS['QuackAMole']
    score = 0
    is_done = True
    stage_posx = int(current_room.left + (current_room.width - 10) / 2)
    stage_posy = int(current_room.top + (current_room.height - 10) / 2)

    while True:
        block_hits = mc.events.pollBlockHits()
        player_pos = player.getTilePos()
        player_pos_2d = Point(player_pos.x, player_pos.z)
        if not current_room.contains(player_pos_2d):
            return 2  # Return 2 when player leave the room when the mission is not finished
        if is_done:
            tnt_posx = random.randint(stage_posx, stage_posx + 10)
            tnt_posy = random.randint(stage_posy, stage_posy + 10)
            distance_from_player = int(math.sqrt(
                                        (player_pos_2d.x - tnt_posx) ** 2 +
                                        (player_pos_2d.y - tnt_posy) ** 2
                                    ))
            mc.setBlock(tnt_posx, current_room.y + 1, tnt_posy)
            tnt_set_time = time.time()
            tnt_setoff_time = tnt_set_time + distance_from_player - 4
            tnt_explode_time = tnt_set_time + distance_from_player
            is_done = False
            tnt_exploding = False
        else:
            current_time = time.time()
            for hit in block_hits:
                if (hit.pos.x == tnt_posx
                        and hit.pos.y == current_room.y + 1
                        and hit.pos.z == tnt_posy):
                    score += 1
                    is_done = True
                    mc.setBlock(tnt_posx, current_room.y + 1, tnt_posy, block.AIR.id)

            if (current_time >= tnt_setoff_time
                    and not tnt_exploding):
                mc.setBlock(tnt_posx, current_room.y + 1, tnt_posy, 1)
                tnt_exploding = True
            if (current_time >= tnt_explode_time):
                return 1

        if score == 10:
            return 0
