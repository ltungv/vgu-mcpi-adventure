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


from shapes import Rectangle, Point, Tiles
from mcpi.minecraft import Minecraft
import time
import numpy as np
import random
from constants import PUZZLE_ROOMS

# mc = Minecraft.create()

DIRECTIONS = [
    Point(1, 0),
    Point(-1, 0),
    Point(0, 1),
    Point(0, -1)
]


class Dungeon(object):
    def __init__(
            self, width, height,
            n_rooms_tries=100,
            room_extra_size=0,
            extra_connector_chance=20,
            winding_percent=0,
            wall_block_type=1):
        if (width % 2 == 0) and (height % 2 == 0):
            raise Exception("VALUE ERROR! Both width and height must be odd")

        self.width = width
        self.height = height

        self.rooms = []
        self.regions = Tiles(width, height, -1)
        self.tiles = Tiles(width, height, wall_block_type)
        self.wall_block_type = wall_block_type

        self.current_region = -1
        self.extra_connector_chance = extra_connector_chance
        self.winding_percent = winding_percent

        self.__n_rooms_tries = n_rooms_tries
        self.__room_extra_size = room_extra_size

        self.generate()

    def generate(self):
        print("[INFO] Adding rooms")
        self.add_rooms(overlap_offset=5)

        print("[INFO] Carving wide passage")
        for pos_y in xrange(2, self.height, 4):
            for pos_x in xrange(2, self.width, 4):
                pos = Point(pos_x, pos_y)
                if self.tiles.get_val(pos) != self.wall_block_type:
                    continue
                self.grow_maze_wide(pos)

        print("[INFO] Carving narrow passage")
        for pos_y in xrange(1, self.height, 2):
            for pos_x in xrange(1, self.width, 2):
                pos = Point(pos_x, pos_y)
                if self.tiles.get_val(pos) != self.wall_block_type:
                    continue
                self.grow_maze(pos)


        self.connect_regions()

    def save_tiles_state(self, path_name="layout/example.csv"):
        with open(path_name, "wb") as f:
            np.savetxt(f, self.tiles.get_tiles(), fmt="%-2i", delimiter=",")

    def build_room(self, pos_x=None, pos_y=None, width=None, height=None, random_size=False):
        if random_size:
            room_size = random.randint(1 + self.__room_extra_size / 2, 3 + self.__room_extra_size) * 2 + 1
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
                raise e
        else:
            room_width = width
            room_height = height
            room_x = pos_x
            room_y = pos_y

        return Rectangle(
                    Point(room_x, room_y),
                    Point(room_x + room_width, room_y + room_height)
                )

    def add_rooms(self, overlap_offset=0):
        for i in xrange(self.__n_rooms_tries):
            try:
                room = self.build_room(random_size=True)
            except Exception as e:
                print("[ERROR] Error encounter while creating a room")
                continue

            overlapped = False
            for existed_room in self.rooms:
                if room.overlaps(existed_room, off_set=overlap_offset):
                    overlapped = True
                    break
            if overlapped:
                continue

            self.rooms.append(room)
            self.start_region()
            for pos in room:
                self.carve(pos)

    def grow_maze_wide(self, pos_start):
        cells = []
        last_direction = None
        maze_init = True

        cells.append(pos_start)
        while cells:
            cell = cells[-1]
            unmade_cells = []

            for direction in DIRECTIONS:
                if (self.can_carve_wide(cell, direction)):
                    unmade_cells.append(direction.get_tuple())

            # print('[DEBUG] VAR unmade_cells length: %d' % (len(unmade_cells)))
            if unmade_cells:
                if maze_init:
                    self.start_region()
                    maze_init = False
                if ((last_direction in unmade_cells) and
                        (random.randint(0, 100) >= self.winding_percent)):
                    direction = Point(last_direction[0], last_direction[1])
                else:
                    rand_dir = random.choice(unmade_cells)
                    direction = Point(rand_dir[0], rand_dir[1])

                for scaling in range(6):
                    scale_dir = direction * scaling
                    self.carve(cell + scale_dir)
                    self.carve(cell + direction.inverse() + scale_dir)
                    self.carve(cell - direction.inverse() + scale_dir)

                cells.append(cell + direction * 4)

                last_direction = direction
            else:
                cells.pop()
                last_direction = None

    def grow_maze(self, pos_start):
        cells = []
        last_direction = None

        self.start_region()
        self.carve(pos_start)

        cells.append(pos_start)
        while cells:
            cell = cells[-1]
            unmade_cells = []

            for direction in DIRECTIONS:
                if (self.can_carve_wide(cell, direction)):
                    unmade_cells.append(direction.get_tuple())

            if unmade_cells:
                if ((last_direction in unmade_cells) and
                        (random.randint(0, 100) >= self.winding_percent)):
                    direction = Point(last_direction[0], last_direction[1])
                else:
                    rand_dir = random.choice(unmade_cells)
                    direction = Point(rand_dir[0], rand_dir[1])

                self.carve(cell + direction)
                self.carve(cell + direction * 2)

                cells.append(cell + direction * 2)

                last_direction = direction
            else:
                cells.pop()
                last_direction = None

    def connect_regions(self):
        connector_regions = [
                [None for i in xrange(self.width)]
                for j in xrange(self.height)
            ]
        connectors = []
        for pos in self.tiles.inflate(-1):
            if self.tiles.get_val(pos) != self.wall_block_type:
                continue

            regions = set()
            for direction in DIRECTIONS:
                region = self.regions.get_val(pos + direction)
                if region != -1:
                    regions.add(region)

            if len(regions) < 2:
                continue

            connector_regions[pos.x][pos.y] = regions
            connectors.append(pos)

        merged = []
        open_regions = set()
        for i in xrange(self.current_region + 1):
            merged.append(i)
            open_regions.add(i)

        open_regions = np.array(list(open_regions))
        merged = np.array(merged)

        while len(open_regions) > 1:
            connector = random.choice(connectors)

            self.add_junction(connector)

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
                            self.add_junction(connector)
                        connectors.pop(i)

    def can_carve_wide(self, pos, direction):
        if (not self.tiles.contains(pos + direction * 6) or
                not self.tiles.contains(pos + direction.inverse() + direction * 5) or
                not self.tiles.contains(pos - direction.inverse() + direction * 5)):
            return False

        for scaling in range(2, 6):
            scale_dir = direction * scaling
            if (self.tiles.get_val(pos + scale_dir) != self.wall_block_type or
                    self.tiles.get_val(pos + direction.inverse() + scale_dir) != self.wall_block_type or
                    self.tiles.get_val(pos - direction.inverse() + scale_dir) != self.wall_block_type):
                return False

        return True

    def can_carve(self, pos, direction):
        if (not self.tiles.contains(pos + direction * 3)):
            return False

        return (self.tiles.get_val(pos + direction * 2) == self.wall_block_type)

    def carve(self, pos):
        self.tiles.set_val(pos, 0)
        self.regions.set_val(pos, self.current_region)

    def add_junction(self, pos):
        self.tiles.set_val(pos, 0)

    def start_region(self):
        self.current_region += 1


class DungeonEasy(Dungeon):
    def __init__(self, width, height, **kwargs):
        super(DungeonEasy, self).__init__(width, height, **kwargs)

    def add_rooms(self, *args, **kwargs):
        print("[INFO] Creating room for easy dungeon")
        # Quack a mole
        self.rooms.append(PUZZLE_ROOMS['QuackAMole'])
        # First passage
        self.rooms.append(PUZZLE_ROOMS['FirstPassage'])
        # Trap
        room = self.build_room(45, 1, 15, 15)
        self.rooms.append(room)
        room = self.build_room(1, 35, 15, 15)
        self.rooms.append(room)

        for room in self.rooms:
            self.start_region()
            for pos in room:
                self.carve(pos)


class DungeonMedium(Dungeon):
    def __init__(self, width, height, **kwargs):
        super(DungeonMedium, self).__init__(width, height, **kwargs)

    def add_rooms(self, *args, **kwargs):
        print("[INFO] Creating room for medium dungeon")
        # Second passage
        self.rooms.append(PUZZLE_ROOMS['SecondPassage'])
        # Red room
        self.rooms.append(PUZZLE_ROOMS['RedRoom'])
        # Cheat room
        room = self.build_room(1, 73, 15, 15)
        self.rooms.append(room)

        room = self.build_room(75, 1, 15, 15)
        self.rooms.append(room)
        room = self.build_room(1, 57, 15, 15)
        self.rooms.append(room)
        room = self.build_room(55, 47, 35, 15)
        self.rooms.append(room)

        for room in self.rooms:
            self.start_region()
            for pos in room:
                self.carve(pos)


class DungeonHard(Dungeon):
    def __init__(self, width, height, **kwargs):
        super(DungeonHard, self).__init__(width, height, **kwargs)

    def add_rooms(self, overlap_offset):
        print("[INFO] Creating room for hard dungeon")
        # Quiz
        self.rooms.append(PUZZLE_ROOMS['Quiz'])
        # Chess
        self.rooms.append(PUZZLE_ROOMS['Chess'])
        # Water
        self.rooms.append(PUZZLE_ROOMS['Water'])
        # Cheat
        room = self.build_room(105, 53, 15, 15)
        self.rooms.append(room)
        # Trap
        room = self.build_room(27, 1, 15, 15)
        self.rooms.append(room)
        room = self.build_room(105, 1, 15, 15)
        self.rooms.append(room)
        room = self.build_room(1, 105, 31, 15)
        self.rooms.append(room)

        for room in self.rooms:
            self.start_region()
            for pos in room:
                self.carve(pos)
