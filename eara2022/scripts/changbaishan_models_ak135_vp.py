"""
changbaishan_models_ak135_vp.py

plot the model comparision figure with ak135 and vp.
"""
from .changbaishan_models_base import plot_base
from functools import partial

conf = {
    'parameter': "vp",
    'ref_key': "ak135",
    'save_name': "changbaishan_models_ak135_vp",
    'colorbar_content': "@~d@~lnV(%)",
}

main = partial(plot_base, parameter=conf['parameter'],
               ref_key=conf['ref_key'], save_name=conf['save_name'], colorbar_content=conf['colorbar_content'])

if __name__ == "__main__":
    main()
