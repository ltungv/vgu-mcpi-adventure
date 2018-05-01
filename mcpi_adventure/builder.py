import mcpi.block as block


def remove_block(mc, posX, posY, posZ):
    mc.setBlock(posX, posY, posZ, block.AIR.id)
