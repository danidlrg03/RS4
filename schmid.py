import numpy as np
from matplotlib import pyplot as plt


schmid_curve = [
    [180, -50 ],
    [  0,   0 ],
    [ 70,  70 ],
    [140,   0 ],
    [210,   0 ],
    [210,  70 ],
    [280,  70 ],
    [360, -10 ],
    [280, -90 ],
    [140, -90 ],
    [120, -110],
    [140, -130],
    [160, -110],
    [140,  -90],
    [ 70,  -90],
    [  0, -130],
    [ 70, -170],
    [140, -170],
    [140, -160],
    [150, -160],
    [150, -170],
    [160, -170],
    [160, -160],
    [170, -160],
    [170, -170],
    [260, -170],
    [360,  -70],
    [260, -170]    
]

def main():
    data = np.array( schmid_curve )
    x, y = data.T
    scaleFactor=2.0
    plt.scatter(x*scaleFactor,y*scaleFactor)
    plt.plot(x*scaleFactor,y*scaleFactor)
    plt.show()


if __name__ == "__main__":
    main()
