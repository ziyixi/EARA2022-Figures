""" 
psf.py

Plot the point spread function test result.
"""
import numpy as np
import pygmt
import xarray as xr
from eara2022 import resource, save_path
from eara2022.utils.psf import get_perturbation_array

depths = [100, 300, 500, 700, 900]
categories = ["per", "betav", "betah", "bulkc"]


def prepare_data(psf_list_path: str, psf_nc_path: str) -> dict[str, dict[int, xr.DataArray]]:
    per_array = get_perturbation_array(psf_list_path, psf_nc_path)
    data = xr.open_dataset(psf_nc_path)
    # * generate xarray
    data_per = data["bulk_c_kernel"].copy()
    data_per.data[:, :, :] = per_array[:, :, :]
    data_betav = data["bulk_betav_kernel"]
    data_betav.data[data_betav.data > 9e6] = np.nan
    data_betah = data["bulk_betah_kernel"]
    data_betah.data[data_betah.data > 9e6] = np.nan
    data_bulkc = data["bulk_c_kernel"]
    data_bulkc.data[data_bulkc.data > 9e6] = np.nan
    # * interp
    hlat = np.linspace(10, 58, 201)
    hlat = xr.DataArray(hlat, dims='hlat', coords={'hlat': hlat})
    hlon = np.linspace(83, 155, 301)
    hlon = xr.DataArray(hlon, dims='hlon', coords={'hlon': hlon})
    # * get res
    res = {}
    categories_mapper = {
        "per": data_per,
        "betav": data_betav,
        "betah": data_betah,
        "bulkc": data_bulkc
    }
    for category in categories_mapper:
        res[category] = {}
        for dep in depths:
            res[category][dep] = categories_mapper[category].interp(
                depth=dep, latitude=hlat, longitude=hlon).T
    return res


def main() -> None:
    fig = pygmt.Figure()
    pygmt.config(FONT_LABEL="18p", MAP_LABEL_OFFSET="18p",
                 FONT_ANNOT_PRIMARY="18p", MAP_FRAME_TYPE="plain")

    # eara2022/resource/psf/psf_list.txt
    psf_list_path = resource(['psf', 'psf_list.txt'], normal_path=True)
    # eara2022/resource/model_files/psf_vsv_bulk_iter19.nc
    psf_nc_path = resource(
        ['model_files', 'psf_vsv_bulk_iter19.nc'], normal_path=True)
    plot_data = prepare_data(
        psf_list_path=psf_list_path, psf_nc_path=psf_nc_path)

    series = ["-0.01/0.01/0.01", "-0.0000003/0.0000003/0.0000001",
              "-0.0000003/0.0000003/0.0000001", "-0.0000003/0.0000003/0.0000001"]
    texts = ["sv", "sv", "sh", "c"]
    with fig.subplot(nrows=5, ncols=4, figsize=("20i", "20i"), sharex='b', sharey='l', margins=['0.05i', '0.05i'], frame=["WSen", "xaf", "yaf"], autolabel="A)+o0.2i/0.1i"):
        for icategory, category in enumerate(categories):
            for idep, dep in enumerate(depths):
                with pygmt.config(MAP_FRAME_TYPE="plain", MAP_TICK_LENGTH="0p"):
                    fig.basemap(region=[82, 155, 10, 58],
                                projection="M?", panel=[idep, icategory])
                pygmt.makecpt(cmap=resource(
                    ['cpt', 'dvs_6p.cpt']), series=series[icategory], continuous=True, background="o")
                fig.grdimage(plot_data[category][dep])
                fig.coast(shorelines="0.5p,black",
                          borders=["1/0.5p,black"], resolution="l", area_thresh="5000")
                fig.plot(data=resource(
                    ["Plate_Boundaries", "nuvel1_boundaries"]), pen="2p,red")
                fig.plot(data=resource(
                    ["China_blocks", "block2d_mod.txt"]), pen="1p,green4")
                fig.plot(data=resource(
                    ["China_blocks", "China_Basins"]), pen="1p,green4")
                fig.text(
                    position="TR", text=f"{dep} km", font="28p,Helvetica-Bold,black", offset="j0.1i/0.15i")
                fig.text(position="BR", text=f"V@-{texts[icategory]}@-",
                         font="28p,32,black", offset="j0.1i/0.15i")

                with pygmt.config(MAP_FRAME_TYPE="inside", MAP_TICK_LENGTH_PRIMARY="10p"):
                    fig.basemap(region=[82, 155, 10, 58], projection="M?", frame=[
                                "wsen", "xaf", "yaf"], panel=[idep, icategory])

    save_path(fig, "psf")


if __name__ == "__main__":
    main()
