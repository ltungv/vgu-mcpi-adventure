from mcpi.minecraft import Minecraft
from .builder import remove_block
from dungeon import Dungeon, DIRECTIONS
from time import sleep
import mcpi.block as block


def main():
    mc = Minecraft.create()
    # player = mc.player
    for height in range(50):
        mc.setBlock(0, height, 0, block.DIAMOND_BLOCK.id)
        mc.setBlock(0, height, 255, block.DIAMOND_BLOCK.id)
        mc.setBlock(255, height, 0, block.DIAMOND_BLOCK.id)
        mc.setBlock(255, height, 255, block.DIAMOND_BLOCK.id)

    my_dungeon = Dungeon(
                    width=255, height=255,
                    n_rooms_tries=300,
                    extra_connector_chance=20,
                    room_extra_size=10,
                    winding_percent=40
                )
    my_dungeon.generate()

    # for i in range(my_dungeon.height):
    #     for j in range(my_dungeon.width):
    #         mc.setBlock(i, 0, j, my_dungeon.tiles[i][j])

    # while True:
    #     sleep(1)
    #     pos = player.getPos()
    #     mc.postToChat("x=%d, y=%d, z=%d" % (pos.x, pos.y, pos.z))


if __name__ == '__main__':
    main()
