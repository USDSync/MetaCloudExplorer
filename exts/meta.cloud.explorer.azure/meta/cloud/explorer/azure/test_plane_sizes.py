import unittest
from math_func import calcPlaneSizeForGroup

#This Unit test, tests the calcPlaneSizeForGroup math function
class TestPlaneSizes(unittest.TestCase):


    def test_1(self):
        planeSize = calcPlaneSizeForGroup(1, 1)
        print("1 " + str(planeSize))
        self.assertEqual(planeSize, 100)

    def test_2_4(self):
        for x in range(2, 4):            
            planeSize = calcPlaneSizeForGroup(1,x)
            print(str(x) + " " + str(planeSize))
            self.assertEqual(planeSize, 200)

    def test_5_9(self):
        for x in range(5, 9):            
            planeSize = calcPlaneSizeForGroup(1,x)
            print(str(x) + " " + str(planeSize))
            self.assertEqual(planeSize, 300)

    def test_10_16(self):
        for x in range(10, 16):            
            planeSize = calcPlaneSizeForGroup(1,x)
            print(str(x) + " " + str(planeSize))
            self.assertEqual(planeSize, 400)

    def test_17_25(self):
        for x in range(17, 25):            
            planeSize = calcPlaneSizeForGroup(1,x)
            print(str(x) + " " + str(planeSize))
            self.assertEqual(planeSize, 500)

    def test_26_36(self):
        for x in range(26, 36):            
            planeSize = calcPlaneSizeForGroup(1,x)
            print(str(x) + " " + str(planeSize))
            self.assertEqual(planeSize, 600)

    def test_37_49(self):
        for x in range(37, 49):            
            planeSize = calcPlaneSizeForGroup(1,x)
            print(str(x) + " " + str(planeSize))
            self.assertEqual(planeSize, 700)

    def test_50_64(self):
        for x in range(50, 64):            
            planeSize = calcPlaneSizeForGroup(1,x)
            print(str(x) + " " + str(planeSize))
            self.assertEqual(planeSize, 800)

    def test_65_81(self):
        for x in range(65, 81):            
            planeSize = calcPlaneSizeForGroup(1,x)
            print(str(x) + " " + str(planeSize))
            self.assertEqual(planeSize, 900)

    def test_82_100(self):
        for x in range(82, 100):            
            planeSize = calcPlaneSizeForGroup(1,x)
            print(str(x) + " " + str(planeSize))
            self.assertEqual(planeSize, 1000)

    def test_102_122(self):
        for x in range(101, 121):            
            planeSize = calcPlaneSizeForGroup(1,x)
            print(str(x) + " " + str(planeSize))
            self.assertEqual(planeSize, 1100)

if __name__ == '__main__':
    unittest.main()