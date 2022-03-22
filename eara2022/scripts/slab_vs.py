""" 
slab_vs.py

Plot the slab vertical cross-secations.
"""
from functools import partial

from .slab_base import slab_plot_base

# * configuration for the plotting
conf = {
    "x_offset": 7.7,
    "y_offset": 5.9,
    "yabs_offset": 3,
    "ytopo_offset": 4,
    'parameter': 'vs',
    'cbar': 'Vs',
    'length': 25,
    'abs_cpt': '3.5/4.8/0.3',
    'save_name': "slab_vs",
    'x_fig': 7.5
}

main = partial(slab_plot_base, conf=conf)
