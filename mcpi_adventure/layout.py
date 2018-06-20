from dungeon import DungeonEasy, DungeonMedium, DungeonHard
from constants import (
        EASY_MAZE_HEIGHT,
        EASY_MAZE_WIDTH,
        MEDIUM_MAZE_HEIGHT,
        MEDIUM_MAZE_WIDTH,
        HARD_MAZE_HEIGHT,
        HARD_MAZE_WIDTH,
        )


def create_dungeon_layouts(n_layouts=5, block_type=1):
    '''
        Generate layout for each levels and save to
        .csv files contained in /layout/*/*
    '''
    print("[INFO] Generating dungeon layout")
    for i in range(n_layouts):
        while True:
            try:
                print("[INFO] Creating easy dungeon")
                # Generate the layout of each level and save to .csv
                dungeon_easy = DungeonEasy(
                                   width=EASY_MAZE_WIDTH, height=EASY_MAZE_HEIGHT,
                                   extra_connector_chance=0,
                                   winding_percent=0,
                                   wall_block_type=block_type
                               )
                print("[INFO] Creating medium dungeon")
                dungeon_medium = DungeonMedium(
                                   width=MEDIUM_MAZE_WIDTH, height=MEDIUM_MAZE_HEIGHT,
                                   extra_connector_chance=0,
                                   winding_percent=0,
                                   wall_block_type=block_type
                               )
                print("[INFO] Creating hard dungeon")
                dungeon_hard = DungeonHard(
                                   width=HARD_MAZE_WIDTH, height=HARD_MAZE_HEIGHT,
                                   extra_connector_chance=0,
                                   winding_percent=0,
                                   wall_block_type=block_type
                               )

                print("[INFO] Saving all dungeon state")
                dungeon_easy.save_tiles_state(path_name='layout/easy/%d.csv' % (i))
                dungeon_medium.save_tiles_state(path_name='layout/medium/%d.csv' % (i))
                dungeon_hard.save_tiles_state(path_name='layout/hard/%d.csv' % (i))
                break
            except Exception as e:
                print(e)
                print("[ERROR] Cannot create dungeon states! Retrying...")
