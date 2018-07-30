import WrightTools as wt
from WrightTools import datasets


def test_zoom():
    p = datasets.PyCMDS.w2_w1_000
    data = wt.data.from_PyCMDS(p)
    data.transform("w1", "wm")
    data.zoom(2)
    # objects = wt.artists.quick2D(data)
    # plt.close('all')


if __name__ == "__main__":
    test_zoom()
