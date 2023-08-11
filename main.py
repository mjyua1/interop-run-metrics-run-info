from parser import *


def finalOutput(run_folder):
    json_value1 = find_basic_metrics(run_folder)
    root = ET.parse(run_folder + "/RunParameters.xml").getroot()

    tags_list = ["Build", "ReadType", "BaseSpaceRunId", "PlatformType", "UcsRunId", "Version", "Barcode"]
    json_value3 = {}
    for tag_item in tags_list:
        tag = tag_item
        tag_items = find_children_with_tag(root, tag)
        for item in tag_items:
            json_value3.update(item)
    tree = ET.parse(run_folder + "/RunInfo.xml")
    root = tree.getroot()

    reads_dict = {}
    for child in root.iter("Read"):
        number = child.attrib.get("Number")
        num_cycles = child.attrib.get("NumCycles")
        reads_dict[number] = num_cycles

    keys_list = [1, -1, -2, 2]
    json_value3["Reads:"] = []  # Create an empty list to hold the read information

    end_cycle = None
    start_cycle = 1

    for (key, value), key_value in zip(reads_dict.items(), keys_list):
        if end_cycle is not None:
            start_cycle = end_cycle + 1
            end_cycle = start_cycle + int(value) - 1
        else:
            start_cycle = 1
            end_cycle = int(value)

        json_value3["Reads:"].append({
            "Read": str(key_value).strip(),
            "Start Cycle": str(start_cycle).strip(),
            "End Cycle": str(end_cycle).strip()
        })

    combined_output = {**json_value1, "JSON_map": json_value3}
    # file_path = "/Users/MichelleJYuan/Desktop/ITP449Spring23/interop/run_folder/run_info.json"
    # with open(file_path, 'w') as f:
    #     json.dump(combined_output, f, indent=4)
    # print("JSON file created:", file_path)
    return combined_output

