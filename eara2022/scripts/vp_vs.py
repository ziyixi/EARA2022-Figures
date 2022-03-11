""" 
vp_vs.py

plot the horizontal crosssection of the model.
"""
from .vpvs_base import plot_base
from functools import partial
import numpy as np

conf = {
    'model_type': "vp_vs",
    'depths': np.arange(100, 1000, 100),
    'cpt_series': "-0.03/0.03/0.01",
    'cpt_reverse': True,
    'save_name': "vp_vs.pdf",
    'colorbar_content': "@~d@~ln(Vp/Vs)(%)"
}

main = partial(plot_base, model_type=conf['model_type'], depths=conf['depths'], cpt_series=conf['cpt_series'],
               cpt_reverse=conf['cpt_reverse'], save_name=conf['save_name'], colorbar_content=conf['colorbar_content'])

if __name__ == "__main__":
    main()
