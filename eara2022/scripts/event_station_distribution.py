"""
Plot the events and stations' distribution.
"""
import pygmt
from eara2022 import resource, save_path
from eara2022.utils import asia_countries, generate_tmp_file
from eara2022.utils.gcmt import collect_gcmt_information, gcmt_to_psmeca

# * events cpt
events_cpt_content = """
0 red 70 red
70 green 150 green
150 blue 300 blue
300 orange 700 orange
"""
cpt_file_meca = generate_tmp_file(events_cpt_content, suffix='.cpt')

# * stations cpt
stations_cpt_content = """
0 red
1 purple
2 blue
3 chocolate
4 green4
5 green1
6 cyan
7 black
"""
cpt_file_stations = generate_tmp_file(stations_cpt_content, suffix='.cpt')

# * events legend
events_legend_content = """
S 0.1c kmeca 15p red 0.5p,black 0.66c   0 - 70 km
S 0.1c kmeca 15p green 0.5p,black 0.66c 70 - 150 km
S 0.1c kmeca 15p blue 0.5p,black 0.66c 150 - 300 km
S 0.1c kmeca 15p orange 0.5p,black 0.66c 300 - 700 km
"""
events_legend = generate_tmp_file(events_legend_content)

# * stations legend
stations_legend_content = """
S 0.1c t 12p red 1p 0.36c CEArray
S 0.1c t 12p purple 1p 0.36c F-net
S 0.1c t 12p blue 1p 0.36c KMA Network
S 0.1c t 12p chocolate 1p 0.36c Central Mongolia
S 0.1c t 12p - - 0.36c Seismic Experiment
S 0.1c t 12p green4 1p 0.36c NCISP7
S 0.1c t 12p green1 1p 0.36c NECESSArray
S 0.1c t 12p cyan 1p 0.36c INDEPTH IV
S 0.1c t 12p black 1p 0.36c Data obstained from
S 0.1c t 12p - - 0.36c IRIS DMC
"""
stations_legend = generate_tmp_file(stations_legend_content)

# * gcmt
gcmt_dir = resource('cmt', normal_path=True)


def plot_base_map(fig: pygmt.Figure) -> None:
    countries = asia_countries()
    fig.coast(water="white", resolution="l", land="GRAY81",
              dcw=f"{countries}+p0.8p,white", lakes=["GRAY81"])
    fig.plot(data=resource(['boundary', 'CN-border-L1.dat']), pen="0.8p,white")
    fig.plot(data=resource(
        ['Plate_Boundaries', 'nuvel1_boundaries']), pen="2p,black")
    for slab in ['izu', 'kur', 'phi', 'ryu', 'man']:
        fig.grdcontour(
            resource(['slab2', f'{slab}_slab2_depth.grd']), interval=100, pen="1p,magenta")
    fig.plot(x=[91.3320117152011, 144.284491292185, 174.409435753150, 74.6060844556399, 91.3320117152011], y=[
             9.37366242174489, 2.08633373396527, 48.6744705245903, 61.1396992149365, 9.37366242174489], pen="2p,navyblue")


def main():
    fig = pygmt.Figure()
    pygmt.config(FONT_LABEL="14p", MAP_LABEL_OFFSET="8p", FONT_ANNOT_PRIMARY="12p",
                 MAP_FRAME_TYPE="plain", MAP_TITLE_OFFSET="8p", FONT_TITLE="14p,black", MAP_FRAME_PEN="1p,black")

    # * lower
    with fig.subplot(nrows=1, ncols=4, figsize=("17.5i", "3i"), autolabel="c)", sharey='l', sharex='b', margins=['0.15i', '0i'], frame=["WSen", "xaf", "yaf"]):
        hist_dict = collect_gcmt_information(gcmt_dir)
        # event time
        fig.histogram(data=hist_dict['time'], series=1, pen="1p",  frame=['yaf+l"Number of events"', "xa3yf1y",
                      "WSen+tYear"], region=[2008, 2019, 0, 30], fill="lightblue", center=False, projection="X?/?", panel=0)
        fig.histogram(data=hist_dict['mw'], series=0.1, pen="1p",  frame=[
                      "yaf", 'xaf', "WSen+tMw"], region=[5, 7, 0, 25], fill="lightblue", center=False, projection="X?/?", panel=1)
        fig.histogram(data=hist_dict['depth'], series=50, pen="1p",  frame=[
                      "yaf", 'xaf', 'WSen+t"Depth(km)"'], region=[0, 700, 0, 80], fill="lightblue", center=False, projection="X?/?", panel=2)
        fig.histogram(data=hist_dict['hd'], series=0.25, pen="1p",  frame=[
                      "yaf", 'xaf', 'WSen+t"Half Duration(s)"'], region=[1, 7, 0, 25], fill="lightblue", center=False, projection="X?/?", panel=3)

    # * upper
    fig.shift_origin(yshift="h+1i")
    with fig.subplot(nrows=1, ncols=2, figsize=("14i", "6i"), autolabel="a)", sharey='l', sharex='b', margins=['0.1i', '0i'], frame=["WSen", "xaf", "yaf"]):
        # * event map
        fig.basemap(region=[70, 160, 0, 62], projection="M?", panel=0)
        # boundaries
        plot_base_map(fig)
        events = gcmt_to_psmeca(gcmt_dir)
        fig.meca(events, convention="mt", scale="12p",
                 M=True, C=cpt_file_meca)

        # station map
        fig.basemap(region=[70, 160, 0, 62], projection="M?", panel=1)
        plot_base_map(fig)
        fig.plot(data=resource(['stations', 'STATIONS_filtered']),
                 style="t0.2c", cmap=cpt_file_stations)  # remove unused stations

    # * legend
    fig.shift_origin(xshift="w+0.5i")
    with pygmt.config(MAP_FRAME_PEN="0.0p,white", FONT_ANNOT_PRIMARY="18p"):
        fig.basemap(region=[0, 1, 0, 1],
                    projection="X3i/5.5i", frame=["lbrt"])
        fig.legend(spec=events_legend, position="jTL+w1.5c+o0.2c/0.2c")
        fig.basemap(region=[0, 1, 0, 1],
                    projection="X3i/3.5i", frame=["lbrt"])
        fig.legend(spec=stations_legend, position="jTL+w1.5c+o0.2c/0.2c")

    fig.savefig(save_path("event_station_distribution.pdf"))


if __name__ == "__main__":
    main()
