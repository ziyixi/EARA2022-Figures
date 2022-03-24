""" 
con_vs_stw105.py

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
    'parameter': 'vs',
    'cbar': 'Vs',
    'length': 15,
    'abs_cpt': '3.5/4.8/0.3',
    'save_name': "con_vs_stw105",
    'x_fig': 4.5,
    'ref': 'stw105',
}

main = partial(con_plot_base, conf=conf)
