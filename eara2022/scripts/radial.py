""" 
radial.py

plot the horizontal crosssection of the model.
"""
from functools import partial

import numpy as np

from .vpvs_base import plot_base

conf = {
    "model_type": "radial",
    "depths": np.arange(100, 700, 100),
    "cpt_series": "-0.03/0.03/0.01",
    "cpt_reverse": False,
    "save_name": "radial",
    "colorbar_content": "@[(V_{SH}-V_{SV}/V_S)@[",
}

main = partial(
    plot_base,
    model_type=conf["model_type"],
    depths=conf["depths"],
    cpt_series=conf["cpt_series"],
    cpt_reverse=conf["cpt_reverse"],
    save_name=conf["save_name"],
    colorbar_content=conf["colorbar_content"],
)

if __name__ == "__main__":
    main()
