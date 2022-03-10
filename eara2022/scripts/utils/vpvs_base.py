""" 
vpvs_base.py

provide basic plotting functions for the vp, vs, vp/vs, radial anistoropy plotting.
"""
from typing import List
import pygmt
from eara2022 import resource, save_path
from eara2022.utils import get_vol_list

vols = get_vol_list()


def plot_base_map(fig: pygmt.Figure, depth: int) -> None:
    fig.plot(data=resource(
        ["Plate_Boundaries", "nuvel1_boundaries"]), pen="1.8p,green4")
    fig.plot(data=resource(
        ["China_blocks", "block2d_mod.txt"]), pen="1.8p,green4")
    fig.plot(data=resource(
        ["China_blocks", "China_Basins"]), pen="1.8p,green4")
    for slab in ['izu', 'kur', 'phi', 'ryu', 'man']:
        fig.grdcontour(
            resource(['slab2', f'{slab}_slab2_depth.grd']), interval=f"+{-depth}", pen="2.5p,magenta")
    fig.plot(x=vols[:, 1], y=vols[:, 0],
             style="kvolcano/0.4", pen="1p,magenta")
    fig.coast(shorelines="1/0.2p,black",
              borders=["1/0.1p,black"], resolution="l", area_thresh="5000")


def plot_base(depths: List[int], cpt_series: str, cpt_reverse: bool, save_name: str, colorbar_content: str) -> None:
    # * configurations
    sizes = len(depths)
    cols = 3
    if sizes % 3 == 0:
        rows = sizes//cols
    else:
        rows = sizes//cols+1

    # * figure
    fig = pygmt.Figure()
    pygmt.config(FONT_LABEL="18p", MAP_LABEL_OFFSET="18p",
                 FONT_ANNOT_PRIMARY="18p", MAP_FRAME_TYPE="plain")
    pygmt.makecpt(cmap=resource(['cpt', 'dvs_6p.cpt']),
                  series=cpt_series, continuous=True, background="o", reverse=cpt_reverse)

    fig.shift_origin(yshift="5i")
    with fig.subplot(nrows=rows, ncols=cols, figsize=(f"{rows*6}i", f"{cols*5.2}i"), sharex='b', sharey='l', margins=['0.05i', '0.02i'], frame=["WSen", "xaf", "yaf"], autolabel="(A)+o0.15i/0.2i"):
        for idx in range(sizes):
            with pygmt.config(MAP_FRAME_TYPE="plain", MAP_TICK_LENGTH="0p"):
                fig.basemap(region=[83, 155, 10, 58],
                            projection="M?", panel=idx)
            plot_base_map(fig, depths[idx])

            fig.text(position="TR", text=f"{depths[idx]} km",
                     font="24p,Helvetica,black", offset="j0.1i/0.15i")

        fig.colorbar(
            # justified inside map frame (j) at Top Center (TC)
            position="JBC+w25c/1.2c+h+o0i/2c",
            box=False,
            frame=["a1", f"x+l{colorbar_content}"],
            scale=100,
            panel=rows*cols-1-cols//2)

    fig.savefig(save_path(save_name))
