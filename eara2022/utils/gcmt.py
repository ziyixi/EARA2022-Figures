""" 
gcmt.py

handle gcmt related problems
"""
from os.path import join
from typing import List

import numpy as np
import obspy
from eara2022 import gmt_path
from numpy.typing import NDArray

from . import generate_tmp_file


def gcmt_to_psmeca(gcmt_dir: str, has_text: bool = False) -> str:
    """Generate gcmt temp file for psmeca plotting

    Args:
        gcmt_dir (str): gcmt files directory
        has_text (bool): if annotate texts

    Returns:
        str: the temp psmeca plotting path, wrapped as gmt_path
    """
    def get_tensor_dict(files: List[str]) -> dict:
        result = {}
        for item in obspy.read_events(files):
            id = item.origins[0].resource_id.id.split("/")[2]
            tensor = item.focal_mechanisms[0].moment_tensor.tensor
            latitude = item.origins[0].latitude
            longitude = item.origins[0].longitude
            depth = item.origins[0].depth
            result[id] = (tensor, longitude, latitude, depth)
        return result

    def split_tensor_exponent(tensor):
        result = {}
        search_list = np.array(
            [tensor.m_rr, tensor.m_tt, tensor.m_pp, tensor.m_rt, tensor.m_rp, tensor.m_tp])
        search_list = np.abs(search_list)
        ref = np.min(search_list)

        exp = len(str(int(ref)))-1
        result = {
            "m_rr": tensor.m_rr/(10**exp),
            "m_tt": tensor.m_tt/(10**exp),
            "m_pp": tensor.m_pp/(10**exp),
            "m_rt": tensor.m_rt/(10**exp),
            "m_rp": tensor.m_rp/(10**exp),
            "m_tp": tensor.m_tp/(10**exp),
            "exp": exp
        }
        return result

    tensor_dict = get_tensor_dict(join(gcmt_dir, "*"))
    tmp_file = generate_tmp_file()
    with open(tmp_file, "w") as f:
        for key in tensor_dict:
            item, longitude, latitude, depth = tensor_dict[key]
            tensor = split_tensor_exponent(item)
            if(has_text):
                f.write(
                    f'{longitude} {latitude} {depth/1000:.2f} {tensor["m_rr"]:.3f} {tensor["m_tt"]:.3f} {tensor["m_pp"]:.3f} {tensor["m_rt"]:.3f} {tensor["m_rp"]:.3f} {tensor["m_tp"]:.3f} {tensor["exp"]} 0 0 {key}\n')
            else:
                f.write(
                    f'{longitude} {latitude} {depth/1000:.2f} {tensor["m_rr"]:.3f} {tensor["m_tt"]:.3f} {tensor["m_pp"]:.3f} {tensor["m_rt"]:.3f} {tensor["m_rp"]:.3f} {tensor["m_tp"]:.3f} {tensor["exp"]} 0 0 \n')

    # the path is always used in gmt script
    return gmt_path(tmp_file)


def collect_gcmt_information(gcmt_dir: str) -> dict[str, NDArray]:
    """Collect source information

    Args:
        gcmt_dir (str): the gcmt directory

    Returns:
        NDArray: an numpy array with the information of time, mw, depth, half_duration, in str format
    """
    all_events = obspy.read_events(join(gcmt_dir, "*"))
    eventtime_list = []
    mw_list = []
    depth_list = []
    hd_list = []
    for each_event in all_events:
        origin = each_event.preferred_origin()
        eventtime_list.append(origin.time.datetime.year)
        mw_list.append(each_event.magnitudes[0].mag)
        depth_list.append(origin.depth/1000)
        hd_list.append(
            each_event.focal_mechanisms[0].moment_tensor.source_time_function.duration/2)
    res = {
        "time": np.array(eventtime_list),
        "mw": np.array(mw_list),
        "depth": np.array(depth_list),
        "hd": np.array(hd_list)
    }
    return res
