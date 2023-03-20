""" 
hist.py

compare the misfit distribution between m00 and m20
"""
from os.path import join
from typing import List

import numpy as np
import pygmt
from eara2022 import resource, save_path

phases = ["z", "r", "t", "surface_z", "surface_r", "surface_t"]
categories = {
    "dt": "@~D@~T(s)",
    "nzcc": "NZCC",
    "cc": "CC"
}


def load_data(dirname: str) -> dict[str, dict[str, np.ndarray]]:
    # * given dirname, load misfit information
    # cols: 2,0,1 dt,nzcc,cc
    res = {}
    for phase in phases:
        ds = np.loadtxt(join(dirname, f"{phase}.txt"))
        res[phase] = {}
        res[phase]['dt'] = ds[:, 2]
        res[phase]['nzcc'] = ds[:, 0]
        res[phase]['cc'] = ds[:, 1]
    return res


# * plotting configurations
ylabels = ["Ver. Body Wave", "Rad. Body Wave", "Tan. Body Wave",
           "Ver. Surface Wave", "Rad. Surface Wave", "Tan. Surface Wave"]
conf: dict[str, dict[str, List[float]]] = {
    'dt': {
        'xa': [5]*6,
        'xf': [1]*6,
        'xmin': [-10]*6,
        'xmax': [10]*6,
        'ya': [25000, 25000, 20000, 5000, 2500, 5000],
        'yf': [5000, 5000, 5000, 1000, 500, 1000],
        'ymin': [0]*6,
        'ymax': [93750, 81250, 43750, 13125, 10000, 12500],
        'bar_width': [0.5]*6
    },
    'nzcc': {
        'xa': [0.2]*6,
        'xf': [0.05]*6,
        'xmin': [0]*6,
        'xmax': [1]*6,
        'ya': [20000, 20000, 10000, 10000, 5000, 10000],
        'yf': [5000, 5000, 2000, 2000, 1000, 2000],
        'ymin': [0]*6,
        'ymax': [75000, 75000, 37500, 37500, 25000, 35000],
        'bar_width': [0.05]*6
    },
    'cc': {
        'xa': [0.1]*6,
        'xf': [0.025]*6,
        'xmin': [0.5]*6,
        'xmax': [1]*6,
        'ya': [10000, 10000, 5000, 5000, 5000, 5000],
        'yf': [2000, 2000, 1000, 1000, 1000, 1000],
        'ymin': [0]*6,
        'ymax': [50000, 50000, 23750, 31250, 18750, 26250],
        'bar_width': [0.025]*6
    }
}


def main() -> None:
    fig = pygmt.Figure()
    pygmt.config(FONT_LABEL="15p", MAP_LABEL_OFFSET="10p",
                 FONT_ANNOT_PRIMARY="13p")

    old_data = load_data(
        resource(['misfit', 'iter1_high_misfit'], normal_path=True))
    new_data = load_data(
        resource(['misfit', 's20_high_misfit'], normal_path=True))

    with fig.subplot(nrows=6, ncols=3, figsize=("14.4i", "17.8i"), sharex='b', margins=['0.2i', '0.06i'], frame=["WSen"], autolabel="(a)"):
        for iphase, phase in enumerate(phases):
            for icategory, category in enumerate(categories):
                frame = [f"xa{conf[category]['xa'][iphase]}f{conf[category]['xf'][iphase]}+l{categories[category]}",
                         f"ya{conf[category]['ya'][iphase]}f{conf[category]['yf'][iphase]}"]
                region = [conf[category]['xmin'][iphase], conf[category]['xmax'][iphase],
                          conf[category]['ymin'][iphase], conf[category]['ymax'][iphase]]
                if icategory != 0:
                    fig.basemap(projection="X?", frame=frame,
                                region=region, panel=[iphase, icategory])
                else:
                    frame[1] += f'+l"{ylabels[iphase]}"'
                    fig.basemap(projection="X?", frame=frame,
                                region=region, panel=[iphase, icategory])
                # plot histogram
                fig.histogram(data=old_data[phase][category], series=conf[category]
                              ['bar_width'][iphase], pen="2p,black", stairs=True, projection="X?/?")
                fig.histogram(data=new_data[phase][category], series=conf[category]
                              ['bar_width'][iphase], pen="2p,red1", stairs=True, projection="X?/?")
                # dt distribution statistics
                if icategory == 0:
                    fig.text(position="TR", text=f"@~D@~T = {np.nanmean(new_data[phase][category]):.2f} \\261 {np.nanstd(new_data[phase][category]):.2f}",
                             font="12p,Helvetica-Bold,red1", offset="j0.05i/0.15i")
                    fig.text(position="TR", text=f"@~D@~T = {np.nanmean(old_data[phase][category]):.2f} \\261 {np.nanstd(old_data[phase][category]):.2f}",
                             font="12p,Helvetica-Bold,black", offset="j0.05i/0.30i")

    save_path(fig, "hist")


if __name__ == "__main__":
    main()
