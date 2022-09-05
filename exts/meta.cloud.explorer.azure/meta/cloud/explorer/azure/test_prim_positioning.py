import unittest
from math_func import calcPlaneSizeForGroup

#This Unit test, tests the calcPlaneSizeForGroup math function
class TestPrimPositioning(unittest.TestCase):


    def test_1(self):
        planeSize = calcPlaneSizeForGroup(1, 1)
        print("1 " + str(planeSize))
        self.assertEqual(planeSize, 100)


if __name__ == '__main__':
    unittest.main()