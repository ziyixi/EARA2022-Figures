import string
from functools import cache

import numpy as np
import pygmt
import xarray as xr
from eara2022 import resource, save_path
from eara2022.utils import get_vol_list
from eara2022.utils.plot import plot_place_holder
from eara2022.utils.slice import (extend_line, gmt_lat_as_dist,
                                  gmt_lon_as_dist, model_interp, topo_interp)
from scipy import interpolate


def con_plot_base(conf: dict) -> None:
    # * load the model
    eara2021_per_path = resource(
        ['model_files', 'eara2021_per_ref.nc'], normal_path=True)
    eara2021_abs_path = resource(
        ['model_files', 'eara2021.nc'], normal_path=True)
    mask_path = resource(
        ['model_files', 'mask.npy'], normal_path=True)
    copy_model: xr.DataArray = xr.open_dataset(eara2021_per_path)[
        conf['parameter']]
    stw105_path = resource(['model_files', 'stw105.txt'], normal_path=True)
    ak135_path = resource(['model_files', 'AK135F_AVG.csv'], normal_path=True)
    copy_model: xr.DataArray = xr.open_dataset(eara2021_per_path)["vs"]

    # * lines
    all_lines = [
        (95, 28, 110, 26, "lon"),
        (95, 25, 110, 32, "lon"),
        (95, 31, 110, 29, "lon"),
        (105, 39, 120, 38, "lon"),
        (105, 37, 120, 36, "lon"),
        (107, 32, 112, 47, "lat"),
        (115, 42, 130, 46, "lon"),
        (115, 49, 130, 44, "lon"),
    ]

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

    def smooth_model(model: xr.DataArray) -> xr.DataArray:
        model[:, :, 41] = (model[:, :, 40]+model[:, :, 42])/2
        model[:, :, 65] = (3*model[:, :, 64]+1*model[:, :, 67])/4
        model[:, :, 66] = (1*model[:, :, 64]+3*model[:, :, 67])/4
        return model

    def load_eara2021_per(parameter: str) -> xr.DataArray:
        eara2021_ref = xr.open_dataset(eara2021_per_path)[parameter]
        return eara2021_ref*100

    def load_eara2021_abs(parameter: str) -> xr.DataArray:
        eara2021_abs = xr.open_dataset(eara2021_abs_path)[parameter]
        return eara2021_abs

    def load_mask() -> xr.DataArray:
        mask = np.load(mask_path)
        mask_xarray = copy_model.copy()
        mask_xarray.data = mask
        return mask_xarray

    @cache
    def prepare_plot(idx: int, length: float) -> dict:
        # * prepare plotting for each idx
        startlon, startlat, endlon, endlat, thetype = all_lines[idx]
        start = (startlon, startlat)
        end = (endlon, endlat)
        endlon, endlat = extend_line(start, end, length)
        if (thetype == "lat" and startlat > endlat) or (thetype == "lon" and startlon > endlon):
            startlon, startlat, endlon, endlat = endlon, endlat, startlon, startlat
        start = (startlon, startlat)
        end = (endlon, endlat)
        # * generate the plotting lons, lats for interp
        # we should project along specific direction
        points = pygmt.project(center=list(start), endpoint=list(
            end), generate=0.02)
        res = {
            'start': start,
            'end': end,
            'type': thetype,
            'lons': points.r,
            'lats': points.s,
            'deps': np.linspace(0, 1000, 1001),
            'deps_abs': np.linspace(0, 100, 101)
        }
        return res

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
                res['x'][row][col] = f"f{col*conf['x_offset']+0.8:.2f}i"
                res['y'][row][col] = f"f{(2-row)*conf['y_offset']+2.5:.2f}i"
                res['yabs'][row][col] = f"f{(2-row)*conf['y_offset']+conf['yabs_offset']+2.5:.2f}i"
                res['ytopo'][row][col] = f"f{(2-row)*conf['y_offset']+conf['ytopo_offset']+2.5:.2f}i"
        return res

    def plot_per(fig: pygmt.Figure, offset: dict[str, np.ndarray], row: int, col: int, info: dict, annote: str, eara: xr.DataArray) -> None:
        fig.shift_origin(xshift=offset['x'][row]
                         [col], yshift=offset['y'][row][col])

        xlabel = "Longitude (degree)" if info['type'] == 'lon' else "Latitude (degree)"
        with pygmt.config(MAP_FRAME_TYPE="plain", MAP_TICK_LENGTH="0p"):
            if col == 0:
                fig.basemap(projection=f"X{conf['x_fig']}i/-2.7i",
                            region=f"0/{conf['length']}/0/1000", frame=["WSen", f'pxc{annote}+l"{xlabel}"', 'yaf+l"Depth (km)"'])
            else:
                fig.basemap(projection=f"X{conf['x_fig']}i/-2.7i",
                            region=f"0/{conf['length']}/0/1000", frame=["wSen", f'pxc{annote}+l"{xlabel}"', "yaf"])

        cross_section = model_interp(
            eara, info['lons'], info['lats'], info['deps'])
        cross_section_xarray = xr.DataArray(cross_section, dims=(
            'h', "v"), coords={'h': np.linspace(0, conf['length'], len(info['lons'])), "v": info['deps']})
        fig.grdimage(cross_section_xarray.T)
        for interval in ["+-10", "+-8", "+-6", "+-4", "+-2"]:
            fig.grdcontour(cross_section_xarray.T, interval=interval,
                           pen="0.5p,black", cut=300, annotation=interval+"+f8p+u%")
        for interval in ["+2", "+4", "+6", "+8"]:
            fig.grdcontour(cross_section_xarray.T, interval=interval,
                           pen="0.5p,white", cut=300, annotation=interval+"+f8p+u%")
        # 410 and 660
        y_410 = np.zeros_like(info['lons'])
        y_410[:] = 410
        y_650 = np.zeros_like(info['lons'])
        y_650[:] = 650
        fig.plot(x=np.linspace(0, conf['length'], len(info['lons'])),
                 y=y_410, pen="0.5p,black,dashed")
        fig.plot(x=np.linspace(0, conf['length'], len(info['lons'])),
                 y=y_650, pen="0.5p,black,dashed")

        with pygmt.config(MAP_FRAME_TYPE="inside", MAP_TICK_LENGTH_PRIMARY="10p"):
            fig.basemap(projection=f"X{conf['x_fig']}i/-2.7i",
                        region=f"0/{conf['length']}/0/1000", frame=["wsen", f'pxc{annote}', "yaf"])

    def plot_abs(fig: pygmt.Figure, offset: dict[str, np.ndarray], row: int, col: int, info: dict, annote: str, eara_abs: xr.DataArray) -> None:
        fig.shift_origin(xshift=offset['x'][row]
                         [col], yshift=offset['yabs'][row][col])
        with pygmt.config(MAP_FRAME_TYPE="plain", MAP_TICK_LENGTH="0p"):
            fig.basemap(projection=f"X{conf['x_fig']}i/-0.7i",
                        region=f"0/{conf['length']}/0/100", frame=["wsen", f'pxc{annote}', "ya100f50"])
        cross_section = model_interp(
            eara_abs, info['lons'], info['lats'], info['deps_abs'])
        cross_section_xarray = xr.DataArray(cross_section, dims=(
            'h', "v"), coords={'h': np.linspace(0, conf['length'], len(info['lons'])), "v": info['deps_abs']})
        fig.grdimage(cross_section_xarray.T)

        with pygmt.config(MAP_FRAME_TYPE="inside", MAP_TICK_LENGTH_PRIMARY="10p"):
            fig.basemap(projection=f"X{conf['x_fig']}i/-0.7i",
                        region=f"0/{conf['length']}/0/100", frame=["wsen", f'pxc{annote}', "ya100f50"])

    def plot_topo(fig: pygmt.Figure, offset: dict[str, np.ndarray], row: int, col: int, info: dict, annote: str, grd_topo: xr.DataArray) -> None:
        fig.shift_origin(xshift=offset['x'][row]
                         [col], yshift=offset['ytopo'][row][col])
        with pygmt.config(MAP_FRAME_TYPE="plain", MAP_TICK_LENGTH="0p"):
            fig.basemap(projection=f"X{conf['x_fig']}i/1i",
                        region=f"0/{conf['length']}/0/6000", frame=["lsrn", 'ya2500f', f'pxc{annote}'])

        grd_interp_result = topo_interp(
            grd_topo, info['lons'], info['lats'])
        grd_interp_result_above = grd_interp_result.copy()
        grd_interp_result_above[grd_interp_result_above < 0] = 0
        grd_interp_result_below = grd_interp_result.copy()
        grd_interp_result_below[grd_interp_result_below > 0] = 0

        fig.plot(x=np.linspace(0, conf['length'], len(
            info['lons'])), y=grd_interp_result_above, pen="black", close="+y0", color="gray")
        fig.plot(x=np.linspace(0, conf['length'], len(
            info['lons'])), y=grd_interp_result_below, pen="black", close="+y0", color="lightblue")
        fig.text(x=1, y=5000, text=string.ascii_uppercase[row*3+col],
                 font="24p,Helvetica-Bold,black", offset="j0.1i/0.3i")

    def plot_text(fig: pygmt.Figure, idx: int) -> None:
        if idx == 0:
            fig.text(x=5.5, y=4000, text=f"Chuandian Block",
                     font="16p,Helvetica,red")
            fig.text(x=11.5, y=2000, text=f"South China Block",
                     font="16p,Helvetica,red")
        if idx == 1:
            fig.text(x=1.5, y=2000, text=f"Burma", font="16p,Helvetica,red")
            fig.text(x=6, y=4500, text=f"Chuandian Block",
                     font="16p,Helvetica,red")
            fig.text(x=12, y=2000, text=f"Sichuan Basin",
                     font="16p,Helvetica,red")
        if idx == 2:
            fig.text(x=3, y=2500, text=f"Qiangtang Block",
                     font="16p,Helvetica,red")
            fig.text(x=5, y=4000, text=f"Chuandian Block",
                     font="16p,Helvetica,red")
            fig.text(x=8.5, y=2000, text=f"Sichuan Basin",
                     font="16p,Helvetica,red")
        if idx == 3:
            fig.text(x=3, y=2500, text=f"Ordos Block",
                     font="16p,Helvetica,red")
            fig.text(x=6, y=4000, text=f"Taihang Mountains",
                     font="16p,Helvetica,red")
            fig.text(x=9.5, y=2000, text=f"Huabei Plain",
                     font="16p,Helvetica,red")
        if idx == 4:
            fig.text(x=3, y=2500, text=f"Ordos Block",
                     font="16p,Helvetica,red")
            fig.text(x=6, y=4000, text=f"Taihang Mountains",
                     font="16p,Helvetica,red")
            fig.text(x=9.5, y=2000, text=f"Huabei Plain",
                     font="16p,Helvetica,red")
        if idx == 5:
            fig.text(x=2, y=4000, text=f"Qinlin", font="16p,Helvetica,red")
            fig.text(x=5.5, y=3000, text=f"Ordos Block",
                     font="16p,Helvetica,red")
            fig.text(x=12, y=3000, text=f"Mongolian Plateau",
                     font="16p,Helvetica,red")
        if idx == 6:
            fig.text(x=2.5, y=3000, text=f"Yin Mountains",
                     font="16p,Helvetica,red")
            fig.text(x=7, y=1500, text=f"Songliao Basin",
                     font="16p,Helvetica,red")
        if idx == 7:
            fig.plot(x=4, y=2000, style="kvolcano/0.3", color="red")
            fig.text(x=4, y=4200, text=f"Arshan Volcano ",
                     font="16p,Helvetica,red")
            fig.text(x=3, y=3000, text=f"Mongolian Plateau",
                     font="16p,Helvetica,red")
            fig.text(x=7.5, y=1500, text=f"Songliao Basin",
                     font="16p,Helvetica,red")
            fig.text(x=10.5, y=3000, text=f"Changbai Mountains",
                     font="16p,Helvetica,red")

    def plot_base_map(fig: pygmt.Figure) -> None:
        fig.coast(water="167/194/223")
        grd_topo = pygmt.datasets.load_earth_relief(
            resolution="02m", region=[83, 160, 10, 60])
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

    # * main
    fig = pygmt.Figure()
    pygmt.config(FONT_LABEL="15p", MAP_LABEL_OFFSET="12p",
                 FONT_ANNOT_PRIMARY="12p", MAP_FRAME_TYPE="plain")
    plot_place_holder(fig)
    offset = generate_offset()

    # prepare plotting
    mask = load_mask()
    eara_abs = load_eara2021_abs(conf['parameter'])

    # * different reference models
    if conf['ref'] == 'eara2022':
        eara = load_eara2021_per(conf['parameter'])
    else:
        if conf['ref'] == 'stw105':
            ref_model = load_stw105(conf['parameter'])
        elif conf['ref'] == 'ak135':
            ref_model = load_ak135(conf['parameter'])
        else:
            raise Exception(f"unknown reference model: {conf['ref']}")
        eara = eara_abs.copy()
        eara.data = (eara.data/ref_model.data-1)*100
        smooth_model(eara)

    eara.data[mask.data < 0.3] = np.nan
    eara_abs.data[mask.data < 0.3] = np.nan
    grd_topo = pygmt.datasets.load_earth_relief(
        resolution="02m", region=[83, 160, 10, 60])

    # * plot figures
    for idx in range(len(all_lines)):
        row, col = divmod(idx, 3)
        info = prepare_plot(idx, length=conf['length'])
        if info['type'] == 'lat':
            annote = gmt_lat_as_dist(
                info['start'], info['end'], a_interval=5, g_interval=1)
        elif info["type"] == 'lon':
            annote = gmt_lon_as_dist(
                info['start'], info['end'], a_interval=5, g_interval=1)

        # * perturbation
        pygmt.makecpt(cmap=resource(['cpt', 'dvs_6p_nan.cpt']),
                      series=f"-3/3/1", continuous=True, background="o")
        plot_per(fig, offset, row, col, info, annote, eara)
        # * abs
        pygmt.makecpt(cmap="seis", series=conf['abs_cpt'],
                      continuous=True, background="o")
        plot_abs(fig, offset, row, col, info, annote, eara_abs)
        # * topo
        plot_topo(fig, offset, row, col, info, annote, grd_topo)
        # * texts
        plot_text(fig, idx)

    # * map
    fig.shift_origin(xshift="f10.5i", yshift="f3i")
    with pygmt.config(MAP_FRAME_TYPE="plain", MAP_TICK_LENGTH="0p"):
        fig.basemap(region=[83, 160, 10, 60], projection="M4.1i", frame=[
                    "WSen", "xaf", "yaf"])

    plot_base_map(fig)
    # plot arrows
    style = "=0.2i+s+e+a30+gblue+h0.5+p0.3i,blue"
    for idx in range(len(all_lines)):
        info = prepare_plot(idx, length=conf['length'])
        fig.plot(data=[list(info['end'])+list(info['start'])],
                 style=style, pen="0.05i,blue")
        if idx in [3, 4]:
            fig.text(x=info['lons'][len(info['lons'])//2], y=info['lats'][len(info['lats'])//2],
                     text=string.ascii_uppercase[idx], fill="white", font="10p,Helvetica-Bold,black")
        elif idx in [0, 1, 2, 5]:
            fig.text(x=info['lons'][len(info['lons'])//4*3], y=info['lats'][len(info['lats'])//4*3],
                     text=string.ascii_uppercase[idx], fill="white", font="10p,Helvetica-Bold,black")
        else:
            fig.text(x=info['lons'][len(info['lons'])//4], y=info['lats'][len(info['lats'])//4],
                     text=string.ascii_uppercase[idx], fill="white", font="10p,Helvetica-Bold,black")

    with pygmt.config(MAP_FRAME_TYPE="inside", MAP_TICK_LENGTH_PRIMARY="10p"):
        fig.basemap(region=[83, 160, 10, 60], projection="M4.1i", frame=[
                    "wsen", "xaf", "yaf"])

    # * colorbar
    fig.shift_origin(xshift="f0i", yshift="f2.5i")
    pygmt.makecpt(cmap=resource(['cpt', 'dvs_6p_nan.cpt']),
                  series=f"-3/3/1", continuous=True, background="o")
    fig.colorbar(
        # justified inside map frame (j) at Top Center (TC)
        position="JBC+w5i/0.8c+h+o1i/1i",
        box=False,
        frame=["a1f", f"+L@~d@~ln{conf['cbar']}(%)"],
        scale=1)
    # pygmt.makecpt(cmap="seis",series=f"2.8/4.6/0.3",continuous=True, D="o")
    pygmt.makecpt(cmap="seis", series=conf['abs_cpt'],
                  continuous=True, background="o")
    fig.colorbar(
        # justified inside map frame (j) at Top Center (TC)
        position="JBC+w5i/0.8c+h+o7i/1i",
        box=False,
        frame=["a0.3f", f"+L{conf['cbar']}(km/s)"],
        scale=1)

    save_path(fig, conf['save_name'])
