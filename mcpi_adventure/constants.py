'''
Constants storing game data
'''
from mcpi.vec3 import Vec3
from shapes import Rectangle, Point


PYRAMID_HEIGHT = 45
PYRAMID_POS = Vec3(0, 0, 0)

# Upperleft corner position of each level
STAGE_POS = [
        Vec3(-30, PYRAMID_POS.y + 0, -30),
        Vec3(-45, PYRAMID_POS.y + 15, -45),
        Vec3(-60, PYRAMID_POS.y + 30, -60)
    ]

# Number of layouts generated using create_dungeon_layouts()
N_LAYOUTS = 5

# Heights and widths of each level
EASY_MAZE_HEIGHT = 61
EASY_MAZE_WIDTH = 61

MEDIUM_MAZE_HEIGHT = 91
MEDIUM_MAZE_WIDTH = 91

HARD_MAZE_HEIGHT = 121
HARD_MAZE_WIDTH = 121

# Puzzle rooms postions
PUZZLE_ROOMS = {
        'Quack': Rectangle(
                Point(1, 1), Point(22, 22)
            ),
        'FirstPassage': Rectangle(
                Point(27, 41), Point(60, 60)
            ),
        'SecondPassage': Rectangle(
                Point(1, 1), Point(46, 16)
            ),
        'Red': Rectangle(
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

# Trap rooms postions
TRAP_ROOMS = {
        'Easy1': Rectangle(
                Point(45, 1), Point(60, 16)
            ),
        'Easy2': Rectangle(
                Point(1, 35), Point(16, 50)
            ),
        'Medium1': Rectangle(
                Point(75, 1), Point(90, 16)
            ),
        'Medium2': Rectangle(
                Point(1, 57), Point(16, 72)
            ),
        'Medium3': Rectangle(
                Point(55, 47), Point(70, 62)
            ),
        'Hard1': Rectangle(
                Point(27, 1), Point(42, 16)
            ),
        'Hard2': Rectangle(
                Point(105, 1), Point(120, 16)
            ),
        'Hard3': Rectangle(
                Point(1, 105), Point(16, 120)
            )
        }

# Cheat rooms positons
CHEAT_ROOMS = {
        'Medium': Rectangle(
                Point(1, 73), Point(16, 88)
            ),
        'Hard': Rectangle(
                Point(105, 53), Point(120, 68)
            ),
        }
