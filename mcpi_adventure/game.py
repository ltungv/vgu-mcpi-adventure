from constants import PUZZLE_ROOMS, STAGE_POS
from shapes import Point, Rectangle
from mcpi import block
from minecraftstuff import MinecraftDrawing, Points
from helpers import tts_chat
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
                tts_chat(mc, "GAME STARTS")
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
                tnt_explode_time = tnt_set_time + distance_from_player / 8
                is_done = False
            else:
                current_time = time.time()
                # Check hitted block position
                for hit in block_hits:
                    if (hit.pos.x == tnt_posx
                            and hit.pos.y == tnt_posy
                            and hit.pos.z == tnt_posz):
                        score += 1
                        tts_chat(mc, "%d / 10 TO WIN" % (score))
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
                tts_chat(mc, "YOU HAVE TO SWIM THROUGH A LOOP OF GLOW STONES", prefix="[RULES]")
                time.sleep(3)
                tts_chat(mc, "YOU GAIN 1 POINT WHEN SUCCESSFULLY SWIM THROUGH IT", prefix="[RULES]")
                time.sleep(3)
                tts_chat(mc, "IF YOU'RE UNDERWATER FOR MORE THAN 10S, YOU'LL DIE", prefix="[RULES]")
                time.sleep(3)
                tts_chat(mc, "EACH TIME YOU COME OUT OF THE WATER, THE WATER'S LEvel raise", prefix="[RULES]")
                time.sleep(3)
                tts_chat(mc, "GAME WILL START IN 5 SECONDS")
                time.sleep(5)
                tts_chat(mc, "GAME START")
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
                    is_done = False
                else:
                    # If the player passes the loop
                    if ((player_pos.x >= x_target-2) and (player_pos.x <= x_target+2) and
                            (player_pos.z >= z_target-2) and (player_pos.z <= z_target+2) and
                            (player_pos.y == y_target-2)):
                        mcdraw.drawFace(face_vertices, False, block.AIR.id)
                        is_done = True
                        score += 1
                        tts_chat(mc, "%d / 12 TO WIN" % (score))
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
            tts_chat(mc, "YOU WILL HAVE TO PLACE GLOWSTONES ON TOP OF ALL THE PILLARS", prefix="[RULES]")
            time.sleep(3)
            tts_chat(mc, "THE LAVA WILL RAISE EVERY 20 SECONDS", prefix="[RULES]")
            time.sleep(3)
            tts_chat(mc, "IF YOU TOUCH THE LAVA, YOU'LL LOSE", prefix="[RULES]")
            time.sleep(3)
            tts_chat(mc, "YOU'LL BE TELEPORTED TO THE ROOM IN 5 SECONDS")
            time.sleep(5)
            init_pos = random.choice(all_pillars)
            player.setTilePos(init_pos.x, init_pos.y + 6, init_pos.z)
        else:
            # Check if the lava level has been raise
            # Add a 20-second timer if it has just been raised
            if not is_raise:
                time_to_raise = time.time() + 20
                is_raise = True
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
                tts_chat(mc, "%d / 7 REDSTONES" % current_glowstones)
            # Return 0 if 7 glowstones have been placed
            if current_glowstones == 7:
                player.setTilePos(door_pos.x, door_pos.y, door_pos.z)
                return 0


def trap_box(mc, current_room, current_stage):
    tts_chat(mc, "YOU WILL BE CRUSHED")
    tts_chat(mc, "THERE'S NO RUNNING! ACCEPT YOUR FATE!")
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
