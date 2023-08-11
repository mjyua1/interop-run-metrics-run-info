import xml.etree.ElementTree as ET
import datetime
import json
from interop import py_interop_run


def find_basic_metrics(run_folder):
    try:
        run_info = py_interop_run.info()
        run_info.read(run_folder + "/RunInfo.xml")
        date_string = run_info.date()
        timestamp = datetime.datetime.strptime(date_string, "%m/%d/%Y  %I:%M:%S %p")

        tree = ET.parse(run_folder + "/RunInfo.xml")
        root = tree.getroot()

        lane_count = None
        for read in root.iter("FlowcellLayout"):
            if "LaneCount" in read.attrib:
                lane_count = int(read.attrib["LaneCount"])
                break
        if lane_count is not None:
            print(f"Lane count: {lane_count}")
        else:
            print("Lane count not found in the XML.")

        tile_count = None
        for read in root.iter("FlowcellLayout"):
            if "TileCount" in read.attrib:
                tile_count = int(read.attrib["TileCount"])
                break
        if tile_count is not None:
            print(f"TileCount: {tile_count}")
        else:
            print("Tile count not found in the XML.")

        current_timestamp = datetime.datetime.now()

        json_value1 = {
            "run_name": run_info.name(),
            "date": timestamp,
            "flowcell": run_info.flowcell_id(),
            "instrument": run_info.instrument_name(),
            "run_number": run_info.run_number(),
            "lane_count": lane_count,
            "tile_count": tile_count,
            "data_path": run_folder,
            'cycle_count': run_info.total_cycles(),
            "last_updated": current_timestamp
        }

        tree = ET.parse(run_folder + "/RunParameters.xml")
        root = tree.getroot()
        for child in root.iter():
            if child.tag == "ExperimentName":
                json_value1["experiment_name"] = child.text
                break
        if "experiment_name" in json_value1:
            print(f"ExperimentName: {json_value1['experiment_name']}")
        else:
            print("ExperimentName not found in the XML.")
        return json_value1
    except Exception as e:
        print("Error processing run:", str(e))
        return {}  # Return an empty dictionary if there's an error


def find_children_with_tag(node, tag):
    tags_list = ["Build", "ReadType", "BaseSpaceRunId", "PlatformType", "UcsRunId", "Version", "Barcode"]
    json_value3 = []
    if any(node.tag.endswith(tag) for tag in tags_list):
        if "\n" not in node.text:
            json_value3.append({node.tag: node.text})
    for child in node:
        json_value3.extend(find_children_with_tag(child, tag))
    return json_value3




