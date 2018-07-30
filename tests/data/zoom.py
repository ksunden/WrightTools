import WrightTools as wt
from WrightTools import datasets
import matplotlib.pyplot as plt


def test_zoom_DOVE():
    p = datasets.KENT.LDS821_DOVE
    data = wt.data.from_KENT(p, ignore=["d1", "d2", "wm"])
    data.transform("w2", "w1-w2")
    newdata = data.zoom([2, 2])
    try:
        wt.artists.quick2D(newdata)
    finally:
        return data, newdata

def test_zoom():
    p = datasets.PyCMDS.w2_w1_000
    data = wt.data.from_PyCMDS(p)
    data.transform("w1", "wm")
    newdata = data.zoom([2,1])
    wt.artists.quick2D(newdata)        
    return data, newdata

if __name__ == "__main__":
    plt.close('all')
    old, new = test_zoom()
    # old, new = test_zoom_DOVE()
