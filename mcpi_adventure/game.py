from mcpi.minecraft import Minecraft
from .helpers import remove_block
import mcpi.block as block


def main():
    mc = Minecraft.create()
    player = mc.player
    for height in range(50):
        mc.setBlock(0, height, 0, block.DIAMOND_BLOCK.id)
        mc.setBlock(0, height, 255, block.DIAMOND_BLOCK.id)
        mc.setBlock(255, height, 0, block.DIAMOND_BLOCK.id)
        mc.setBlock(255, height, 255, block.DIAMOND_BLOCK.id)

    whil True:
        pos = player.getPos()
        mc.postToChat("x=%d, y=%d, z=%d" % (pos.x, pos.y, pos.z))


if __name__ == '__main__':
    main()
