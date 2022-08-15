# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["scatterWithPlaneSize"]

from typing import List, Optional
import random
from pxr import Gf


def scatterWithPlaneSize(
    count: List[int], 
    distance: List[float], 
    sizes: List[float],
    randomization: List[float], 
    id_count: int = 1, 
    seed: Optional[int] = None,
    scaleFactor:float=1.0
):
    """
    Returns generator with pairs containing transform matrices and ids to
    arrange multiple objects.

    ### Arguments:

        `count: List[int]`
            Number of matrices to generage per axis

        `distance: List[float]`
            The distance between objects per axis

        `randomization: List[float]`
            Random distance per axis

        `id_count: int`
            Count of differrent id

        `seed: int`
            If seed is omitted or None, the current system time is used. If seed
            is an int, it is used directly.

    """
    print("Generating " + str(id_count) + " postions: " + str(count[0]) + "|" + str(count[1]) + "|" + str(count[2]))
    
    for i in range(id_count):
        if (sizes[i]>250):
            x = (i - 0.5 * (count[0] - 1)) * (distance[0]*scaleFactor) + (sizes[i]*2)
        else:
            x = (i - 0.5 * (count[0] - 1)) * (distance[0]*scaleFactor) - (sizes[i]*2)

        for j in range(count[1]):
            if (sizes[i]>250):
                y = (j - 0.5 * (count[1] - 1)) * (distance[1]*scaleFactor) + (sizes[i]*2)
            else:
                y = (j - 0.5 * (count[1] - 1)) * (distance[1]*scaleFactor) - (sizes[i]*2)

            for k in range(count[2]):
                if (sizes[i]>250):
                    z = (k - 0.5 * (count[2] - 1)) * (distance[2]*scaleFactor) + (sizes[i]*2)
                else:
                    z = (k - 0.5 * (count[2] - 1)) * (distance[2]*scaleFactor) - (sizes[i]*2)

                result = Gf.Vec3d(x,y,z)

                yield (result)
