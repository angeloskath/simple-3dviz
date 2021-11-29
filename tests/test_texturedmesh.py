from os import path
import unittest
import numpy as np
from cv2 import imwrite
from simple_3dviz.renderables import TexturedMesh
from simple_3dviz import Scene, Mesh

class TestTexturedMesh(unittest.TestCase):
    def test_bed(self):
        s = Scene(size=(1024, 1024), background=(0, 0, 0, 0))
        s.add(TexturedMesh.from_file(path.join(path.dirname(__file__), "bed_model/raw_model.obj")))
        s.rotate_z(np.pi/2)
        s.camera_position = (3, 3, 3)
        for i in range(180):
            s.render()
            imwrite("/tmp/frame_{:03d}.png".format(i), s.frame)
            s.rotate_y(np.pi/90)    


if __name__ == "__main__":
    unittest.main()

