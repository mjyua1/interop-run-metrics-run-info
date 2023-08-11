from interop import py_interop_run_metrics, py_interop_run
import datetime
import xml.etree.ElementTree as ET
run_metrics = py_interop_run_metrics.run_metrics()
run_metrics.read(".")
tile_metric = run_metrics.tile_metric_set()

tile_list = []
tiles_list = []
clusters_density = []
clusters_pf = []
clusters_count = []


def getMetrics(run_folder, corrected_end_list, start_cycle_list, end_cycle_list, laneZero, outermost):
    tree = ET.parse(run_folder + "/RunInfo.xml")
    root = tree.getroot()
    run_info = py_interop_run.info()
    run_info.read(run_folder + "/RunInfo.xml")

    error_metrics = run_metrics.error_metric_set()
    q_metric = run_metrics.q_metric_set()

    pfr_dict_0 = {}
    bases_dict_0 = {}
    total_phix_error_rates = {}
    cd_dict_zero = {}
    lane_q30 = 0
    bases_total_zero = 0


    import statistics
    lane_info_list = []

    for read in root.iter("FlowcellLayout"):
        if "LaneCount" in read.attrib:
            lane_count = int(read.attrib["LaneCount"])
            lane_list = list(range(1, lane_count + 1))
            laneZero["lane"] = 0

            for lane in lane_list:
                lane_info = {}
                outermost["run_name"] = run_info.name()
                lane_info["lane"] = lane

                clusters_density = []
                clusters_pf = []
                clusters_count = []
                phix_error_rates = []

                for tileSet in root.iter("TileSet"):
                    for tile_count in tileSet.iter("Tiles"):
                        for tile in tile_count.iter("Tile"):
                            tile_text = tile.text
                            tile_num = tile_text.split("_")[1]
                            tile_list.append(tile_num)
                            lane_num = int(tile_text.split("_")[0])

                            tile_metric = run_metrics.tile_metric_set()
                            cluster_density = tile_metric.get_metric(lane_num, int(tile_num)).cluster_density()
                            cluster_count_pf = tile_metric.get_metric(lane_num, int(tile_num)).cluster_count_pf()
                            cluster_count = tile_metric.get_metric(lane_num, int(tile_num)).cluster_count()

                            if lane == lane_num:
                                clusters_density.append(cluster_density)
                                clusters_pf.append(cluster_count_pf)
                                clusters_count.append(cluster_count)

                dynamic_name = f"cluster_density_{lane}"
                cd_dict_zero[dynamic_name] = sum(clusters_density) / len(clusters_density)

                pass_filter_rate = [a / b for a, b in zip(clusters_pf, clusters_count)]
                average_pfr = sum(pass_filter_rate) / len(pass_filter_rate)

                lane_cluster_pf = sum(clusters_pf)
                lane_cluster_count = sum(clusters_count)
                pass_filter_rate_0 = lane_cluster_pf / lane_cluster_count
                dynamic_name = f"pass_filter_rate_{lane}"
                pfr_dict_0[dynamic_name] = pass_filter_rate_0

                lane_info["cluster_density"] = statistics.mean(clusters_density)
                lane_info["pass_filter_rate"] = average_pfr

                metric_list = []
                q30 = []

                for i in range(q_metric.size()):
                    if q_metric.at(i).lane() == lane and (corrected_end_list[0] > q_metric.at(i).cycle()):
                        metric_list.append(q_metric.at(i).total_over_qscore(q_metric.index_for_q_value(0)))
                        q30.append(q_metric.at(i).total_over_qscore(q_metric.index_for_q_value(30)))
                    elif q_metric.at(i).lane() == lane and (corrected_end_list[-2] < q_metric.at(i).cycle() < corrected_end_list[2]):
                        metric_list.append(q_metric.at(i).total_over_qscore(q_metric.index_for_q_value(0)))
                        q30.append(q_metric.at(i).total_over_qscore(q_metric.index_for_q_value(30)))

                lane_info["bases_total"] = sum(metric_list)
                lane_info["fraction_q30"] = sum(q30) / sum(metric_list)

                dynamic_name_bt = f"bases_total_{lane}"
                lane_base_total = sum(metric_list)
                bases_dict_0[dynamic_name_bt] = lane_base_total
                bases_total_0 = sum(bases_dict_0.values())

                bases_total_zero += sum(metric_list)
                lane_q30 += sum(q30)
                q30_zero = lane_q30 / bases_total_zero

                for i in range(error_metrics.size()):
                    if error_metrics.at(i).lane() == lane and (corrected_end_list[0] > error_metrics.at(i).cycle()):
                        phix_error_rate = error_metrics.at(i).error_rate()
                        phix_error_rates.append(phix_error_rate)
                    elif error_metrics.at(i).lane() == lane and (corrected_end_list[-1] < error_metrics.at(i).cycle() < corrected_end_list[1]):
                        phix_error_rate = error_metrics.at(i).error_rate()
                        phix_error_rates.append(phix_error_rate)

                phix_error_avg = statistics.mean(phix_error_rates)
                lane_info["phix_error_avg"] = phix_error_avg
                current_timestamp = datetime.datetime.now()
                lane_info["last_updated"] = current_timestamp

                dynamic_name_pea = f"phix_error_avg_{lane}"
                total_phix_error_rates[dynamic_name_pea] = phix_error_avg
                lane_info_list.append(lane_info)


            json_map = getJsonMap(run_folder, start_cycle_list, end_cycle_list, laneZero)


    for index, item in enumerate(lane_info_list):
        item["json_map"] = json_map[index]

    json_zero = getJsonZero(run_folder, end_cycle_list, start_cycle_list)

    laneZero["cluster_density"] = statistics.mean(cd_dict_zero.values())
    laneZero["pass_filter_rate"] = statistics.mean(pfr_dict_0.values())
    laneZero["bases_total"] = bases_total_0
    laneZero["fraction_q30"] = q30_zero
    laneZero["phix_error_avg"] = statistics.mean(total_phix_error_rates.values())
    laneZero["last_updated"] = current_timestamp
    laneZero["json_map"] = json_zero

    lane_info_list.insert(0, laneZero)
    outermost["lane"] = lane_info_list

    return outermost


def getJsonMap(run_folder, start_cycle_list, end_cycle_list, laneZero):
    import statistics

    tree = ET.parse(run_folder + "/RunInfo.xml")
    root = tree.getroot()
    error_metrics = run_metrics.error_metric_set()
    q_metric = run_metrics.q_metric_set()

    read_num_list = []
    for child in root.iter("Read"):
        read_number = int(child.attrib.get("Number"))
        read_num_list.append(read_number)
    for read in root.iter("FlowcellLayout"):
        if "LaneCount" in read.attrib:
            lane_count = int(read.attrib["LaneCount"])
            lane_list = list(range(1, lane_count + 1))

    json_map_each_lane_list = []
    for lane in lane_list:
        json_map_read_list = []
        for reads in range(len(read_num_list)):
            json_map_read = {}
            metric_list = []
            q30 = []
            error_rates_in_read = []
            for i in range(error_metrics.size()):
                if error_metrics.at(i).lane() == lane and start_cycle_list[reads] <= error_metrics.at(i).cycle() <= end_cycle_list[reads]:
                    phix_error_rate = error_metrics.at(i).error_rate()
                    error_rates_in_read.append(phix_error_rate)

            if len(error_rates_in_read) > 0:
                mean_error_rate = statistics.mean(error_rates_in_read)
            else:
                mean_error_rate = 0

            if len(error_rates_in_read) > 1:
                stdev_error_rate = statistics.stdev(error_rates_in_read)
            else:
                stdev_error_rate = 0

            error_rate_dict = {"avg": mean_error_rate, "stdev": stdev_error_rate}

            json_map_read["read"] = read_num_list[reads]
            json_map_read["phixError"] = error_rate_dict

            for i in range(q_metric.size()):
                if q_metric.at(i).lane() == lane and start_cycle_list[reads] <= q_metric.at(i).cycle() < end_cycle_list[reads]:
                    metric_list.append(q_metric.at(i).total_over_qscore(q_metric.index_for_q_value(0)))
                    q30.append(q_metric.at(i).total_over_qscore(q_metric.index_for_q_value(30)))

            q30_sum = sum(q30)
            bases_total = sum(metric_list)

            fractionq30 = q30_sum / bases_total
            json_map_read["q30"] = fractionq30

            json_map_read_list.append(json_map_read)

        json_map_read_dict = {"reads": json_map_read_list}

        json_map_each_lane_list.append(json_map_read_dict)

    return json_map_each_lane_list

def getJsonZero(run_folder, end_cycle_list, start_cycle_list):
    import statistics
    tree = ET.parse(run_folder + "/RunInfo.xml")
    root = tree.getroot()
    read_num_list = []
    error_metrics = run_metrics.error_metric_set()
    q_metric = run_metrics.q_metric_set()
    for child in root.iter("Read"):
        read_number = int(child.attrib.get("Number"))
        read_num_list.append(read_number)
    random_list = []
    random_list2 = []
    q30_list = []
    lane_q30 = 0
    bases_total_zero = 0
    total_phix_error_rates = {}
    for read in root.iter("FlowcellLayout"):
        if "LaneCount" in read.attrib:
            lane_count = int(read.attrib["LaneCount"])
            lane_list = list(range(1, lane_count + 1))

    for lane in lane_list:
        for reads in range(len(read_num_list)):
            metric_list = []
            q30 = []
            error_rates_in_read = []
            for i in range(error_metrics.size()):
                if error_metrics.at(i).lane() == lane and start_cycle_list[reads] <= error_metrics.at(i).cycle() <= \
                        end_cycle_list[reads]:
                    phix_error_rate = error_metrics.at(i).error_rate()
                    error_rates_in_read.append(phix_error_rate)
            if len(error_rates_in_read) > 0:
                mean_error_rate = statistics.mean(error_rates_in_read)
            else:
                mean_error_rate = 0

            if len(error_rates_in_read) > 1:
                stdev_error_rate = statistics.stdev(error_rates_in_read)
            else:
                stdev_error_rate = 0


            for i in range(q_metric.size()):
                if q_metric.at(i).lane() == lane and start_cycle_list[reads] <= q_metric.at(i).cycle() < end_cycle_list[reads]:
                    metric_list.append(q_metric.at(i).total_over_qscore(q_metric.index_for_q_value(0)))
                    q30.append(q_metric.at(i).total_over_qscore(q_metric.index_for_q_value(30)))

            bases_total_zero += sum(metric_list)
            lane_q30 += sum(q30)
            q30_zero = lane_q30 / bases_total_zero



            random_list.append(stdev_error_rate)
            random_list2.append(mean_error_rate)
            q30_list.append(q30_zero)

            eachPart1Len = len(random_list) // int(lane)
            eachPart2Len = len(random_list2) // int(lane)
            eachPart30Len = len(q30_list) // int(lane)

    result1 = [random_list[i:i + eachPart1Len] for i in range(0, len(random_list), eachPart1Len)]
    result2 = [random_list2[i:i + eachPart2Len] for i in range(0, len(random_list2), eachPart2Len)]
    result30 = [q30_list[i:i + eachPart30Len] for i in range(0, len(q30_list), eachPart30Len)]

    averages1 = []

    # Use zip to iterate through elements at the same index in each sublist
    for index_values in zip(*result1):
        # Filter out 0 values
        filtered_values = [value for value in index_values if value != 0]
        # Calculate the average for the current index
        avg = sum(filtered_values) / len(filtered_values) if len(filtered_values) > 0 else 0
        # Append the average to the 'averages' list
        averages1.append(avg)

    averages2 = []
    for index_values in zip(*result2):
        # Filter out 0 values
        filtered_values = [value for value in index_values if value != 0]
        # Calculate the average for the current index
        avg = sum(filtered_values) / len(filtered_values) if len(filtered_values) > 0 else 0
        # Append the average to the 'averages' list
        averages2.append(avg)

    averages30 = []
    for index_values in zip(*result30):
        # Filter out 0 values
        filtered_values = [value for value in index_values if value != 0]
        # Calculate the average for the current index
        avg = sum(filtered_values) / len(filtered_values) if len(filtered_values) > 0 else 0
        # Append the average to the 'averages' list
        averages30.append(avg)
    json_map_read_list = []

    for reads in range(len(read_num_list)):
        json_map_zero = {}
        json_map_zero["read"] = read_num_list[reads]
        new_dict = {"avg": averages2[reads], "stdev": averages1[reads]}
        json_map_zero["phixError"] = new_dict
        json_map_zero["q30"] = averages30[reads]

        json_map_read_list.append(json_map_zero)

    json_map_read_dict_zero = {"reads": json_map_read_list}

    return json_map_read_dict_zero

def finalOutput2(run_folder):
    tree = ET.parse(run_folder + "/RunInfo.xml")
    root = tree.getroot()
    cycles_dict = {}
    for child in root.iter("Read"):
        number = child.attrib.get("Number")
        num_cycles = child.attrib.get("NumCycles")
        cycles_dict[number] = num_cycles

    end_cycle = None
    keys_list = [1, -1, -2, 2]
    end_cycle_list = []
    start_cycle_num = 1
    start_cycle_list = []

    for (key, value), key_value in zip(cycles_dict.items(), keys_list):
        if end_cycle is not None:
            start_cycle_num = end_cycle + 1
            end_cycle = start_cycle_num + int(value) - 1
        else:
            start_cycle = 1
            end_cycle = int(value)
        start_cycle_list.append(start_cycle_num)
        end_cycle_list.append(end_cycle)

    indexedList = []
    for read in root.iter("Reads"):
        for indexed in read.iter("Read"):
            if "IsIndexedRead" in indexed.attrib:
                isIndexed = indexed.attrib["IsIndexedRead"]
                indexedList.append(isIndexed)

    corrected_end_list = []
    paired_index_end = zip(end_cycle_list, indexedList)

    for end_cycle, index in paired_index_end:
        if index == 'N':
            corrected_end_list.append(end_cycle)
        else:
            pass
    if len(corrected_end_list) >= 2:
        value_to_insert = end_cycle_list[-2]
        corrected_end_list.append(value_to_insert)
        corrected_end_list.sort()


    laneZero = {}
    outermost = {}

    metrics = getMetrics(run_folder, corrected_end_list, start_cycle_list, end_cycle_list, laneZero, outermost)
    return metrics






