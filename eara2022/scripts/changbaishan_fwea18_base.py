"""
changbaishan_fwea18_base

Directly plot the Changbaishan volcano region's structure. Will be used in Jiaqi's paper.
"""
import numpy as np
import pygmt
import xarray as xr
from eara2022 import resource, save_path
from eara2022.utils import get_vol_list
from eara2022.utils.plot import plot_place_holder
from eara2022.utils.slice import extend_line, gmt_lon_as_dist, model_interp
from scipy import interpolate

# * settings
np.seterr(divide='ignore')
np.seterr(invalid='ignore')

start_point = (118, 42)
end_point = (128.08, 41.98)
end_point = extend_line(start_point, end_point, 18)

# * several paths for the models, some may unused
eara2021_per_path = resource(
    ['model_files', 'eara2021_per_ref.nc'], normal_path=True)
fwea18_abs_path = resource(['model_files', 'fwea18.nc'], normal_path=True)
ak135_path = resource(['model_files', 'AK135F_AVG.csv'], normal_path=True)
iasp91_path = resource(['model_files', 'iasp91.txt'], normal_path=True)


# * load models with the respect to certain reference model
copy_model: xr.DataArray = xr.open_dataset(eara2021_per_path)["vs"]


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


def load_iasp91(parameter: str) -> xr.DataArray:
    iasp91 = np.loadtxt(iasp91_path)
    h = iasp91[:, 0]
    if parameter == "vp":
        v = iasp91[:, 1]
    else:
        v = iasp91[:, 2]
    f = interpolate.interp1d(h, v, fill_value="extrapolate")
    iasp91_depth = f(np.arange(0, 2005, 10))
    iasp91_abs_data = copy_model.copy()
    for index in range(201):
        iasp91_abs_data.data[:, :, index] = iasp91_depth[index]
    return iasp91_abs_data


def load_fwea18(parameter: str, ref_model: xr.DataArray) -> xr.DataArray:
    fwea18_abs = xr.open_dataset(fwea18_abs_path)
    if parameter == "vs":
        fwea18_abs_iso = np.sqrt(
            (2 * fwea18_abs["vsv"] ** 2 + fwea18_abs["vsh"] ** 2) / 3)
        fwea18_abs_iso_interp = fwea18_abs_iso.interp_like(copy_model)
    else:
        fwea18_abs_iso = np.sqrt(
            (fwea18_abs["vpv"] ** 2 + 4 * fwea18_abs["vph"] ** 2) / 5)
        fwea18_abs_iso_interp = fwea18_abs_iso.interp_like(copy_model)
    fwea18_per = copy_model.copy()
    fwea18_per.data = fwea18_abs_iso_interp.data/ref_model.data-1
    return fwea18_per*100


def smooth_model(model: xr.DataArray) -> xr.DataArray:
    model[:, :, 41] = (model[:, :, 40]+model[:, :, 42])/2
    model[:, :, 65] = (3*model[:, :, 64]+1*model[:, :, 67])/4
    model[:, :, 66] = (1*model[:, :, 64]+3*model[:, :, 67])/4
    return model


def plot_base(ref_key: str, save_name: str):
    # * load models
    mapper = {
        'ak135': load_ak135,
        "iasp91": load_iasp91
    }
    ref_model_vs = mapper[ref_key]("vs")
    ref_model_vp = mapper[ref_key]("vp")
    fwea18_vs = load_fwea18("vs", ref_model_vs)
    fwea18_vp = load_fwea18("vp", ref_model_vp)

    # * draw the base plot
    fig = pygmt.Figure()
    pygmt.makecpt(cmap=resource(['cpt', 'dvs_6p_nan.cpt']),
                  series="-3/3/1", continuous=True, background="o")

    plot_place_holder(fig)
    # * prepare plotting
    tmp_xannote = gmt_lon_as_dist(
        start_point, end_point, a_interval=5, g_interval=1)
    fwea18_vs = smooth_model(fwea18_vs)
    fwea18_vp = smooth_model(fwea18_vp)

    # the lons and lats
    points = pygmt.project(
        center=start_point, endpoint=end_point, generate=0.02)
    lons: np.ndarray = points.r
    lats: np.ndarray = points.s
    deps = np.linspace(0, 1000, 1001)

    # * plot figure
    # * vs
    with pygmt.config(MAP_FRAME_TYPE="plain", MAP_TICK_LENGTH="0p"):
        fig.basemap(projection=f"X5.4i/-2.7i",
                    region=f"0/18/0/1000", frame=["WSen", 'yaf+l"Depth (km)"', f'pxc{tmp_xannote}+l"Longitude (degree)"'])

        # cs
        cross_section = model_interp(fwea18_vs, lons, lats, deps)
        cross_section_xarray = xr.DataArray(cross_section, dims=(
            'h', "v"), coords={'h': np.linspace(0, 18, len(lons)), "v": deps})
        fig.grdimage(cross_section_xarray.T)
        for interval in ["+-7.5", "+-6", "+-4.5", "+-3", "+-1.5"]:
            fig.grdcontour(cross_section_xarray.T, interval=interval,
                           pen="0.5p,black", cut=300, annotation=interval+"+f8p+u%")
        for interval in ["+1.5", "+3", "+4.5", "+6"]:
            fig.grdcontour(cross_section_xarray.T, interval=interval,
                           pen="0.5p,white", cut=300, annotation=interval+"+f8p+u%")
        # 410 and 660
        y_410 = np.zeros_like(lons)
        y_410[:] = 410
        y_650 = np.zeros_like(lats)
        y_650[:] = 650
        fig.plot(x=np.linspace(0, 18, len(lons)),
                 y=y_410, pen="0.5p,black,dashed")
        fig.plot(x=np.linspace(0, 18, len(lons)),
                 y=y_650, pen="0.5p,black,dashed")
        fig.text(x=17, y=900, text="A",
                 font="18p,Helvetica-Bold,black", fill="white", offset="j0.1i/0.3i")
        fig.plot(x=7.42, y=-50, style="kvolcano/0.7",
                 color="red", no_clip=True)

    with pygmt.config(MAP_FRAME_TYPE="inside", MAP_TICK_LENGTH_PRIMARY="10p"):
        fig.basemap(projection=f"X5.4i/-2.7i",
                    region=f"0/18/0/1000", frame=["wsen", f'pxc{tmp_xannote}', 'yaf'])

    fig.colorbar(
        # justified inside map frame (j) at Top Center (TC)
        position="JBC+w4i/0.8c+h+o0i/1.5c",
        box=False,
        frame=["a1f", f'"+L@~d@~lnVs(%)"'],
        scale=1,)

    # * vp
    fig.shift_origin(xshift="f10.5i")
    with pygmt.config(MAP_FRAME_TYPE="plain", MAP_TICK_LENGTH="0p"):
        fig.basemap(projection=f"X5.4i/-2.7i",
                    region=f"0/18/0/1000", frame=["wSen", 'yaf', f'pxc{tmp_xannote}+l"Longitude (degree)"'])

        # cs
        cross_section = model_interp(fwea18_vp, lons, lats, deps)
        cross_section_xarray = xr.DataArray(cross_section, dims=(
            'h', "v"), coords={'h': np.linspace(0, 18, len(lons)), "v": deps})
        fig.grdimage(cross_section_xarray.T)
        for interval in ["+-7.5", "+-6", "+-4.5", "+-3", "+-1.5"]:
            fig.grdcontour(cross_section_xarray.T, interval=interval,
                           pen="0.5p,black", cut=300, annotation=interval+"+f8p+u%")
        for interval in ["+1.5", "+3", "+4.5", "+6"]:
            fig.grdcontour(cross_section_xarray.T, interval=interval,
                           pen="0.5p,white", cut=300, annotation=interval+"+f8p+u%")
        # 410 and 660
        y_410 = np.zeros_like(lons)
        y_410[:] = 410
        y_650 = np.zeros_like(lats)
        y_650[:] = 650
        fig.plot(x=np.linspace(0, 18, len(lons)),
                 y=y_410, pen="0.5p,black,dashed")
        fig.plot(x=np.linspace(0, 18, len(lons)),
                 y=y_650, pen="0.5p,black,dashed")
        fig.text(x=17, y=900, text="B",
                 font="18p,Helvetica-Bold,black", fill="white", offset="j0.1i/0.3i")
        fig.plot(x=7.42, y=-50, style="kvolcano/0.7",
                 color="red", no_clip=True)

    with pygmt.config(MAP_FRAME_TYPE="inside", MAP_TICK_LENGTH_PRIMARY="10p"):
        fig.basemap(projection=f"X5.4i/-2.7i",
                    region=f"0/18/0/1000", frame=["wsen", f'pxc{tmp_xannote}', 'yaf'])

    fig.colorbar(
        # justified inside map frame (j) at Top Center (TC)
        position="JBC+w4i/0.8c+h+o0i/1.5c",
        box=False,
        frame=["a1f", f'"+L@~d@~lnVp(%)"'],
        scale=1,)

    save_path(fig, save_name, suffix="pdf")
