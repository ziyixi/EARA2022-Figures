"""
changbaishan_models_stw105_vp.py

plot the model comparision figure with stw105 and vp.
"""
from .changbaishan_models_base import plot_base
from functools import partial

conf = {
    "parameter": "vp",
    "ref_key": "stw105",
    "save_name": "changbaishan_models_stw105_vp",
    "colorbar_content": "@[\delta@[ln@[V@[",
}

main = partial(
    plot_base,
    parameter=conf["parameter"],
    ref_key=conf["ref_key"],
    save_name=conf["save_name"],
    colorbar_content=conf["colorbar_content"],
)

if __name__ == "__main__":
    main()
