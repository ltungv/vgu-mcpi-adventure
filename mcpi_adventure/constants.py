from mcpi.vec3 import Vec3
from shapes import Rectangle, Point


PYRAMID_HEIGHT = 45

STAGE_POS = [
        Vec3(-30, 0, -30),
        Vec3(-45, 15, -45),
        Vec3(-60, 30, -60)
    ]

N_LAYOUTS = 5

EASY_MAZE_HEIGHT = 61
EASY_MAZE_WIDTH = 61

MEDIUM_MAZE_HEIGHT = 91
MEDIUM_MAZE_WIDTH = 91

HARD_MAZE_HEIGHT = 121
HARD_MAZE_WIDTH = 121

PUZZLE_ROOMS = {
        'QuackAMole': Rectangle(
                Point(1, 1), Point(22, 22)
            ),
        'FirstPassage': Rectangle(
                Point(27, 41), Point(60, 60)
            ),
        'SecondPassage': Rectangle(
                Point(1, 1), Point(46, 16)
            ),
        'RedRoom': Rectangle(
                Point(55, 63), Point(90, 90)
            ),
        'Quiz': Rectangle(
                Point(1, 1), Point(22, 22)
            ),
        'Chess': Rectangle(
                Point(69, 69), Point(120, 120)
            ),
        'Water': Rectangle(
                Point(1, 73), Point(32, 104)
            )
        }
