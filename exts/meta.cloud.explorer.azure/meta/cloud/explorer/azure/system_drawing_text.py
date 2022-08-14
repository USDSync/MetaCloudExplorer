import clr
clr.AddReference('System.Drawing')
clr.AddReference('System.Windows.Forms')
 
import os
import __main__

from System.Drawing import Graphics, Bitmap
from System.Drawing import Rectangle, GraphicsUnit
from System.Drawing.Imaging import ColorMatrix, ImageAttributes
from System.Windows.Forms import PictureBox, PictureBoxSizeMode


def test_indexing_value_types_cp20370(self):
        import clr
        if is_netcoreapp:
            clr.AddReference("System.Drawing.Primitives")
        else:
            clr.AddReference("System.Drawing")
        from System.Drawing import Point

        p = Point(1,2)
        l = [None]
        l[0] = p
        self.assertEqual(id(l[0]), id(p))
        self.assertEqual(id(l[0]), id(p))

        x = {}
        x[p] = p
        self.assertEqual(id(list(x.iterkeys())[0]), id(p))
        self.assertEqual(id(list(x.itervalues())[0]), id(p))

        self.load_iron_python_test()

        from IronPythonTest import StructIndexable
        a = StructIndexable()
        a[0] = 1
        self.assertEqual(a[0], 1) 