from constants import PUZZLE_ROOMS, STAGE_POS
from shapes import Point, Rectangle
from mcpi import block
from minecraftstuff import MinecraftDrawing, Points
from helpers import tts_chat
from helpers import led_timer, reset_led_timer
import math
import random
import time


def play_quackamole(mc, player):
    current_room = PUZZLE_ROOMS['Quack']
    is_done = True
    score = 0
    # The platform on which the player plays
    stage_posx = int(current_room.left + (current_room.width - 10) / 2) + STAGE_POS[0].x
    stage_posy = int(current_room.top + (current_room.height - 10) / 2) + STAGE_POS[0].z
    stage = Rectangle(Point(stage_posx, stage_posy), Point(stage_posx+10, stage_posy+10))
    start = False

    while True:
        # Player positon and hit events data
        block_hits = mc.events.pollBlockHits()
        player_pos = player.getTilePos()
        player_pos_2d = Point(player_pos.x, player_pos.z)
        # Return 2 when player leave the room when the mission is not finished
        if not current_room.contains(player_pos_2d, -STAGE_POS[0].x, -STAGE_POS[0].z):
            return 2
        if not start:
            # Start puzzle when the play is on the platform
            if stage.contains(player_pos_2d):
                start = True
                tts_chat(mc, "Game starts")
        else:
            # Checking if the player has hitted the tnt
            if is_done:
                # Radom tnt's position
                tnt_posx = random.randint(stage_posx, stage_posx + 10)
                tnt_posy = STAGE_POS[0].y + 1
                tnt_posz = random.randint(stage_posy, stage_posy + 10)
                # Calculate the distance of the tnt to the player
                # to set the time of explostion of the tnt
                distance_from_player = int(math.sqrt(
                                            (player_pos_2d.x - tnt_posx) ** 2 +
                                            (player_pos_2d.y - tnt_posy) ** 2
                                        ))
                mc.setBlock(tnt_posx, tnt_posy, tnt_posz, block.TNT.id)
                tnt_set_time = time.time()
                duration = distance_from_player / 6
                tnt_explode_time = tnt_set_time + duration
                # Turn on all LEDs
                reset_led_timer()
                is_done = False
            else:
                # Turn off LEDs based on remaning time
                led_timer(tnt_explode_time, duration)
                current_time = time.time()
                # Check hitted block position
                for hit in block_hits:
                    if (hit.pos.x == tnt_posx
                            and hit.pos.y == tnt_posy
                            and hit.pos.z == tnt_posz):
                        score += 1
                        mc.postToChat("%d / 10 TO WIN" % (score))
                        is_done = True
                        mc.setBlock(tnt_posx, tnt_posy, tnt_posz, block.AIR.id)

                if (current_time >= tnt_explode_time):
                    # Immitate the behaviour of an exploded tnt
                    mc.setBlocks(tnt_posx-2, tnt_posy-1, tnt_posz-2,
                                 tnt_posx+2, tnt_posy+2, tnt_posz+2,
                                 block.AIR.id)
                    return 1
        # Return 0 if win
        if score == 10:
            return 0


def play_water(mc, player):
    '''
        The water room puzzle mechanics
    '''
    def random_sphere_point(x0, y0, z0, radius):
        '''
            Returns a random point of a sphere, evenly distributed over the sphere.
            The sphere is centered at (x0,y0,z0) with the passed in radius.
            The returned point is returned as a three element array [x,y,z].
        '''
        u = random.random()
        v = random.random()
        theta = 2 * math.pi * u
        phi = math.acos(2 * v - 1)
        x = x0 + (radius * math.sin(phi) * math.cos(theta))
        y = y0 + (radius * math.sin(phi) * math.sin(theta))
        z = z0 + (radius * math.cos(phi))
        return x, y, z

    # Helpers object for drawing object and shapes
    mcdraw = MinecraftDrawing(mc)
    # Puzzle's parameters
    score = 0
    current_room = PUZZLE_ROOMS['Water']
    water_height = 10
    start = False
    is_done = True
    is_diving = False

    while True:
        # Player's position
        player_pos = player.getTilePos()
        player_pos_2d = Point(player_pos.x, player_pos.z)
        # Return 2 when player leave the room when the mission is not finished
        if not current_room.contains(player_pos_2d, -STAGE_POS[2].x, -STAGE_POS[2].z):
            return 2
        if not start:
            # Start the puzzle when the player swim to the surface
            if player_pos.y >= STAGE_POS[2].y+water_height-1:
                start = True
                tts_chat(mc, "You have to swim through a loop of glow stones", prefix="[RULES]")
                tts_chat(mc, "You gain 1 point when successfully swim through it", prefix="[RULES]")
                tts_chat(mc, "If you're underwater for more than 10s, you'll die", prefix="[RULES]")
                tts_chat(mc, "Each time you come out of the water, the water's level raise", prefix="[RULES]")
                tts_chat(mc, "Game will start in 5 seconds")
                time.sleep(5)
                tts_chat(mc, "Game start")
        else:
            # Check if the player is under water
            if player_pos.y < STAGE_POS[2].y + water_height:
                # When the player is underwater, start the 10-second timer
                if not is_diving:
                    expired_time = time.time() + 10
                    is_diving = True
                # When player score 1 point, place new loop
                if is_done:
                    # Generate random position for the loop
                    while True:
                        x_target, y_target, z_target = random_sphere_point(player_pos.x, player_pos.y, player_pos.z, 5)
                        x_target = int(math.floor(x_target))
                        y_target = int(math.floor(y_target))
                        z_target = int(math.floor(z_target))
                        if (current_room.inflate(-2).contains(Point(x_target, z_target), -STAGE_POS[2].x, -STAGE_POS[2].z) and
                                (y_target > STAGE_POS[2].y + 1) and (y_target < STAGE_POS[2].y + water_height - 1)):
                            break
                    # Vertices of the rectangular loop
                    face_vertices = Points()
                    face_vertices.add(x_target-2, y_target, z_target-2)
                    face_vertices.add(x_target+2, y_target, z_target-2)
                    face_vertices.add(x_target+2, y_target, z_target+2)
                    face_vertices.add(x_target-2, y_target, z_target+2)
                    # Draw to loop
                    mcdraw.drawFace(face_vertices, False, block.GLOWSTONE_BLOCK.id)
                    # Turn on all LEDs
                    reset_led_timer()
                    is_done = False
                else:
                    # If the player passes the loop
                    led_timer(expired_time, 10)
                    if ((player_pos.x >= x_target-2) and (player_pos.x <= x_target+2) and
                            (player_pos.z >= z_target-2) and (player_pos.z <= z_target+2) and
                            (player_pos.y == y_target-2)):
                        mcdraw.drawFace(face_vertices, False, block.AIR.id)
                        is_done = True
                        score += 1
                        mc.postToChat("%d / 12 TO WIN" % (score))
                # Check if the player has been under water for more than 10 seconds
                # if so, the player fails the puzzle
                if time.time() >= expired_time:
                    mcdraw.drawFace(face_vertices, False, block.AIR.id)
                    return 1
            elif is_diving:
                # Raise the water level when the player raise to the surface
                is_diving = False
                water_height += 1
                mc.setBlocks(current_room.left + STAGE_POS[2].x,
                             STAGE_POS[2].y + water_height,
                             current_room.top + STAGE_POS[2].z,
                             current_room.right + STAGE_POS[2].x - 1,
                             STAGE_POS[2].y + water_height,
                             current_room.bottom + STAGE_POS[2].z - 1,
                             block.WATER.id)
        if score == 12:
            # Drain all the water when the player win
            # for dramatic movie effects
            for i in range(14, -1, -1):
                mc.setBlocks(current_room.left + STAGE_POS[2].x,
                             STAGE_POS[2].y + i,
                             current_room.top + STAGE_POS[2].z,
                             current_room.right + STAGE_POS[2].x - 1,
                             STAGE_POS[2].y + i,
                             current_room.bottom + STAGE_POS[2].z - 1,
                             block.AIR.id)
                time.sleep(0.5)
            return 0


def play_first_passage(mc, player, all_pillars):
    '''
        "First Passage" puzzle mechanics
    '''
    def count_glowstones():
        '''
            Counting the number of glowstones placed
            on top of the pillars
        '''
        count = 0
        for pillar in all_pillars:
            block_at_pillar = mc.getBlock(pillar.x, pillar.y+6, pillar.z)
            if block_at_pillar == block.GLOWSTONE_BLOCK.id:
                count += 1
        return count

    # Game's parameters
    current_room = PUZZLE_ROOMS['FirstPassage']
    door_pos = player.getTilePos()
    start = False
    is_raise = False
    lava_height = 3
    prev_glowstones = 0

    while True:
        # Player's positions
        player_pos = player.getTilePos()
        player_pos_2d = Point(player_pos.x, player_pos.z)
        # Return 2 when player leave the room when the mission is not finished
        if not current_room.contains(player_pos_2d, -STAGE_POS[0].x, -STAGE_POS[0].z):
            return 2
        if not start:
            # Teleport the player to a random pillar and start the puzzle
            start = True
            tts_chat(mc, "Do not leave the room before finishing the game", prefix="[RULES]")
            tts_chat(mc, "You will have to place glowstones on top of all the pillars", prefix="[RULES]")
            tts_chat(mc, "The lava will raise every 20 seconds", prefix="[RULES]")
            tts_chat(mc, "If you touch the lava, you'll lose", prefix="[RULES]")
            tts_chat(mc, "You'll be teleported to the room in 5 seconds")
            time.sleep(5)
            init_pos = random.choice(all_pillars)
            player.setTilePos(init_pos.x, init_pos.y + 6, init_pos.z)
        else:
            # Check if the lava level has been raise
            # Add a 20-second timer if it has just been raised
            if not is_raise:
                reset_led_timer()
                time_to_raise = time.time() + 20
                is_raise = True
            led_timer(time_to_raise, 20)
            # Raise the level every 20 seconds
            if time.time() >= time_to_raise:
                lava_height += 1
                is_raise = False
                mc.setBlocks(current_room.inflate(-4).left + STAGE_POS[0].x,
                             STAGE_POS[0].y + lava_height,
                             current_room.inflate(-4).top + STAGE_POS[0].z,
                             current_room.inflate(-4).right + STAGE_POS[0].x,
                             STAGE_POS[0].y + lava_height,
                             current_room.inflate(-4).bottom + STAGE_POS[0].z,
                             block.LAVA.id)
            # Return 1 when the player fall into the lava
            if player_pos.y <= STAGE_POS[0].y+lava_height:
                return 1
            # Current number of placed glowstones
            current_glowstones = count_glowstones()
            if current_glowstones > prev_glowstones:
                prev_glowstones = current_glowstones
                mc.postToChat("%d / 7 REDSTONES" % current_glowstones)
            # Return 0 if 7 glowstones have been placed
            if current_glowstones == 7:
                player.setTilePos(door_pos.x, door_pos.y, door_pos.z)
                return 0


def play_red(mc):
    current_room = PUZZLE_ROOMS['Red']
    width = 26
    height = 13
    depth = 34

    x = current_room.left + STAGE_POS[1].x-3
    z = current_room.top + STAGE_POS[1].z
    y = STAGE_POS[1].y

    start = False
    door_pos = mc.player.getTilePos()

    mc.player.setTilePos(x+int(depth/2), y, z+int(width/2))

    while True:
        player_pos = mc.player.getTilePos()
        player_pos_2d = Point(player_pos.x, player_pos.z)
        # Return 2 when player leave the room when the mission is not finished
        if not current_room.contains(player_pos_2d, -STAGE_POS[1].x, -STAGE_POS[1].z):
            return 2
        if not start:
            tts_chat(mc, "Do not leave the room before finishing the game", prefix="[RULES]")
            tts_chat(mc, "Delete for word reds to win", prefix="[RULES]")
            start = True
        else:
            check_RED = mc.getBlock(x+3+depth-1, y+3, z+width-15)
            if check_RED == 0:
                tts_chat(mc, "You win, continue to your mission")
                mc.player.setTilePos(door_pos.x, door_pos.y, door_pos.z)
                return 0
            else:
                tts_chat(mc, "Nearly get it!")


def play_second_passage(mc):
    current_room = PUZZLE_ROOMS['SecondPassage']

    x = current_room.left + STAGE_POS[1].x-3
    z = current_room.top + STAGE_POS[1].z
    y = STAGE_POS[1].y
    width = 14
    height = 13
    depth = 44

    door_pos = mc.player.getTilePos()
    mc.player.setTilePos(x+4, y+height-2, z+4)
    start = False

    while True:
        player_pos = mc.player.getTilePos()
        player_pos_2d = Point(player_pos.x, player_pos.z)
        # Return 2 when player leave the room when the mission is not finished
        if not current_room.contains(player_pos_2d, -STAGE_POS[1].x, -STAGE_POS[1].z):
            return 2
        if not start:
            tts_chat("Try to get to the other side of the room", prefix="[RULES]")
            tts_chat("Do not fall into the lava", prefix="[RULES]")
            start = True
        if player_pos.y in range(y+height-6, y+1, -1) and play_pos.x != x+width:
            return 1
        if player_pos.x == x+width:
            tts_chat("You win")
            mc.player.setTilePos(door_pos.x, door_pos.y, door_pos.z)
            return 0

    # while True:
    #     if not start:
    #         mc.postToChat("Try to find the door and escape")
    #         mc.postToChat("Use your blocks")
    #         start = True
    #     elif current_position.y in range(y+height, y+height-6, -1) and current_position.x != x+width:
    #         mc.postToChat("Keep calm and love this game <3")
    #         time.sleep(3)
    #         mc.postToChat("You are nearly out!!")
    #     elif current_position.y in range(y+height-6, y+1, -1) and current_position.x != x+width:
    #         mc.postToChat("You lost")
    #         time.sleep(1)
    #     if current_position.x == x+width:
    #         mc.postToChat("You win")
    #         # mc.player.setTilePos()


def trap_box(mc, current_room, current_stage):
    tts_chat(mc, "You will be crushed")
    tts_chat(mc, "There's no running! accept your fate!")
    for i in range(1, 14):
        filled_room = current_room.inflate(-i)
        mc.setBlocks(filled_room.left+current_stage.x, current_stage.y, filled_room.top+current_stage.z,
                     filled_room.right+current_stage.x, current_stage.y+13, filled_room.top+current_stage.z,
                     block.SANDSTONE.id)
        mc.setBlocks(filled_room.left+current_stage.x, current_stage.y, filled_room.bottom+current_stage.z,
                     filled_room.right+current_stage.x, current_stage.y+13, filled_room.bottom+current_stage.z,
                     block.SANDSTONE.id)
        mc.setBlocks(filled_room.left+current_stage.x, current_stage.y, filled_room.top+current_stage.z,
                     filled_room.left+current_stage.x, current_stage.y+13, filled_room.bottom+current_stage.z,
                     block.SANDSTONE.id)
        mc.setBlocks(filled_room.right+current_stage.x, current_stage.y, filled_room.top+current_stage.z,
                     filled_room.right+current_stage.x, current_stage.y+13, filled_room.bottom+current_stage.z,
                     block.SANDSTONE.id)
        time.sleep(0.2)
