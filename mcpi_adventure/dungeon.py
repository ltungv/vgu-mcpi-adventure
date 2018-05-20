'''
This is the python implementation of the procedural dungeon generator written by Bob Nystrom
Which can be found here:
    https://github.com/munificent/hauberk/blob/db360d9efa714efb6d937c31953ef849c7394a39/lib/src/content/dungeon.dart


Steps taken:
    1. Randomly placed rooms of random sizes.
    Room is discarded when it overlaps an existing room.
    2. Fill the remaining spaces with mazes.
    These mazes will not connect any room.
    3. Remove tiles that is adjacent to 2 unconnected regions,
    untill all the regions are connected. There's a chance that there
    are 2 "door" that connect 2 regions.'
    4. Remove dead ends by filling in any tile that is closed on 3 sides.
'''


from .shapes import Rectangle, Point, Tiles
from mcpi.minecraft import Minecraft
import time
import numpy as np
import random

mc = Minecraft.create()

DIRECTIONS = [
    Point(1, 0),
    Point(-1, 0),
    Point(0, 1),
    Point(0, -1)
]


class Dungeon:
    def __init__(
            self, width, height, n_rooms_tries,
            start_x=0, start_y=0,
            extra_connector_chance=20,
            room_extra_size=0,
            winding_percent=0):
        if (width % 2 == 0) and (height % 2 == 0):
            raise Exception("VALUE ERROR! Both width and height must be odd")

        self.width = width
        self.height = height

        self.n_rooms_tries = n_rooms_tries

        self.extra_connector_chance = extra_connector_chance
        self.room_extra_size = room_extra_size
        self.winding_percent = winding_percent

        self.tiles = Tiles(width, height, 1)

        self.__rooms = []
        self.__regions = Tiles(width, height, -1)
        self.__current_region = -1

        self.__generate()

    def __generate(self):
        print("Adding rooms")
        self.__add_rooms(overlap_offset=5)

        print("Carving wide passage")
        for pos_y in xrange(2, self.height, 4):
            for pos_x in xrange(2, self.width, 4):
                pos = Point(pos_x, pos_y)
                if self.tiles.get_val(pos) != 1:
                    continue
                self.__grow_maze_wide(pos)

        print("Carving narrow passage")
        for pos_y in xrange(1, self.height, 2):
            for pos_x in xrange(1, self.width, 2):
                pos = Point(pos_x, pos_y)
                if self.tiles.get_val(pos) != 1:
                    continue
                self.__grow_maze(pos)

        with open("regions.csv", "wb") as f:
            np.savetxt(f, self.__regions.get_tiles(), fmt="%-2i", delimiter=",")

        self.__connect_regions()
        # self.__remove_dead_ends()

    def __add_rooms(self, overlap_offset=0):
        for i in xrange(self.n_rooms_tries):
            room_size = random.randint(1 + self.room_extra_size / 2, 3 + self.room_extra_size) * 2 + 1
            rectangularity = random.randint(0, 1 + int(room_size / 2)) * 2
            room_width = room_size
            room_height = room_size
            if (random.randint(0, 1) < 1):
                room_width += rectangularity
            else:
                room_height += rectangularity

            try:
                room_x = random.randint(0, (self.width - room_width - 1) / 2) * 2 + 1
                room_y = random.randint(0, (self.height - room_height - 1) / 2) * 2 + 1
            except Exception as e:
                print(e)
                continue

            room = Rectangle(
                    Point(room_x, room_y),
                    Point(room_x + room_width, room_y + room_height))

            overlapped = False
            for existed_room in self.__rooms:
                if room.overlaps(existed_room, off_set=overlap_offset):
                    overlapped = True
                    break
            if overlapped:
                continue

            self.__rooms.append(room)
            self.__start_region()
            for pos in room:
                self.__carve(pos)

    def __grow_maze_wide(self, pos_start):
        cells = []
        last_direction = None
        maze_init = True

        cells.append(pos_start)
        while cells:
            cell = cells[-1]
            unmade_cells = []

            for direction in DIRECTIONS:
                if (self.__can_carve_wide(cell, direction)):
                    unmade_cells.append(direction.get_tuple())

            if unmade_cells:
                if maze_init:
                    self.__start_region()
                    maze_init = False
                if ((last_direction in unmade_cells) and
                        (random.randint(0, 100) >= self.winding_percent)):
                    direction = Point(last_direction[0], last_direction[1])
                else:
                    rand_dir = random.choice(unmade_cells)
                    direction = Point(rand_dir[0], rand_dir[1])

                for i in xrange(6):
                    direction_offset = direction * i
                    self.__carve(cell + direction_offset)
                    self.__carve(cell - direction.inverse() + direction_offset)
                    self.__carve(cell + direction.inverse() + direction_offset)

                cells.append(cell + direction*4)

                last_direction = direction
            else:
                cells.pop()
                last_direction = None

    def __grow_maze(self, pos_start):
        cells = []
        last_direction = None

        self.__start_region()
        self.__carve(pos_start)

        cells.append(pos_start)
        while cells:
            cell = cells[-1]
            unmade_cells = []

            for direction in DIRECTIONS:
                if (self.__can_carve_wide(cell, direction)):
                    unmade_cells.append(direction.get_tuple())

            if unmade_cells:
                if ((last_direction in unmade_cells) and
                        (random.randint(0, 100) >= self.winding_percent)):
                    direction = Point(last_direction[0], last_direction[1])
                else:
                    rand_dir = random.choice(unmade_cells)
                    direction = Point(rand_dir[0], rand_dir[1])

                self.__carve(cell + direction)
                self.__carve(cell + direction * 2)

                cells.append(cell + direction * 2)

                last_direction = direction
            else:
                cells.pop()
                last_direction = None

    def __connect_regions(self):
        connector_regions = [
                [None for i in xrange(self.width)]
                for j in xrange(self.height)
            ]
        connectors = []
        for pos in self.tiles.inflate(-1):
            if self.tiles.get_val(pos) != 1:
                continue

            regions = set()
            for direction in DIRECTIONS:
                region = self.__regions.get_val(pos + direction)
                if region != -1:
                    regions.add(region)

            if len(regions) < 2:
                continue

            connector_regions[pos.x][pos.y] = regions
            connectors.append(pos)

        merged = []
        open_regions = set()
        for i in xrange(self.__current_region + 1):
            merged.append(i)
            open_regions.add(i)

        open_regions = np.array(list(open_regions))
        merged = np.array(merged)

        while len(open_regions) > 1:
            print(len(open_regions), len(connectors))
            connector = random.choice(connectors)

            self.__add_junction(connector)

            regions = list(set([
                    merged[region] for region in connector_regions[connector.x][connector.y]
                ]))
            dest = regions[0]
            sources = regions[1:]

            np.place(merged, np.in1d(merged, sources), dest)

            open_regions = np.delete(
                            open_regions,
                            np.where(np.in1d(open_regions, sources))
                        )

            for i, pos in enumerate(connectors):
                if (connector.distance_to(pos) < 2):
                    connectors.pop(i)
                else:
                    regions = set([
                            merged[region] for region in
                            connector_regions[pos.x][pos.y]
                        ])
                    if (len(regions) <= 1):
                        if (random.randint(0, 100) <= self.extra_connector_chance):
                            self.__add_junction(connector)
                        connectors.pop(i)

    def __remove_dead_ends(self):
        done = False

        while not done:
            done = True
            for pos in self.tiles.inflate(-1):
                if self.tiles.get_val(pos) == 1:
                    continue

                exits = 0
                for direction in DIRECTIONS:
                    if self.tiles.get_val(pos + direction) != 1:
                        exits += 1

                if exits != 1:
                    continue

                done = False
                self.tiles.set_val(pos, 1)

    def __can_carve_wide(self, pos, direction):
        if (not self.tiles.contains(pos + direction * 6) or
                not self.tiles.contains(pos + direction.inverse() + direction * 6) or
                not self.tiles.contains(pos - direction.inverse() + direction * 6)):
            return False

        return (self.tiles.get_val(pos + direction * 5) == 1 and
                self.tiles.get_val(pos + direction.inverse() + direction * 5) == 1 and
                self.tiles.get_val(pos - direction.inverse() + direction * 5) == 1 and
                self.tiles.get_val(pos + direction * 2) == 1 and
                self.tiles.get_val(pos + direction.inverse() + direction * 2) == 1 and
                self.tiles.get_val(pos - direction.inverse() + direction * 2) == 1)

    def __can_carve(self, pos, direction):
        if (not self.tiles.contains(pos + direction * 3)):
            return False

        return (self.tiles.get_val(pos + direction * 2) == 1)

    def __carve(self, pos):
        self.tiles.set_val(pos, 0)
        self.__regions.set_val(pos, self.__current_region)

    def __add_junction(self, pos):
        self.tiles.set_val(pos, 0)

    def __start_region(self):
        self.__current_region += 1
