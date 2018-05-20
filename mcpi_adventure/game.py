from mcpi.minecraft import Minecraft
from mcpi import block
from .dungeon import Dungeon


MAZE_HEIGHT = 127
MAZE_WIDTH = 127


def main():
    global mc
    mc = Minecraft.create()

    # mc.setting('world_immutable', True)
    mc.setBlocks(-128, 0, -128, 128, 4, 128, block.AIR.id)
    is_created = False

    while (True):
        if is_created:
            break
        try:
            mc.setBlocks(-128, 0, -128, -128 + MAZE_WIDTH, 0, -128 + MAZE_HEIGHT, block.GLOWSTONE_BLOCK.id)
            my_dungeon = Dungeon(
                            width=MAZE_WIDTH, height=MAZE_HEIGHT,
                            n_rooms_tries=300,
                            extra_connector_chance=75,
                            room_extra_size=15,
                            winding_percent=0
                        )
            is_created = True
        except:
            print("Failed to create maze! Re-creating")

    for pos in my_dungeon.tiles:
        mc.setBlock(pos.x - 128, 0, pos.y - 128, my_dungeon.tiles.get_val(pos))
        mc.setBlock(pos.x - 128, 1, pos.y - 128, my_dungeon.tiles.get_val(pos))
        # mc.setBlock(pos.x - 128, 2, pos.y - 128, my_dungeon.tiles.get_val(pos))
        # mc.setBlock(pos.x - 128, 3, pos.y - 128, block.GLOWSTONE_BLOCK.id)


if __name__ == '__main__':
    main()
