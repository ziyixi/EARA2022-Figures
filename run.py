from eara2022.scripts import *
import sys

scripts_mapper = {
    "geo_map": geo_map_main,
    'event_station_distribution': event_station_distribution_main,
    'misfit': misfit_main,
    'hist': hist_main,
    'psf': psf_main,
    'waveform': waveform_main,
    'vs_eara2022': vs_eara2022_main,
    'vs_ak135': vs_ak135_main,
    'vs_stw105': vs_stw105_main,
    'vp_eara2022': vp_eara2022_main,
    'vp_ak135': vp_ak135_main,
    'vp_stw105': vp_stw105_main,
    "vp_vs": vp_vs_main,
    'radial': radial_main,
    'slab_vs_eara2022': slab_vs_eara2022_main,
    'slab_vs_ak135': slab_vs_ak135_main,
    'slab_vs_stw105': slab_vs_stw105_main,
    'slab_vp_eara2022': slab_vp_eara2022_main,
    'slab_vp_ak135': slab_vp_ak135_main,
    'slab_vp_stw105': slab_vp_stw105_main,
    'changbaishan_models_stw105_vs': changbaishan_models_stw105_vs_main,
    'changbaishan_models_stw105_vp': changbaishan_models_stw105_vp_main,
    'changbaishan_models_eara2022_vs': changbaishan_models_eara2022_vs_main,
    'changbaishan_models_eara2022_vp': changbaishan_models_eara2022_vp_main,
    'changbaishan_models_ak135_vs': changbaishan_models_ak135_vs_main,
    'changbaishan_models_ak135_vp': changbaishan_models_ak135_vp_main,
    'con_vs_eara2022': con_vs_eara2022_main,
    'con_vs_ak135': con_vs_ak135_main,
    'con_vs_stw105': con_vs_stw105_main,
    'con_vp_eara2022': con_vp_eara2022_main,
    'con_vp_ak135': con_vp_ak135_main,
    'con_vp_stw105': con_vp_stw105_main,
    'vol_vs_eara2022': vol_vs_eara2022_main,
    'vol_vp_eara2022': vol_vp_eara2022_main,
    'vol_vs_ak135': vol_vs_ak135_main,
    'vol_vp_ak135': vol_vp_ak135_main,
    'vol_vs_stw105': vol_vs_stw105_main,
    'vol_vp_stw105': vol_vp_stw105_main,
    'changbaishan_fwea18_ak135': changbaishan_fwea18_ak135_main,
    'changbaishan_fwea18_iasp91': changbaishan_fwea18_iasp91_main,
    'paraview': paraview_main,
}


def main():
    if len(sys.argv) == 2:
        if sys.argv[1] == "all" or (sys.argv[1] in scripts_mapper):
            if sys.argv[1] != 'all':
                scripts_mapper[sys.argv[1]]()
            else:
                for key in scripts_mapper:
                    print(f"Plot {key} now...")
                    scripts_mapper[key]()
        else:
            raise Exception(f"scripts {sys.argv[1]} is not supported!")
    else:
        raise Exception("correct format: python run.py [script name]")


if __name__ == "__main__":
    main()
