""" 
slab.py

Plot the slab vertical cross-secations.
"""
import pygmt
import numpy as np
from eara2022.utils.plot import plot_place_holder
from eara2022 import save_path

conf = {
    "x_offset": 7.7,
    "y_offset": 5.7,
    "yabs_offset": 3,
    "ytopo_offset": 4,
}


def generate_offset() -> dict[str, np.ndarray]:
    # generate the offset array
    res = {
        "x": np.zeros((3, 3), dtype='<U10'),
        "y": np.zeros((3, 3), dtype='<U10'),
        "yabs": np.zeros((3, 3), dtype='<U10'),
        "ytopo": np.zeros((3, 3), dtype='<U10')
    }
    for row in range(3):
        for col in range(3):
            res['x'][row][col] = f"f{col*conf['x_offset']}i"
            res['y'][row][col] = f"f{(2-row)*conf['y_offset']}i"
            res['yabs'][row][col] = f"f{(2-row)*conf['y_offset']+conf['yabs_offset']}i"
            res['ytopo'][row][col] = f"f{(2-row)*conf['y_offset']+conf['ytopo_offset']}i"
    return res


def plot_per(fig: pygmt.Figure, offset: dict[str, np.ndarray], row: int, col: int) -> None:
    fig.shift_origin(xshift=offset['x'][row]
                     [col], yshift=offset['y'][row][col])
    with pygmt.config(MAP_FRAME_TYPE="plain", MAP_TICK_LENGTH="0p"):
        fig.basemap(projection=f"X7.5i/-2.7i",
                    region=f"0/25/0/1000", frame=["wsen", "xaf", "yaf"])

    with pygmt.config(MAP_FRAME_TYPE="inside", MAP_TICK_LENGTH_PRIMARY="10p"):
        fig.basemap(projection=f"X7.5i/-2.7i",
                    region=f"0/25/0/1000", frame=["wsen", "xaf", "yaf"])


def plot_abs(fig: pygmt.Figure, offset: dict[str, np.ndarray], row: int, col: int) -> None:
    fig.shift_origin(xshift=offset['x'][row]
                     [col], yshift=offset['yabs'][row][col])
    with pygmt.config(MAP_FRAME_TYPE="plain", MAP_TICK_LENGTH="0p"):
        fig.basemap(projection=f"X7.5i/-0.7i",
                    region=f"0/25/0/100", frame=["wsen", "xaf", "yaf"])

    with pygmt.config(MAP_FRAME_TYPE="inside", MAP_TICK_LENGTH_PRIMARY="10p"):
        fig.basemap(projection=f"X7.5i/-0.7i",
                    region=f"0/25/0/100", frame=["wsen", "xaf", "yaf"])


def plot_topo(fig: pygmt.Figure, offset: dict[str, np.ndarray], row: int, col: int) -> None:
    fig.shift_origin(xshift=offset['x'][row]
                     [col], yshift=offset['ytopo'][row][col])
    with pygmt.config(MAP_FRAME_TYPE="plain", MAP_TICK_LENGTH="0p"):
        fig.basemap(projection=f"X7.5i/1i",
                    region=f"0/25/-8000/4000", frame=["lsrn", 'ya2500f', 'xaf'])


def main() -> None:
    fig = pygmt.Figure()
    pygmt.config(FONT_LABEL="15p", MAP_LABEL_OFFSET="12p",
                 FONT_ANNOT_PRIMARY="12p", MAP_FRAME_TYPE="plain")
    plot_place_holder(fig)
    offset = generate_offset()

    # * plot figures
    for idx in range(8):
        row, col = divmod(idx, 3)
        # * perturbation
        plot_per(fig, offset, row, col)
        # * abs
        plot_abs(fig, offset, row, col)
        # * topo
        plot_topo(fig, offset, row, col)

    fig.savefig(save_path("slab.pdf"))


if __name__ == "__main__":
    main()
