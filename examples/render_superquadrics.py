import numpy as np

from simple_3dviz.renderables import Mesh
from simple_3dviz.behaviours.keyboard import SnapshotOnKey
from simple_3dviz.window import show

if __name__ == "__main__":
    # Number of e1, e2 parameters to be tested
    N = 7
    # SQs shapes
    e2 = np.linspace(0.1, 1.9, N, endpoint=True)
    e1 = np.linspace(0.1, 1.9, N, endpoint=True)
    epsilon_1, epsilon_2 = np.meshgrid(e1, e2)
    epsilons = np.stack([epsilon_1, epsilon_2]).reshape(2, -1).T
    # SQs sizes
    alphas = np.ones((epsilons.shape[0], 3))
    # SQs translations
    s = np.ceil(N*2.5 / 2)
    x = np.linspace(-s, s, N)
    y = np.linspace(-s, s, N)
    z = np.array([0])
    X, Y, Z = np.meshgrid(x, y, z)
    translations = np.stack([X, Y, Z]).reshape(3, -1).T
    # SQs rotations
    rotations = np.eye(3)[np.newaxis] * np.ones((len(epsilons), 1, 1))

    colors = np.array([[1., 0, 0, 1],
                        [0, 1, 1, 1]])[np.random.randint(0, 2, size=epsilons.shape[0])]

    m = Mesh.from_superquadrics(alphas, epsilons, translations, rotations, colors)
    show(m, size=(512,512), light=(0, 0, 3), behaviours=[SnapshotOnKey()])
