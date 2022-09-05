
# Calculate the size of the Plane to place Resource Group X's items on
# using 2D spaces here, will locate all the items on a plane the size of the group
# 1x, 2x2, 3x3, 4x4, 5x5, 6x6, 7x7, 8x8, etc...  what size do we need?

import math
from pxr import Gf

__all__ = ["calcPlaneSizeForGroup"]

from re import I
from typing import List
from .scatter_on_planes import scatterOnFixedPlane

# Calculate the size of the Group Plane to create
def calcPlaneSizeForGroup(scaleFactor:float, resourceCount: int): 

    # 1-30 squared, return the square root, this is the size of the space needed
    for i in [1, 4, 9, 16, 25, 36, 49, 64, 81, 100, 121, 144, 169, 196, 225, 256, 289, 324, 361, 400, 441, 484,529,576,625,676,729, 784, 841,900]:
        if resourceCount > 0 and resourceCount <= i:
            return float(((math.sqrt(i)*100)*scaleFactor))


#FIGURES OUT WHERE TO PUT THE PRIMS ON A VARIABLE SIZED-PLANE
def calculateGroupTransforms(self, scale:float, count:int ):

    #ex 400.0 -> 800 - 400 plane is 800x800
    plane_size = (calcPlaneSizeForGroup(scaleFactor=scale, resourceCount=count)*2)
    plane_class = ((plane_size/100)/2) 
    
    #distance of objects depending on grid size..  
    dist = plane_size / plane_class

    #Use NVIDIAs Scatter algo to position on varying sized planes
    transforms = scatterOnFixedPlane(
        count=[int(plane_class), int(plane_class), 1], # Distribute accross the plane class
        distance=[dist,dist,dist],
        scaleFactor=scale
    )

    #there should be at least one transform
    if len(transforms) == 0:
        vec_id = 0
        vec = {vec_id: Gf.Vec3f(0,0,0)}
        transforms[0] = vec

    return transforms 
