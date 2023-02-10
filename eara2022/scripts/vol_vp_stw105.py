""" 
vol_vp_stw105.py

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
    'parameter': 'vp',
    'cbar': 'Vp',
    'length': 25,
    'abs_cpt': '6.2/8.7/0.5',
    'save_name': "vol_vp_stw105",
    'x_fig': 7.5,
    'ref': 'stw105',
}

main = partial(vol_plot_base, conf=conf)
