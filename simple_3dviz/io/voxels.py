
import numpy as np

from ._utils import get_file, close_file


def read_binvox(filename):
    try:
        f = get_file(filename, "rb")

        # Read and validate the version line
        l = f.readline()
        assert l == b"#binvox 1\n"

        # Read the size of the voxel grid
        l = f.readline()
        assert l.startswith(b"dim")
        W, H, D = [int(d) for d in l.split()[1:]]

        # Read the translation vector
        l = f.readline()
        assert l.startswith(b"translate")
        translation = np.array([float(x) for x in l.split()[1:]])

        # Read the scaling factor
        l = f.readline()
        assert l.startswith(b"scale")
        scale = float(l.split()[1])

        # Make sure that the last line is 'data'
        assert f.readline().strip() == b"data"

        data = np.fromfile(f, dtype=np.uint8)
        values, counts = data[::2], data[1::2]
        voxelgrid = np.repeat(values.astype(np.bool), counts)
        voxelgrid = voxelgrid.reshape(W, H, D).transpose(0, 2, 1)

        return voxelgrid, translation, scale

    finally:
        close_file(filename, f)
