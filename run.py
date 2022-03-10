from eara2022.scripts import *
import sys

scripts_mapper = {
    "geo_map": geo_map_main,
    'event_station_distribution': event_station_distribution_main,
    'misfit': misfit_main,
    'hist': hist_main,
    'psf': psf_main,
    'waveform': waveform_main,
    'vs': vs_main
}


def main():
    if len(sys.argv) == 2:
        if sys.argv[1] in scripts_mapper:
            scripts_mapper[sys.argv[1]]()
        else:
            raise Exception(f"scripts {sys.argv[1]} is not supported!")
    else:
        raise Exception("correct format: python run.py [script name]")


if __name__ == "__main__":
    main()
