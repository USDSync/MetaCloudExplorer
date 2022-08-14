__all__ = ["positioner"]

from typing import List, Optional
from pxr import Gf


def postioner(
    count: List[int], distance: List[float], id_count: int = 1
):
    """
    Returns generator with pairs containing transform matrices and ids to arrange multiple objects.

    ### Arguments:

        `count: List[int]`
            Number of matrices to generage per axis

        `distance: List[float]`
            The distance between objects per axis

        `id_count: int`
            Count of differrent id

    """

    for i in range(count[0]):
        x = (i - 0.5 * (count[0] - 1)) * distance[0]

        for j in range(count[1]):
            y = (j - 0.5 * (count[1] - 1)) * distance[1]

            for k in range(count[2]):
                z = (k - 0.5 * (count[2] - 1)) * distance[2]

                # Create a matrix with position randomization
                result = Gf.Matrix4d(1)
                result.SetTranslate(Gf.Vec3d(x,y,z))

                id = int(random.random() * id_count)

                yield (result, id)
