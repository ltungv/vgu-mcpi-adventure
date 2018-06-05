from mcpi.minecraft import Minecraft
from mcpi.vec3 import Vec3
from mcpi import block
from helpers import build_inversed_pyramid
from helpers import build_dungeon
from layout import create_dungeon_layouts


PYRAMID_HEIGHT = 45
STAGE_HEIGHTS = [0, 15, 30]


def main():
    mc = Minecraft.create()

    # World Initialization
    print("[INFO] GENERATING WORLD! PLEASE WAIT")
    # mc.setting('world_immutable', True)
    mc.setBlocks(-256, 0, -256, 256, 101, 256, block.AIR.id)

    # Build pyramid
    print("[INFO] BUIDLING PYRAMID")
    build_inversed_pyramid(
                    mc, pos_start=Vec3(0, 0, 0),
                    height=PYRAMID_HEIGHT, size_offset=30,
                    block_type=block.GLOWSTONE_BLOCK.id
                )

    print("[INFO] ADDING FLOORS")
    mc.setBlocks(-30 + 1, STAGE_HEIGHTS[0] - 1, -30 + 1, 30 - 1, STAGE_HEIGHTS[0] - 1, 30 - 1, block.GLOWSTONE_BLOCK.id)
    mc.setBlocks(-45 + 1, STAGE_HEIGHTS[1] - 1, -45 + 1, 45 - 1, STAGE_HEIGHTS[1] - 1, 45 - 1, block.GLOWSTONE_BLOCK.id)
    mc.setBlocks(-60 + 1, STAGE_HEIGHTS[2] - 1, -60 + 1, 60 - 1, STAGE_HEIGHTS[2] - 1, 60 - 1, block.GLOWSTONE_BLOCK.id)

    # Generating dungeon state to a .csv file
    create_dungeon_layouts(block_type=block.SANDSTONE.id)

    print("[INFO] Building easy dungeon")
    # build_dungeon(mc, Vec3(-30, STAGE_HEIGHTS[0], -30), path='layout/easy')

    print("[INFO] Building medium dungeon")
    # build_dungeon(mc, Vec3(-45, STAGE_HEIGHTS[1], -45), path='layout/medium')

    # print("[INFO] Building hard dungeon")
    # build_dungeon(mc, Vec3(-60, STAGE_HEIGHTS[2], -60), path='layout/hard')

    print("[INFO] FINISHED GENERATING WORLD")


if __name__ == '__main__':
    main()
