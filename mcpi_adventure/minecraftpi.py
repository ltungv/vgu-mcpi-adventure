from mcpi.minecraft import Minecraft
from .helpers import remove_block
import mcpi.block as block


def main():
    mc = Minecraft.create()
    player = mc.player
    for height in range(10):
        mc.setBlock(0, height, 0, block.DIAMOND_BLOCK.id)

    remove_block(mc, 0, 0, 0)

    while True:
        pos = player.getPos()
        mc.postToChat("x=%d, y=%d, z=%d" % (pos.x, pos.y, pos.z))


if __name__ == '__main__':
    main()
