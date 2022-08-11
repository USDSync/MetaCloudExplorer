
# Calculate the size of the Plane to place Resource Group X's items on
# using 2D spaces here, will locate all the items on a plane the size of the group
# 1x, 2x2, 3x3, 4x4, 5x5, 6x6, 7x7, 8x8, etc...  what size do we need?

import math

__all__ = ["calcPlaneSizeForGroup"]

from re import I
from typing import List

def calcPlaneSizeForGroup(resourceCount: int): 

    # 1-16 squared, return the square root, this is the size of the space needed
    for i in [1, 4, 9, 16, 25, 36, 49, 64, 81, 100, 121, 144, 169, 196, 225, 256]:
        if resourceCount > 0 and resourceCount <= i:
            return math.sqrt(i)*2

