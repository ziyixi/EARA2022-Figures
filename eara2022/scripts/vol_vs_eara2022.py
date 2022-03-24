""" 
vol_vs_eara2022.py

Plot the vol vertical cross-secations.
"""
from functools import partial

from .vol_base import vol_plot_base

# * configuration for the plotting
conf = {
    "x_offset": 7.7,
    "y_offset": 5.475,
    "yabs_offset": 2.9,
    "ytopo_offset": 3.64,
    'parameter': 'vs',
    'cbar': 'Vs',
    'length': 25,
    'abs_cpt': '3.5/4.8/0.3',
    'save_name': "vol_vs_eara2022",
    'x_fig': 7.5,
    'ref': 'eara2022',
}

main = partial(vol_plot_base, conf=conf)
