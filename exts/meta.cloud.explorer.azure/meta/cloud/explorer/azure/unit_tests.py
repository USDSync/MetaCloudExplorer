import unittest
from .math_utils import calcPlaneSizeForGroup

class TestRGPlaneSizeCalc(unittest.TestCase):

    def test_lower(self):
        planeSize = calcPlaneSizeForGroup(1)
        self.assertEqual(planeSize, 1)

    def test_lower(self):
        planeSize = calcPlaneSizeForGroup(2)
        self.assertEqual(planeSize, 2)

    def test_lower(self):
        planeSize = calcPlaneSizeForGroup(3)
        self.assertEqual(planeSize, 2)

    def test_lower(self):
        planeSize = calcPlaneSizeForGroup(4)
        self.assertEqual(planeSize, 2)

    def test_lower(self):
        planeSize = calcPlaneSizeForGroup(5)
        self.assertEqual(planeSize, 3)

    def test_lower(self):
        planeSize = calcPlaneSizeForGroup(6)
        self.assertEqual(planeSize, 3)


if __name__ == '__main__':
    unittest.main()