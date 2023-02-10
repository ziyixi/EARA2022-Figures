""" 
con_vp_eara2022.py

Plot the con vertical cross-secations.
"""
from functools import partial

from .con_base import con_plot_base

# * configuration for the plotting
conf = {
    "x_offset": 4.7,
    "y_offset": 5.9,
    "yabs_offset": 3,
    "ytopo_offset": 4,
    'parameter': 'vp',
    'cbar': 'Vp',
    'length': 15,
    'abs_cpt': '6.2/8.7/0.5',
    'save_name': "con_vp_eara2022",
    'x_fig': 4.5,
    'ref': 'eara2022',
}

main = partial(con_plot_base, conf=conf)
