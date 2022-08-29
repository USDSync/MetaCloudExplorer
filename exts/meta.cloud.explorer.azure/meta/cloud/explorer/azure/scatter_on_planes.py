# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["scatterOnFixedPlane"]

from typing import List, Optional
import random

from pxr import Gf


def scatterOnFixedPlane(
    count: List[int], 
    distance: List[float], 
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


    """
    vectors = {}
    id_cnt = 0

    for i in range(count[0]):
        x = (i - 0.5 * (count[0] - 1)) * distance[0]*scaleFactor

        for j in range(count[1]):
            y = (j - 0.5 * (count[1] - 1)) * distance[1]*scaleFactor

            for k in range(count[2]):
                z = (k - 0.5 * (count[2] - 1)) * distance[2]*scaleFactor

                #yield([x, y, z])
                vec_id = id_cnt
                vec = {vec_id: Gf.Vec3f(x,y,z)}
                vectors.update(vec)
                id_cnt = id_cnt +1

    return vectors                

