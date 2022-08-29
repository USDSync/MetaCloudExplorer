__all__ = ["distributePlanes"]

from typing import List, Optional
import random

from pxr import Gf

def distributePlanes(
    UpAxis: 'Z',
    count: List[int], 
    distance: List[float], 
    sizes: List[float],
    randomization: List[float], 
    seed: Optional[int] = None,
    scaleFactor:float=1.0
):
    #print("UpAxis = " + UpAxis)
    random.seed(seed)

    if(UpAxis == 'Z'):
        nUpPlane = count[0]*count[1]
    elif(UpAxis == 'X'):
        nUpPlane = count[1]*count[2]
    else:#(UpAxis == 'Y'):
        nUpPlane = count[2]*count[0]
    for i in range(len(sizes)):
        iPlane = i % nUpPlane

        if(UpAxis == 'Z'):
            ix = iPlane // count[1]
            iy = iPlane % count[1]
            iz = i // nUpPlane
        elif(UpAxis == 'X'):
            iy = iPlane // count[2]
            iz = iPlane % count[2]
            ix = i // nUpPlane
        else:#(UpAxis == 'Y'):
            iz = iPlane // count[0]
            ix = iPlane % count[0]
            iy = i // nUpPlane

        x = ix*((distance[0]+sizes[i])*scaleFactor) * randomization[0]
        y = iy*((distance[1]+sizes[i])*scaleFactor) * randomization[1]
        z = iz*((distance[2]+sizes[i])*scaleFactor) * randomization[2]

        yield(Gf.Vec3d(x,y,z))


