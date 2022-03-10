""" 
vpvs_base.py

provide basic plotting functions for the vp, vs, vp/vs, radial anistoropy plotting.
"""
from typing import List

import numpy as np
import pygmt
import xarray as xr
from eara2022 import resource, save_path
from eara2022.utils import get_vol_list

vols = get_vol_list()
MODEL_SHAPE = [421, 281, 201]


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


def prepare_model(data: xr.Dataset, nzcc_mask: np.ndarray, model_type: str) -> xr.DataArray:
    to_interp_data = data[model_type]
    for ilon in range(MODEL_SHAPE[0]):
        for ilat in range(MODEL_SHAPE[1]):
            if(nzcc_mask[ilon, ilat] == True):
                to_interp_data.data[ilon, ilat, :] = np.nan
    return to_interp_data


def prepare_cross_section(to_interp_data: xr.DataArray, depth: int) -> xr.DataArray:
    hlat = np.linspace(10, 58, 201)
    hlat = xr.DataArray(hlat, dims='hlat', coords={'hlat': hlat})
    hlon = np.linspace(83, 155, 301)
    hlon = xr.DataArray(hlon, dims='hlon', coords={'hlon': hlon})

    plot_data = to_interp_data.interp(
        depth=depth, latitude=hlat, longitude=hlon)
    plot_data = plot_data.T
    return plot_data


def plot_base(model_type: str, depths: List[int], cpt_series: str, cpt_reverse: bool, save_name: str, colorbar_content: str) -> None:
    # * configurations
    sizes = len(depths)
    cols = 3
    if sizes % 3 == 0:
        rows = sizes//cols
    else:
        rows = sizes//cols+1

    # * load ndarray
    data: xr.Dataset = xr.open_dataset(
        resource(['model_files', 'eara2021_per_ref.nc'], normal_path=True))
    nzcc_mask: np.ndarray = np.load(
        resource(['model_files', 'mask_psf_100km_050.npy'], normal_path=True))
    to_interp_data = prepare_model(data, nzcc_mask, model_type)

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
            fig.grdimage(prepare_cross_section(to_interp_data, depths[idx]))
            plot_base_map(fig, depths[idx])

            fig.text(position="TR", text=f"{depths[idx]} km",
                     font="24p,Helvetica,black", offset="j0.1i/0.15i")
            with pygmt.config(MAP_FRAME_TYPE="inside", MAP_TICK_LENGTH_PRIMARY="10p"):
                fig.basemap(region=[83, 155, 10, 58],
                            projection="M?", frame=["wsen", "xaf", "yaf"], panel=idx)

        fig.colorbar(
            # justified inside map frame (j) at Top Center (TC)
            position="JBC+w25c/1.2c+h+o0i/2c",
            box=False,
            frame=["a1", f"x+l{colorbar_content}"],
            scale=100,
            panel=rows*cols-1-cols//2)

    fig.savefig(save_path(save_name))
