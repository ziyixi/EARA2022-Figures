"""
vpvs_base.py

provide basic plotting functions for the vp, vs, vp/vs, radial anistoropy plotting.
"""
from json import load
from string import ascii_lowercase
from typing import List

import numpy as np
import pygmt
import xarray as xr
from eara2022 import resource, save_path
from eara2022.utils import get_vol_list
from scipy import interpolate
from scipy.ndimage import gaussian_filter

# * settings
np.seterr(divide='ignore')
np.seterr(invalid='ignore')

# * several paths for the models, some may unused
eara2021_abs_path = resource(['model_files', 'eara2021.nc'], normal_path=True)
eara2021_per_path = resource(
    ['model_files', 'eara2021_per_ref.nc'], normal_path=True)
stw105_path = resource(['model_files', 'stw105.txt'], normal_path=True)
ak135_path = resource(['model_files', 'AK135F_AVG.csv'], normal_path=True)

# * load models with the respect to certain reference model
copy_model: xr.DataArray = xr.open_dataset(eara2021_per_path)["vs"]

vols = get_vol_list()
MODEL_SHAPE = [421, 281, 201]


def load_stw105(parameter: str) -> xr.DataArray:
    stw105 = np.loadtxt(stw105_path)
    r = stw105[:, 0]
    if parameter == "vs":
        v_v = stw105[:, 3]
        v_h = stw105[:, 7]
        v = np.sqrt((2 * v_v ** 2 + v_h ** 2) / 3)
    elif parameter == "vp":
        v_v = stw105[:, 2]
        v_h = stw105[:, 6]
        v = np.sqrt((v_v ** 2 + 4*v_h ** 2) / 5)
    f = interpolate.interp1d((6371000-r)/1000, v)
    stw105_depth = f(np.arange(0, 2005, 10))/1000
    stw105_abs_data = copy_model.copy()
    for index in range(201):
        stw105_abs_data.data[:, :, index] = stw105_depth[index]
    return stw105_abs_data


def load_ak135(parameter: str) -> xr.DataArray:
    ak135 = np.loadtxt(ak135_path, delimiter=',')
    h = ak135[:, 0]
    if parameter == "vp":
        v = ak135[:, 2]
    else:
        v = ak135[:, 3]
    f = interpolate.interp1d(h, v)
    ak135_depth = f(np.arange(0, 2005, 10))
    ak135_abs_data = copy_model.copy()
    for index in range(201):
        ak135_abs_data.data[:, :, index] = ak135_depth[index]
    return ak135_abs_data


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
    if model_type in ["vp", "vs"]:
        to_interp_data = data[model_type]
    elif model_type == "vp_vs":
        to_interp_data = data["vp"]-data["vs"]
    elif model_type == "radial":
        to_interp_data = (data["vsh"]-data["vsv"])/data["vs"]
    else:
        raise Exception(
            f"{model_type} is not a supported model_type. Try to use vp, vs, vp_vs, or radial.")

    to_interp_data.data[nzcc_mask < 0.3] = np.nan
    return to_interp_data


def prepare_cross_section(to_interp_data: xr.DataArray, depth: int, model_type: str) -> xr.DataArray:
    hlat = np.linspace(10, 58, 201)
    hlat = xr.DataArray(hlat, dims='hlat', coords={'hlat': hlat})
    hlon = np.linspace(83, 155, 301)
    hlon = xr.DataArray(hlon, dims='hlon', coords={'hlon': hlon})

    plot_data = to_interp_data.interp(
        depth=depth, latitude=hlat, longitude=hlon)
    plot_data = plot_data.T
    if model_type == "radial":
        plot_data.data = gaussian_filter(plot_data.data, sigma=2)
    return plot_data


def plot_base(model_type: str, depths: List[int], cpt_series: str, cpt_reverse: bool, save_name: str, colorbar_content: str, ref='eara2022') -> None:
    # * configurations
    sizes = len(depths)
    cols = 3
    if sizes % 3 == 0:
        rows = sizes//cols
    else:
        rows = sizes//cols+1

    # * load ndarray
    if model_type == "radial":
        data: xr.Dataset = xr.open_dataset(
            eara2021_abs_path)
    else:
        if ref == 'eara2022':
            data: xr.Dataset = xr.open_dataset(
                eara2021_per_path)
        else:
            # other models are only for vs, vp, and vp_vs
            data: xr.Dataset = xr.open_dataset(
                eara2021_abs_path)
            if ref == 'stw105':
                ref_model_vp = load_stw105('vp')
                ref_model_vs = load_stw105('vs')
            elif ref == 'ak135':
                ref_model_vp = load_ak135('vp')
                ref_model_vs = load_ak135('vs')
            else:
                raise Exception('ref is not supported.')
            data['vp'].data = data['vp'].data/ref_model_vp.data-1
            data['vs'].data = data['vs'].data/ref_model_vs.data-1

    # load mask
    mask_path = resource(['model_files', 'mask.npy'], normal_path=True)
    nzcc_mask = np.load(mask_path)
    to_interp_data = prepare_model(data, nzcc_mask, model_type)

    # * figure
    fig = pygmt.Figure()
    pygmt.config(FONT_LABEL="18p", MAP_LABEL_OFFSET="18p",
                 FONT_ANNOT_PRIMARY="18p", MAP_FRAME_TYPE="plain")
    pygmt.makecpt(cmap=resource(['cpt', 'dvs_6p_nan.cpt']),
                  series=cpt_series, continuous=True, background="o", reverse=cpt_reverse)

    fig.shift_origin(yshift="5i")
    with fig.subplot(nrows=rows, ncols=cols, figsize=(f"{cols*6}i", f"{rows*5.2}i"), sharex='b', sharey='l', margins=['0.05i', '0.02i'], frame=["WSen", "xaf", "yaf"]):
        for idx in range(sizes):
            with pygmt.config(MAP_FRAME_TYPE="plain", MAP_TICK_LENGTH="0p"):
                fig.basemap(region=[83, 155, 10, 58],
                            projection="M?", panel=idx)
            fig.grdimage(prepare_cross_section(
                to_interp_data, depths[idx], model_type))
            plot_base_map(fig, depths[idx])

            fig.text(
                position="TL", text=f"({ascii_lowercase[idx]})", font="28p,Helvetica-Bold,black", offset="j0.1i/0.15i")
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

    save_path(fig, save_name)
