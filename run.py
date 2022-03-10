from eara2022.scripts import *
import sys

scripts_mapper = {
    "geo_map": geo_map_main,
    'event_station_distribution': event_station_distribution_main,
    'misfit': misfit_main,
    'hist': hist_main,
    'psf': psf_main,
    'waveform': waveform_main,
    'vs': vs_main,
    'vp': vp_main
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
