""" 
misfit.py:

Plot the misfit reduction during the inversion.
"""
from string import ascii_lowercase
from typing import List

import numpy as np
import pygmt
from eara2022 import resource, save_path
from numpy.typing import NDArray

# * load misfit dataset
misfit_high: dict[str, NDArray] = np.load(
    resource(['misfit', 'misfit_high_tosave.npy'], normal_path=True), allow_pickle=True).all()
misfit_low: dict[str, NDArray] = np.load(
    resource(['misfit', 'misfit_low_tosave.npy'], normal_path=True), allow_pickle=True).all()


def plot_left_table(fig: pygmt.Figure, projection: str) -> None:
    # * plot the inside lines and texts for the left table
    fig.plot(x=[0, 1], y=[0.25, 0.25], pen="0.5p,black", projection=projection)
    fig.plot(x=[0, 1], y=[0.5, 0.5], pen="0.5p,black", projection=projection)
    fig.plot(x=[0, 1], y=[0.75, 0.75], pen="0.5p,black", projection=projection)
    fig.plot(x=[0.3, 0.3], y=[0.25, 1],
             pen="0.5p,black", projection=projection)
    fig.plot(x=[0.65, 0.65], y=[0.25, 1],
             pen="0.5p,black", projection=projection)
    fig.text(x=0.15, y=0.875, text="Measurements No.",
             font="8p,Helvetica-Bold,black", projection=projection)
    fig.text(x=0.475, y=0.875, text="Body Waves",
             font="12p,Helvetica-Bold,black", projection=projection)
    fig.text(x=0.825, y=0.875, text="Surface Waves",
             font="12p,Helvetica-Bold,black", projection=projection)
    fig.text(x=0.475, y=0.625, text="623120",
             font="12p,Helvetica-Bold,black", projection=projection)
    fig.text(x=0.825, y=0.625, text="130639",
             font="12p,Helvetica-Bold,black", projection=projection)
    fig.text(x=0.475, y=0.375, text="639173",
             font="12p,Helvetica-Bold,black", projection=projection)
    fig.text(x=0.825, y=0.375, text="148334",
             font="12p,Helvetica-Bold,black", projection=projection)
    fig.text(x=0.1, y=0.625, text="Stage 1",
             font="12p,Helvetica-Bold,black", projection=projection)
    fig.plot(x=0.22, y=0.625, style="a0.1i",
             color="red", projection=projection)
    fig.text(x=0.1, y=0.375, text="Stage 2",
             font="12p,Helvetica-Bold,black", projection=projection)
    fig.plot(x=0.22, y=0.375, style="d0.1i",
             color="blue", projection=projection)
    fig.text(x=0.5, y=0.125, text="Measured at the last iteration of each stage",
             font="12p,Helvetica-Bold,black", projection=projection)


def plot_right_table(fig: pygmt.Figure, projection: str) -> None:
    fig.plot(x=[0, 1], y=[0.25, 0.25], pen="0.5p,black", projection=projection)
    fig.plot(x=[0, 1], y=[0.5, 0.5], pen="0.5p,black", projection=projection)
    fig.plot(x=[0, 1], y=[0.75, 0.75], pen="0.5p,black", projection=projection)
    fig.plot(x=[0.3, 0.3], y=[0.25, 1],
             pen="0.5p,black", projection=projection)
    fig.plot(x=[0.65, 0.65], y=[0.25, 1],
             pen="0.5p,black", projection=projection)
    fig.text(x=0.15, y=0.875, text="Period Range",
             font="10p,Helvetica-Bold,black", projection=projection)
    fig.text(x=0.475, y=0.875, text="Body Waves",
             font="12p,Helvetica-Bold,black", projection=projection)
    fig.text(x=0.825, y=0.875, text="Surface Waves",
             font="12p,Helvetica-Bold,black", projection=projection)
    fig.text(x=0.475, y=0.625, text="10 - 40 s",
             font="12p,Helvetica-Bold,black", projection=projection)
    fig.text(x=0.825, y=0.625, text="40 - 120 s",
             font="12p,Helvetica-Bold,black", projection=projection)
    fig.text(x=0.475, y=0.375, text="8 - 40 s",
             font="12p,Helvetica-Bold,black", projection=projection)
    fig.text(x=0.825, y=0.375, text="30 - 120 s",
             font="12p,Helvetica-Bold,black", projection=projection)
    fig.text(x=0.1, y=0.625, text="Stage 1",
             font="12p,Helvetica-Bold,black", projection=projection)
    fig.plot(x=0.22, y=0.625, style="a0.1i",
             color="red", projection=projection)
    fig.text(x=0.1, y=0.375, text="Stage 2",
             font="12p,Helvetica-Bold,black", projection=projection)
    fig.plot(x=0.22, y=0.375, style="d0.1i",
             color="blue", projection=projection)
    fig.text(x=0.4, y=0.125, text="Starting Misfit at Each Stage:",
             font="12p,Helvetica-Bold,black", projection=projection)
    fig.plot(x=0.80, y=0.125, style="a0.1i", projection=projection)
    fig.plot(x=0.87, y=0.125, style="d0.1i", projection=projection)


def handle_misfit_npy(category: str) -> dict[str, dict[str, NDArray]]:
    # * handle the misfit npy and convert to x and y array
    # ! in the future, try to use better way to handle it
    res = {
        'source1': {
            'x': np.array([0]),
            'y': np.array(misfit_low[category][0:1])
        },
        'stage1': {
            'x': np.arange(0, 11),
            'y': np.hstack([misfit_low[category+"s"][0], misfit_low[category][1:11]])
        },
        'source2': {
            'x': np.array([10]),
            'y': np.array(misfit_high[category][10:11])
        },
        'stage2': {
            'x': np.arange(10, 21),
            'y': np.hstack([misfit_high[category+"s"][1], misfit_high[category][11:21]])
        }
    }
    return res


def plot_misfit(fig: pygmt.Figure, panel: int, category: str, yrange: List[float], ylabel: str, phase: str) -> None:
    # * plot each panel
    data = handle_misfit_npy(category=category)
    fig.basemap(region=[-1, 21]+list(yrange),
                frame=["xaf", "yaf"], projection="X?", panel=panel)

    fig.plot(x=data['source1']['x'], y=1-data['source1']['y'], style="a0.1i")
    fig.plot(x=data['stage1']['x'], y=1-data['stage1']
             ['y'], style="a0.1i", color="red")
    fig.plot(x=data['source2']['x'], y=1-data['source2']['y'],  style="d0.1i")
    fig.plot(x=data['stage2']['x'], y=1-data['stage2']
             ['y'], style="d0.1i", color="blue")

    fig.text(position="TR", text=ylabel,
             font="12p,Helvetica-Bold,black", offset="j0.1i/0.15i")
    fig.text(position="TR", text=phase,
             font="12p,Helvetica-Bold,black", offset="j0.1i/0.32i")
    fig.text(position="BL", text=f"({ascii_lowercase[panel-2 if panel>=3 else 0]})",
             font="15p,Helvetica-Bold,black", offset="j0.2c/0.2c")
    if panel == 1:
        fig.text(x=data['source1']['x'], y=1-data['source1']['y'], text="before 1st",
                 font="10p,Helvetica-Bold,black", angle=0, justify="TL", offset="j0.3i/0.1i")
        fig.text(x=data['source1']['x'], y=1-data['source1']['y']-0.007, text="source inversion",
                 font="10p,Helvetica-Bold,black", angle=0, justify="TL", offset="j0.3i/0.1i")
        fig.text(x=data['stage1']['x'][:1], y=1-data['stage1']['y'][:1]+0.007, text="kernel smoother:",
                 font="10p,Helvetica-Bold,black", angle=0, justify="BL", offset="j0.3i/0.1i")
        fig.text(x=data['stage1']['x'][:1], y=1-data['stage1']['y'][:1], text="h: 50km, v: 25km",
                 font="10p,Helvetica-Bold,black", angle=0, justify="BL", offset="j0.3i/0.1i")
        fig.text(x=data['stage1']['x'][5:6], y=1-data['stage1']['y'][5:6], text="kernel smoother:",
                 font="10p,Helvetica-Bold,black", angle=0, justify="TR", offset="j0i/0.3i")
        fig.text(x=data['stage1']['x'][5:6], y=1-data['stage1']['y'][5:6]-0.007, text="h: 25km, v: 10km",
                 font="10p,Helvetica-Bold,black", angle=0, justify="TR", offset="j0i/0.3i")
        fig.text(x=data['source2']['x'], y=1-data['source2']['y']+0.007, text="before 2nd",
                 font="10p,Helvetica-Bold,black", angle=0, justify="BL", offset="j0.3i/0.1i")
        fig.text(x=data['source2']['x'], y=1-data['source2']['y'], text="source inversion",
                 font="10p,Helvetica-Bold,black", angle=0, justify="BL", offset="j0.3i/0.1i")

        style = "v0.1i+s+e+a40+ggreen4+h0+p1p,green4"
        offsets = [0.3, 0.0015, 1.4, 0.006]
        fig.plot(x=data['source1']['x']+offsets[2], y=1-data['source1']['y']-offsets[3], style=style,
                 pen="0.04i,green4", direction=[data['source1']['x']+offsets[0], 1-data['source1']['y']-offsets[1]])
        fig.plot(x=data['stage1']['x'][:1]+offsets[2], y=1-data['stage1']['y'][:1]+offsets[3], style=style,
                 pen="0.04i,green4", direction=[data['stage1']['x'][:1]+offsets[0], 1-data['stage1']['y'][:1]+offsets[1]])
        fig.plot(x=data['stage1']['x'][5:6]-offsets[2], y=1-data['stage1']['y'][5:6]-offsets[3]*2, style=style,
                 pen="0.04i,green4", direction=[data['stage1']['x'][5:6]-offsets[0], 1-data['stage1']['y'][5:6]-offsets[1]])
        fig.plot(x=data['source2']['x']+offsets[2], y=1-data['source2']['y']+offsets[3], style=style,
                 pen="0.04i,green4", direction=[data['source2']['x']+offsets[0], 1-data['source2']['y']+offsets[1]])


def main():
    # * init
    fig = pygmt.Figure()
    pygmt.config(FONT_LABEL="16p", MAP_LABEL_OFFSET="8p",
                 FONT_ANNOT_PRIMARY="16p")

    with fig.subplot(nrows=3, ncols=3, figsize=("14.4i", "9i"), sharex='b', margins=['0.2i', '0.06i'], frame=["WSen", 'xaf+l"Iteration No."', "yaf"]):
        # * left table
        fig.basemap(region=[0, 1, 0, 1],
                    frame=['lbrt'], projection="X4.2i/2i", panel=0)
        plot_left_table(fig, projection="X4.2i/2i")

        # * right table
        fig.basemap(region=[0, 1, 0, 1],
                    frame=['lbrt'], projection="X4.2i/2i", panel=2)
        plot_right_table(fig, projection="X4.2i/2i")

        # * misfits
        categories = ["all", "z", "r", "t",
                      "surface_z", "surface_r", "surface_t"]
        yranges = [(0.13, 0.26), (0.15, 0.35), (0.15, 0.35),
                   (0.2, 0.45), (0.07, 0.14), (0.09, 0.16), (0.07, 0.13)]
        ylabels = ["", "Ver. Body Wave", "Rad. Body Wave", "Tan. Body Wave",
                   "Ver. Surface Wave", "Rad. Surface Wave", "Tan. Surface Wave"]
        phases = ["", "p, s, P, S, sP, sS, PP, SS", "p, s, P, S, sP, sS, PP, SS",
                  "s, S, sS, SS, ScS", "Rayleigh Wave", "Rayleigh Wave", "Love Wave"]
        panels = [1, 3, 4, 5, 6, 7, 8]
        for category, yrange, panel, ylabel, phase in zip(categories, yranges, panels, ylabels, phases):
            plot_misfit(fig, panel, category, yrange, ylabel, phase)
        # y labels
        for panel in [3, 6]:
            fig.basemap(region=[-1, 21]+list(yranges[panel-2]),
                        frame=['Wbrt', 'yaf+lMisfit'], panel=panel)

    save_path(fig, "misfit")


if __name__ == "__main__":
    main()
