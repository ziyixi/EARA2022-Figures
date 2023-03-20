import pygmt


def plot_place_holder(fig: pygmt.Figure) -> None:
    with pygmt.config(MAP_FRAME_PEN="0.5p,white"):
        fig.basemap(region=[110, 160, 10, 60],
                    projection="X0.04i", frame=["lbrt"])
