"""
changbaishan_models_base

Compare models bfor the structure beneath the Changbaishan volcano, with the referencec model passed.
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
# * old points
# start_point = (113, 42)
# end_point = (145.6063681055389, 38)
# * new points
start_point = (118, 42)
end_point = (128.08, 41.98)
end_point = extend_line(start_point, end_point, 23)

# * several paths for the models, some may unused
eara2021_abs_path = resource(['model_files', 'eara2021.nc'], normal_path=True)
eara2021_per_path = resource(
    ['model_files', 'eara2021_per_ref.nc'], normal_path=True)
eara2014_abs_path = resource(['model_files', 'eara2014.nc'], normal_path=True)
fwea18_abs_path = resource(['model_files', 'fwea18.nc'], normal_path=True)
gap_p4_per_path = resource(['model_files', 'GAP_P4_dvp.nc'], normal_path=True)
glad_m25_abs_path = resource(
    ['model_files', 'glad-m25-vs-0.0-n4.nc'], normal_path=True)

ref_path = resource(['model_files', 'ref.nc'], normal_path=True)
stw105_path = resource(['model_files', 'stw105.txt'], normal_path=True)
ak135_path = resource(['model_files', 'AK135F_AVG.csv'], normal_path=True)
mask_path = resource(
    ['model_files', 'mask.npy'], normal_path=True)

# * load models with the respect to certain reference model
copy_model: xr.DataArray = xr.open_dataset(eara2021_per_path)["vs"]


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


def load_eara2021_ref(parameter: str) -> xr.DataArray:
    eara2021_ref = xr.open_dataset(ref_path)[parameter]
    return eara2021_ref

# * load other models based on the reference model


def load_eara2021(parameter: str, ref_model: xr.DataArray) -> xr.DataArray:
    eara2021_abs = xr.open_dataset(eara2021_abs_path)[parameter]
    eara2021_per = copy_model.copy()
    eara2021_per.data = eara2021_abs.data/ref_model.data-1
    return eara2021_per*100


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


def load_eara2014(parameter: str, ref_model: xr.DataArray) -> xr.DataArray:
    eara2014_abs = xr.open_dataset(eara2014_abs_path)
    if parameter == "vs":
        eara2014_abs_iso = np.sqrt(
            (2 * eara2014_abs["vsv"] ** 2 + eara2014_abs["vsh"] ** 2) / 3)
        eara2014_abs_iso_interp = eara2014_abs_iso.interp_like(copy_model)
    else:
        eara2014_abs_iso = np.sqrt(
            (eara2014_abs["vpv"] ** 2 + 4 * eara2014_abs["vph"] ** 2) / 5)
        eara2014_abs_iso_interp = eara2014_abs_iso.interp_like(copy_model)
    eara2014_per = copy_model.copy()
    eara2014_per.data = eara2014_abs_iso_interp.data/ref_model.data-1
    return eara2014_per*100


def load_glad_m25(parameter: str, ref_model: xr.DataArray) -> xr.DataArray:
    # only have vs model
    glad_m25_abs = xr.open_dataset(glad_m25_abs_path)
    glad_m25_abs_iso = np.sqrt(
        (2 * glad_m25_abs["vsv"] ** 2 + glad_m25_abs["vsh"] ** 2) / 3)
    glad_m25_abs_iso_interp = glad_m25_abs_iso.interp_like(copy_model)
    glad_m25_per = copy_model.copy()
    glad_m25_per.data = np.transpose(
        glad_m25_abs_iso_interp.data)/ref_model.data-1
    return glad_m25_per*100


def load_gap_p4() -> xr.DataArray:
    gapp4_per = xr.open_dataset(gap_p4_per_path)
    gapp4_ref_vp = gapp4_per["v"].interp_like(copy_model)
    # reverse direction
    gapp4_ref_vp_corrected = copy_model.copy()
    gapp4_ref_vp_corrected.data = np.transpose(gapp4_ref_vp.data)
    return gapp4_ref_vp_corrected


def load_mask() -> xr.DataArray:
    mask = np.load(mask_path)
    mask_xarray = copy_model.copy()
    mask_xarray.data = mask
    return mask_xarray


def smooth_model(model: xr.DataArray) -> xr.DataArray:
    model[:, :, 41] = (model[:, :, 40]+model[:, :, 42])/2
    model[:, :, 65] = (3*model[:, :, 64]+1*model[:, :, 67])/4
    model[:, :, 66] = (1*model[:, :, 64]+3*model[:, :, 67])/4
    return model


def plot_base_map(fig: pygmt.Figure) -> None:
    fig.coast(water="167/194/223")
    grd_topo = pygmt.datasets.load_earth_relief(
        resolution="02m", region=[83, 160, 10, 60], registration="gridline")
    fig.grdimage(grd_topo, cmap=resource(
        ['cpt', 'land_sea.cpt'], normal_path=True))
    fig.plot(data=resource(
        ["Plate_Boundaries", "nuvel1_boundaries"]), pen="2p,red")
    fig.plot(data=resource(
        ["China_blocks", "block2d_mod.txt"]), pen="0.5p")
    fig.plot(data=resource(
        ["China_blocks", "China_Basins"]), pen="0.5p")
    for slab in ['izu', 'kur', 'phi', 'ryu', 'man']:
        fig.grdcontour(
            resource(['slab2', f'{slab}_slab2_depth.grd']), interval=100, pen="1.5p,magenta")
    vols = get_vol_list()
    fig.plot(x=vols[:, 1], y=vols[:, 0],
             style="kvolcano/0.4", pen="red")
    # arrows
    style = "=0.2i+s+e+a30+gblue+h0.5+p0.3i,blue"
    fig.plot(data=[list(end_point)+list(start_point)],
             style=style, pen="0.05i,blue")


def plot_base(parameter: str, ref_key: str, save_name: str, colorbar_content: str):
    # * load models
    mapper = {
        "stw105": load_stw105,
        'eara2021': load_eara2021_ref,
        'ak135': load_ak135,
    }
    ref_model = mapper[ref_key](parameter)
    if parameter == "vp":
        ref_model_vs = mapper[ref_key]("vs")
    else:
        ref_model_vs = ref_model

    eara2021 = load_eara2021(parameter, ref_model)
    fwea18 = load_fwea18(parameter, ref_model)
    eara2014 = load_eara2014(parameter, ref_model)
    glad_m25 = load_glad_m25(parameter, ref_model_vs)
    gap_p4 = load_gap_p4()

    # * draw the base plot
    fig = pygmt.Figure()
    pygmt.makecpt(cmap=resource(['cpt', 'dvs_6p_nan.cpt']),
                  series="-3/3/1", continuous=True, background="o")

    # plot_place_holder(fig)
    # * prepare plotting
    X = ["f0.8i", "f7.9i", "f0.8i", "f7.9i", "f0.8i"]
    Y = ["f8.3i"]*2+["f5.4i"]*2+["f2.5i"]
    tmp_xannote = gmt_lon_as_dist(
        start_point, end_point, a_interval=5, g_interval=1)

    models = [eara2021, fwea18, eara2014, glad_m25, gap_p4]
    model_names = ["EARA2021", "FWEA18", "EARA2014", "GLAD_M25", "GAP_P4"]
    for i, model in enumerate(models):
        models[i] = smooth_model(model)
    if parameter == "vs":
        labels = ["Vs", "Vs", "Vs", "Vs", "Vp"]
    elif parameter == "vp":
        labels = ["Vp", "Vp", "Vp", "Vs", "Vp"]

    # the lons and lats
    points = pygmt.project(
        center=start_point, endpoint=end_point, generate=0.02)
    lons: np.ndarray = points.r
    lats: np.ndarray = points.s
    deps = np.linspace(0, 800, 801)

    # mask
    mask_model = load_mask()
    mask_cs = model_interp(mask_model, lons, lats, deps)

    # * plot each figure
    for index in range(5):
        fig.shift_origin(xshift=X[index], yshift=Y[index])
        # basemap
        with pygmt.config(MAP_FRAME_TYPE="plain", MAP_TICK_LENGTH="0p"):
            if index in [0, 2]:
                fig.basemap(projection=f"X6.9i/-2.16i",
                            region=f"0/25/0/800", frame=["Wsen", f'pxc{tmp_xannote}', 'yaf+l"Depth (km)"'])
            elif index in [1, 3]:
                fig.basemap(projection=f"X6.9i/-2.16i",
                            region=f"0/25/0/800", frame=["wsen", 'yaf', f'pxc{tmp_xannote}'])
            else:
                fig.basemap(projection=f"X6.9i/-2.16i",
                            region=f"0/25/0/800", frame=["WSen", 'yaf+l"Depth (km)"', f'pxc{tmp_xannote}+l"Longitude (degree)"'])
        # cs
        cross_section = model_interp(models[index], lons, lats, deps)
        cross_section_xarray = xr.DataArray(cross_section, dims=(
            'h', "v"), coords={'h': np.linspace(0, 25, len(lons)), "v": deps})
        cross_section_xarray_for_contour = cross_section_xarray.copy()
        cross_section_xarray.data[mask_cs < 0.3] = np.nan
        fig.grdimage(cross_section_xarray.T)
        for interval in ["+-10", "+-8", "+-6", "+-4", "+-2"]:
            fig.grdcontour(cross_section_xarray_for_contour.T, interval=interval,
                           pen="0.5p,black", cut=300, annotation=interval+"+f8p+u%")
        for interval in ["+2", "+4", "+6", "+8"]:
            fig.grdcontour(cross_section_xarray_for_contour.T, interval=interval,
                           pen="0.5p,white", cut=300, annotation=interval+"+f8p+u%")
        # 410 and 660
        y_410 = np.zeros_like(lons)
        y_410[:] = 410
        y_650 = np.zeros_like(lats)
        y_650[:] = 650
        fig.plot(x=np.linspace(0, 25, len(lons)),
                 y=y_410, pen="0.5p,black,dashed")
        fig.plot(x=np.linspace(0, 25, len(lons)),
                 y=y_650, pen="0.5p,black,dashed")

        # others
        fig.text(x=2.5, y=100, text=model_names[index],
                 font="18p,Helvetica-Bold,black", fill="white", offset="j0.1i/0.3i")
        fig.text(x=24, y=900, text=labels[index],
                 font="18p,Helvetica-Bold,black", fill="white", offset="j0.1i/0.3i")
        fig.plot(x=7.42, y=-50, style="kvolcano/0.7",
                 color="red", no_clip=True)

        # ticks for the basemap
        with pygmt.config(MAP_FRAME_TYPE="inside", MAP_TICK_LENGTH_PRIMARY="10p"):
            fig.basemap(projection=f"X6.9i/-2.16i",
                        region=f"0/25/0/800", frame=["wsen", f'pxc{tmp_xannote}', 'yaf'])

    # * colorbar
    fig.shift_origin(xshift="f0.8i", yshift="f2.5i")
    fig.colorbar(
        # justified inside map frame (j) at Top Center (TC)
        position="JBC+w5i/0.8c+h+o0i/1.5c",
        box=False,
        frame=["a1f", f'"+L{colorbar_content}"'],
        scale=1,)

    # * plot map
    fig.shift_origin(xshift="f9i", yshift="f1i")
    # basemap
    with pygmt.config(MAP_FRAME_TYPE="plain", MAP_TICK_LENGTH="0p"):
        fig.basemap(region=[83, 160, 10, 60],
                    projection="M5i", frame=["WSen", "xaf", "yaf"])
    plot_base_map(fig)
    # ticks
    with pygmt.config(MAP_FRAME_TYPE="inside", MAP_TICK_LENGTH_PRIMARY="10p"):
        fig.basemap(region=[83, 160, 10, 60],
                    projection="M5i", frame=["wsen", "xaf", "yaf"])

    save_path(fig, save_name)
