"""
waveform.py

compare waveform between the old and the new model
"""
from os.path import join
from string import ascii_uppercase
from typing import Dict, List, TypedDict

import numpy as np
import obspy
import pygmt
from eara2022 import resource, save_path
from eara2022.utils import generate_tmp_file
from eara2022.utils.load_files import load_pickle
from pyasdf import ASDFDataSet

# * configurations
freq_list = ["8/40", "20/120", "40/120"]
labels = ["T = 8 - 40 s", "T = 20 - 120 s", "T = 40 - 120 s"]
components = {
    "Z": ["z", "surface_z"],
    "R": ["r", "surface_r"],
    "T": ["t", "surface_t"]
}
phases = ["P", "S", "sP", "SS", "PP", "ScS"]

conf = {
    'gcmt': "200805071602A",
    'sta_name': "JX.JIJ",
    'start': 200,
    'end': 1100,
    'amp': 0.8,
    'win_height': 0.5
}
colors_mapper = {}
colors = ["red", "orange", "green", "blue", "purple", "magenta"]
for ii in range(6):
    colors_mapper[phases[ii]] = colors[ii]

# * arrivals annotation legend
arrivals_legend_content = ""
for color, phase in zip(colors, phases):
    arrivals_legend_content += f"S 0.1c t 6p {color} 1p 0.25c {phase}\nS 0.1c t 6p - - 0.25c \n"
arrivals_legend = generate_tmp_file(arrivals_legend_content, suffix='.cpt')

# * meca
meca_file_content = "141.8656 36.1291 21.33 14.621 -1.621 -12.999 6.488 17.601 -4.863 17 0 0"
meca = generate_tmp_file(meca_file_content)


class PreparedInfo(TypedDict):
    arrivals: Dict[str, float]
    # [freq,comp,category] for waveforms
    waveforms: Dict[str, Dict[str, Dict[str, np.ndarray]]]
    windows: Dict[str, List[List[float]]]


def prepare_info(old_asdf_dir: str, new_asdf_dir: str, data_dir: str, window_dir: str, data_info_dir: str) -> PreparedInfo:
    # * collect arrivals
    arrivals = {}
    for each_phase in phases:
        arrivals[each_phase] = load_pickle(
            join(data_info_dir, f"traveltime.{each_phase}.pkl"))[conf["gcmt"]][conf["sta_name"]]
    # * collect waveforms
    res = {}
    for each_freq in freq_list:
        res[each_freq] = {}
        # load
        mint, maxt = map(int, each_freq.split("/"))
        data_path = join(
            data_dir, f"{conf['gcmt']}.preprocessed_{mint}s_to_{maxt}s.h5")
        old_path = join(
            old_asdf_dir, f"{conf['gcmt']}.preprocessed_{mint}s_to_{maxt}s.h5")
        new_path = join(
            new_asdf_dir, f"{conf['gcmt']}.preprocessed_{mint}s_to_{maxt}s.h5")
        data = ASDFDataSet(data_path, mode="r")
        old = ASDFDataSet(old_path, mode="r")
        new = ASDFDataSet(new_path, mode="r")
        # process
        event_time: obspy.UTCDateTime = data.events[0].origins[0].time
        for component in components:
            data_slice: obspy.Trace = data.waveforms[conf['sta_name']][f"preprocessed_{mint}s_to_{maxt}s"].select(
                component=component)[0].slice(event_time+conf['start'], event_time+conf['end'])
            old_slice: obspy.Trace = old.waveforms[conf['sta_name']][f"preprocessed_{mint}s_to_{maxt}s"].select(
                component=component)[0].slice(event_time+conf['start'], event_time+conf['end'])
            new_slice: obspy.Trace = new.waveforms[conf['sta_name']][f"preprocessed_{mint}s_to_{maxt}s"].select(
                component=component)[0].slice(event_time+conf['start'], event_time+conf['end'])
            # normalize
            data_slice.normalize()
            old_slice.normalize()
            new_slice.normalize()
            # update the result
            res[each_freq][component] = {}
            res[each_freq][component]['x'] = np.linspace(
                conf['start'], conf['end'], data_slice.stats.npts)
            res[each_freq][component]['data'] = data_slice.data*conf['amp']
            res[each_freq][component]['new'] = new_slice.data*conf['amp']
            res[each_freq][component]['old'] = old_slice.data*conf['amp']

    # * collect windows
    wins = {}
    window_path = join(window_dir, f"{conf['gcmt']}.pkl")
    windows: dict = load_pickle(window_path)
    for component in components:
        wins[component] = []
        all_wins1 = windows[conf["sta_name"]
                            ][components[component][0]].windows
        all_wins2 = windows[conf["sta_name"]
                            ][components[component][1]].windows

        for each_win in all_wins1:
            if each_win.cc >= 0.5:
                wins[component].append(
                    [each_win.left-event_time, each_win.right-event_time])
        for each_win in all_wins2:
            if each_win.cc >= 0.5:
                wins[component].append(
                    [each_win.left-event_time, each_win.right-event_time])
    return {
        "arrivals": arrivals,
        "waveforms": res,
        "windows": wins
    }


def plot_base_map(fig: pygmt.Figure) -> None:
    fig.coast(water="white", resolution="l", land="GRAY81",
              borders=["1/0.8p,white"], lakes=["GRAY81"])
    fig.plot(data=resource(
        ['Plate_Boundaries', 'nuvel1_boundaries']), pen="2p,black")
    for slab in ['izu', 'kur', 'phi', 'ryu', 'man']:
        fig.grdcontour(
            resource(['slab2', f'{slab}_slab2_depth.grd']), interval=100, pen="1p,magenta")


def plot_waveform(fig: pygmt.Figure, prepared_info: PreparedInfo, freq: str):
    waveform = prepared_info["waveforms"][freq]
    arrivals = prepared_info["arrivals"]
    offset = 5
    for comp in components:
        # * waveform
        x, yd, yn, yo = [waveform[comp][key]
                         for key in ['x', 'data', 'new', 'old']]
        fig.plot(x=x, y=yd+offset, pen="0.4p,black")
        fig.plot(x=x, y=yo+offset, pen="0.4p,green4")
        fig.plot(x=x, y=yn+offset, pen="0.4p,red")
        # * windows
        wins = prepared_info["windows"][comp]
        for ii, val in enumerate(wins):
            win_left, win_right = val
            fig.plot(x=[win_left, win_right, win_right, win_left, win_left], y=np.array([-conf['win_height']-ii*0.1, -conf['win_height']-ii *
                     0.1, conf['win_height']+ii*0.1, conf['win_height']+ii*0.1, -conf['win_height']-ii*0.1])+offset, pen="0.5p,black")
        # * arrivals
        for ii, each_phase in enumerate(phases):
            fig.plot(x=arrivals[each_phase], y=offset-0.9-0.03*ii, style="t0.04i",
                     pen=f"0.03i,{colors_mapper[each_phase]}", no_clip=True)

        offset -= 2


def main() -> None:
    # * load info
    prepared_info = prepare_info(
        *[resource(['waveform', file], normal_path=True) for file in ['m00', 'm20', 'data', 'windows', 'data_info']])
    # * plot the figures
    fig = pygmt.Figure()
    pygmt.config(FONT_LABEL="12p", MAP_LABEL_OFFSET="6p",
                 FONT_ANNOT_PRIMARY="12p", MAP_FRAME_TYPE="plain")

    with fig.subplot(nrows=2, ncols=2, figsize=("8i", "6i"), margins=['0.2i', '0.06i']):
        # * the three frequency bands
        for ifreq, freq in enumerate(freq_list):
            fig.basemap(projection="X?/?", region=[conf["start"], conf["end"], 0, 6],
                        frame=["S", "xaf+lTime(s)"], panel=ifreq+1)
            plot_waveform(fig, prepared_info, freq)
            fig.text(position="TL", text=labels[ifreq],
                     font="10p,Helvetica-Bold,black", offset="j0.1i/0.1i")
            fig.text(position="TL", text=f"({ascii_uppercase[ifreq+1]})",
                     font="15p,Helvetica-Bold,black", offset="j-0.3i/0.2i", no_clip=True)

    # * the basemap
    fig.shift_origin(yshift="3i")
    fig.basemap(region=[95, 165, 10, 56], projection="M3i", frame=[
        "WSen", "xaf", "yaf"])
    plot_base_map(fig)
    fig.plot(data=resource(['stations', 'STATIONS_filtered']),
             style="t0.03i", pen="0.004i,black")  # remove unused stations
    fig.plot(x=116.01, y=29.6474, style="t0.09i",
             pen="0.03i,red")  # station position
    fig.text(position="TL", text=f"200805071602A (Mw 6.2, 21km) [Station:{conf['sta_name']}]",
             font="10p,Helvetica-Bold,black", offset="j0.1i/-0.3i", no_clip=True)
    fig.meca(spec=meca, convention="mt", scale="0.8i")
    fig.text(position="TL", text="(A)",
             font="15p,Helvetica-Bold,black", offset="j-0.3i/-0.3i", no_clip=True)

    # * legend
    fig.shift_origin(xshift="w+0.3i")
    with pygmt.config(MAP_FRAME_PEN="0.0p,white", FONT_ANNOT_PRIMARY="6p"):
        fig.basemap(region=[0, 1, 0, 1],
                    projection="X0.8i/1.6i", frame=["lbrt"])
        fig.legend(spec=arrivals_legend, position="jTL+w1.5c+o1.0c/0.2c")

    save_path(fig, "waveform")


if __name__ == "__main__":
    main()
