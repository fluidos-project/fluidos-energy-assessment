import matplotlib.pyplot as plt
from datetime import datetime
import pandas as pd
import numpy as np

report_directory = "../Measures/SmartPlug/data-server-crownlabs"

def read_load_events(filepath):
    samples = []
    with open(filepath, 'r') as fileRead:
        data = fileRead.readlines()
        for line in data:
            if "#how" in line:
                continue

            sample = {}
            sample["start"] = datetime.fromtimestamp(int(line.split(" ")[0]))
            sample["load"] = float(line.split(" ")[1])
            sample["score"] = float(line.split(" ")[2])
            sample["end"] = datetime.fromtimestamp(int(line.split(" ")[3]))
            samples.append(sample)

    return samples

def read_resource_usage(filename):
    samples = []
    with open(filename, 'r') as fileRead:
        data = fileRead.readlines()
        timestamp = 0
        for line in data:
            if "#how" in line:
                continue
            if "###" in line:
                timestamp = line.split(" ")[1]
                continue
            sample = {}
            sample["time"] = datetime.fromtimestamp(int(timestamp))
            sample["pid"] = int(line.split(" ")[0])
            sample["process"] = line.split(" ")[1]
            sample["usage"] = float(line.split(" ")[2].replace(",", "."))
            samples.append(sample)

    return samples

def read_power_consumption_csv(filename):
    data = pd.read_csv(filename)
    samples_powertop = []
    samples_smartplug = []
    del data["Time"]
    #del data["docker cpu usage"]

    data = data.reset_index()  # make sure indexes pair with number of rows
    for index , row in data.iterrows():
        sample_powertop = {}
        sample_smartplug = {}

        sample_powertop["time"] = datetime.fromtimestamp(row["timestamp"])
        sample_smartplug["time"] = datetime.fromtimestamp(row["timestamp"])
        #sample_powertop["usage"] = row["powertop measure"]
        sample_smartplug["usage"] = row["smart plug measure"]
        samples_powertop.append(sample_powertop)
        samples_smartplug.append(sample_smartplug)
    
    return samples_powertop, samples_smartplug

def read_docker_resource_usage(filename):
    data = pd.read_csv(filename)
    samples = []
    del data["Time"]
    #del data["powertop measure"]
    del data["smart plug measure"]

    data = data.reset_index()  # make sure indexes pair with number of rows
    for index , row in data.iterrows():
        sample = {}
        sample["time"] = datetime.fromtimestamp(row["timestamp"])
        sample["usage"] = row["docker cpu usage"]/8
        samples.append(sample)

    return samples

#def read_docker_resource_usage(filename):
#    samples = []
#    with open(filename, 'r') as fileRead:
#        data = fileRead.readlines()
#        for line in data:
#            if "#how" in line:
#                continue
#            
#            sample = {}
#            sample["time"] = datetime.fromtimestamp(int(line.split(" ")[0]))
#            sample["usage"] = 0
#
#            if line.split(" ")[1] != "\n":
#                #print(len(line.split(" ")))
#                sample["usage"] = float(line.split(" ")[1])/8 # TODO: mettere in modo dinamico
#
#            samples.append(sample)
#
#    return samples

def convert_float(element):
    try:
        float(element)
        return float(element)
    except ValueError:
        return 0

def read_power_consumption(filename):
    samples = []
    with open(filename, 'r') as fileRead:
        data = fileRead.readlines()
        for line in data:
            if "#how" in line:
                continue
            
            sample = {}
            sample["time"] = datetime.fromtimestamp(int(line.split(" ")[0]))
            sample["usage"] = 0

            if line.split(" ")[3] == "W":
                sample["usage"] = convert_float(line.split(" ")[2])
            elif line.split(" ")[3] == "mW":
                sample["usage"] = convert_float(line.split(" ")[2])/1000

            samples.append(sample)

    return samples

def aggregate_resource_usage(data):
    result = []
    last_timestamp = 0

    if len(data) > 1:
        last_timestamp = data[0]["time"]
    else:
        print("no available data for resource usage")
        exit(-1)

    cumulative_load = 0
    processed_samples = 0
    for d in data:
        processed_samples = processed_samples + 1

        if last_timestamp != d["time"] or processed_samples == len(data):
            r = {}
            r["time"] = last_timestamp
            r["usage"] = float(cumulative_load)/8 # TODO: mettere questo numero in modo dinamico
            result.append(r)
            last_timestamp = d["time"]
            cumulative_load = d["usage"]
        else:
            cumulative_load = cumulative_load + d["usage"]

    return result

def compute_percentile_data(data, load_events, percentile):
    p_data = []
    x_values = []

    for event in load_events:
        x_values.append(event["load"])
        start_event = event["start"]
        end_event = event["end"]
        val = []

        for d in data:
            if d["time"] > start_event and d["time"] < end_event:
                val.append(d["usage"])
        
        val_np = np.array(val) 
        p_data.append(np.percentile(val_np, percentile))
    
    return x_values, p_data

def compute_load_average_data(data1, load_events):
    avg_data1 = []
    x_values = []
    for event in load_events:
        x_values.append(event["start"])

        start_event = event["start"]
        end_event = event["end"]

        sum = 0.0
        count = 0.0
        for d in data1:
            if d["time"] > start_event and d["time"] < end_event:
                count = count + 1
                sum = sum + d["usage"]

        if count > 0:
            avg_data1.append(sum/count)

    return x_values, avg_data1


def plot_averaged_monitored_cpu_usage(data1, data2, load_events):
    x_values, avg_data1 = compute_load_average_data(data1, load_events)
    _, avg_data2 = compute_load_average_data(data2, load_events)

    fig, ax = plt.subplots()

    ax.plot(x_values, avg_data1, label="top command")
    ax.plot(x_values, avg_data2, label="docker stats")

    ax.legend()
    ax.set_xlabel("Time")
    ax.set_ylabel("CPU load (%)")

    fig.savefig("../data/plot/CPU_load.png")
    plt.close(fig)

def plot_power_consumption(core_consumption, device_consumption, load_events):
    #x_val, core_cons = compute_percentile_data(core_consumption, load_events, 85) 
    x_val, dev_cons = compute_percentile_data(device_consumption, load_events, 85) 

    print(x_val)
    #print(core_cons)
    print(dev_cons)


def plot_power_consumption_on_load(data1, data2, data3, load, load_events):
    width = .75

    _, avg_data1 = compute_load_average_data(data1, load_events)
    _, avg_data2 = compute_load_average_data(data2, load_events)
    _, avg_data3 = compute_load_average_data(data3, load_events)
    #_, x_values = compute_load_average_data(load, load_events)

    x_values = []
    for event in load_events:
        x_values.append(event["load"])

    x_values = [str(i) for i in x_values]
    fig, ax = plt.subplots()

    ax.bar(x_values, avg_data3, width, label="DRAM")
    ax.bar(x_values, avg_data1, width, bottom=avg_data3, label="cpu core")
    ax.bar(x_values, avg_data2, width, bottom=avg_data1, label="cpu misc")

    ax.legend()
    ax.set_xlabel("Assigned CPU cores")
    ax.set_ylabel("Power consumption (W)")

    fig.savefig("../data/plot/Power_consumption.png")
    plt.close(fig)
        
def plot_cpu_efficiency(load, load_events):
    x_values = []
    for event in load_events:
        x_values.append(event["load"])

    x_values = [str(i) for i in x_values]
    y_values = [i["score"] for i in load_events]

    print(y_values)

    fig, ax1 = plt.subplots()

    ax1.bar(x_values, y_values)

    ax1.set_xlabel("Assigned CPU cores")
    ax1.set_ylabel("Passmark Score")

    fig.tight_layout()

    fig.savefig("/".join([report_directory, "plot/CPU_score.png"]))
    plt.close(fig)

def load_cpu_scores(load_events):
    result = {}
    result_normalized = {}
    for event in load_events:
        sub_name = str(int(event["load"]))

        with open("/".join([report_directory, 'results_cpu_' + sub_name + ".yml"]), 'r') as fileRead:
            data = fileRead.readlines()
            for line in data:
                if "CPU_INTEGER_MATH" in line:
                    if "CPU_INTEGER_MATH" not in result:
                        result["CPU_INTEGER_MATH"] = []
                    result["CPU_INTEGER_MATH"].append(float(line.split(":")[1]))
                elif "CPU_FLOATINGPOINT_MATH" in line:
                    if "CPU_FLOATINGPOINT_MATH" not in result:
                        result["CPU_FLOATINGPOINT_MATH"] = []
                    result["CPU_FLOATINGPOINT_MATH"].append(float(line.split(":")[1]))
                elif "CPU_PRIME" in line:
                    if "CPU_PRIME" not in result:
                        result["CPU_PRIME"] = []
                    result["CPU_PRIME"].append(float(line.split(":")[1]))
                elif "CPU_SORTING" in line:
                    if "CPU_SORTING" not in result:
                        result["CPU_SORTING"] = []
                    result["CPU_SORTING"].append(float(line.split(":")[1]))
                elif "CPU_ENCRYPTION" in line:
                    if "CPU_ENCRYPTION" not in result:
                        result["CPU_ENCRYPTION"] = []
                    result["CPU_ENCRYPTION"].append(float(line.split(":")[1]))
                elif "CPU_COMPRESSION" in line:
                    if "CPU_COMPRESSION" not in result:
                        result["CPU_COMPRESSION"] = []
                    result["CPU_COMPRESSION"].append(float(line.split(":")[1]))
                elif "CPU_SINGLETHREAD" in line:
                    if "CPU_SINGLETHREAD" not in result:
                        result["CPU_SINGLETHREAD"] = []
                    result["CPU_SINGLETHREAD"].append(float(line.split(":")[1]))
                elif "CPU_PHYSICS" in line:
                    if "CPU_PHYSICS" not in result:
                        result["CPU_PHYSICS"] = []
                    result["CPU_PHYSICS"].append(float(line.split(":")[1]))
                elif "CPU_MATRIX_MULT_SSE" in line:
                    if "CPU_MATRIX_MULT_SSE" not in result:
                        result["CPU_MATRIX_MULT_SSE"] = []
                    result["CPU_MATRIX_MULT_SSE"].append(float(line.split(":")[1]))
                elif "CPU_mm" in line:
                    if "CPU_mm" not in result:
                        result["CPU_mm"] = []
                    result["CPU_mm"].append(float(line.split(":")[1]))
                elif "CPU_sse" in line:
                    if "CPU_sse" not in result:
                        result["CPU_sse"] = []
                    result["CPU_sse"].append(float(line.split(":")[1]))
                elif "CPU_fma" in line:
                    if "CPU_fma" not in result:
                        result["CPU_fma"] = []
                    result["CPU_fma"].append(float(line.split(":")[1]))
                elif "CPU_avx:" in line:
                    if "CPU_avx:" not in result:
                        result["CPU_avx:"] = []
                    result["CPU_avx:"].append(float(line.split(":")[1]))
                elif "m_CPU_enc_SHA" in line:
                    if "m_CPU_enc_SHA" not in result:
                        result["m_CPU_enc_SHA"] = []
                    result["m_CPU_enc_SHA"].append(float(line.split(":")[1]))
                elif "m_CPU_enc_AES" in line:
                    if "m_CPU_enc_AES" not in result:
                        result["m_CPU_enc_AES"] = []
                    result["m_CPU_enc_AES"].append(float(line.split(":")[1]))
                elif "m_CPU_enc_ECDSA" in line:
                    if "m_CPU_enc_ECDSA" not in result:
                        result["m_CPU_enc_ECDSA"] = []
                    result["m_CPU_enc_ECDSA"].append(float(line.split(":")[1]))

    for key in result:
        if key not in result_normalized:
            result_normalized[key] = []
        
        max = 0
        for val in result[key]:
            if val > max:
                max = val

        for val in result[key]:
            result_normalized[key].append(val/max)

    return result_normalized

def plot_cpu_scores(load, load_events):
    #_, x_values = compute_load_average_data(load, load_events)
    #x_values = [str(int(i)) for i in x_values]

    x_values = []
    for event in load_events:
        x_values.append(event["load"])

    x_values = [str(i) for i in x_values]

    scores = load_cpu_scores(load_events)

    fig, ax = plt.subplots()
    
    for key in scores:
        ax.plot(x_values, scores[key], label=key.replace(":", ""))

    # Shrink current axis's height by 10% on the bottom
    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * 0.1,
                    box.width, box.height * 0.9])

    handles, labels = ax.get_legend_handles_labels()
    lgd = ax.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5,1.35), fancybox=True, shadow=True, ncol=4)

    ax.set_xlabel("Assigned CPU cores")
    ax.set_ylabel("Normalized Passmark score")

    fig.savefig("/".join([report_directory, "plot/CPU_scores.png"]), bbox_extra_artists=(lgd,), bbox_inches='tight')
    plt.close(fig)

def plot_load_consumption_dispersion(load, consumption):
    result = []
    cumulative_load = 0
    count_load = 0
    last_load_minute = 0
    if len(load) > 0:
        last_load_minute = load[0]["time"].minute
    else:
        exit(-1)

    for l in load:
        if l["time"].minute == last_load_minute and l["time"] != load[len(load)-1]["time"]:
            cumulative_load = cumulative_load + l["usage"]
            count_load = count_load + 1
        elif l["time"].minute != last_load_minute or l["time"] == load[len(load)-1]["time"]:
            cumulative_consumption = 0
            count_consumption = 0

            for c in consumption:
                if c["time"].minute == last_load_minute:
                    cumulative_consumption = cumulative_consumption + c["usage"]
                    count_consumption = count_consumption + 1

            r = {}
            if count_load > 0:
                r["load"] = cumulative_load/count_load
            else:
                r["load"] = 0
            if count_consumption > 0:
                r["consumption"] = cumulative_consumption/count_consumption
            else:
                r["consumption"] = 0

            result.append(r)

            last_load_minute = l["time"].minute
            cumulative_load = l["usage"]
            count_load = 1

    x_values = []
    y_values = []

    for r in result:
        x_values.append(r["load"])
        y_values.append(r["consumption"])

    fig, ax = plt.subplots()

    ax.plot(x_values, y_values, 'o')

    ax.set_xlabel("CPU load (%)")
    ax.set_ylabel("Power consumption (W)")

    fig.savefig("../data/plot/Load_Consumption_scatter.png")
    plt.close(fig)
    
def plot_score_on_assigned_resources(load_events):
    x_values = []
    y_values = []
    for event in load_events:
        x_values.append(event["load"])
        y_values.append(event["score"])

    fig, ax = plt.subplots()
    ax.plot(x_values, y_values)
    ax.set_xlabel("CPU core assigned")
    ax.set_ylabel("Passmark score")
    fig.savefig("../data/plot/Passmark_score.png")
    plt.close(fig)

def plot_load_on_assigned_resources(load, load_events):
    x_values = []
    for event in load_events:
        x_values.append(event["load"])

    _, y_values = compute_load_average_data(load, load_events)

    fig, ax = plt.subplots()
    ax.plot(x_values, y_values)
    ax.set_xlabel("CPU core assigned")
    ax.set_ylabel("Measured CPU Load (%)")
    fig.savefig("../data/plot/Measured_CPU_load_on_assigned_resources.png")
    plt.close(fig)
    



if __name__ == "__main__":
    load_events = read_load_events("/".join([report_directory, "load_events"]))
    #memory_usage = read_resource_usage("../data/memory_usage")
    #cpu_usage = read_resource_usage("/".join([report_directory, "Prometheus_results.csv"]))
    #cpu_usage_docker_aggregated = read_docker_resource_usage("/".join([report_directory, "Prometheus_results.csv"]))
    #cpu_core_consumption = read_power_consumption("../data/cpu_core_consumption")
    #cpu_misc_consumption = read_power_consumption("../data/cpu_misc_consumption")
    #memory_consumption = read_power_consumption("../data/memory_consumption")
    cpu_consumption, system_consumption = read_power_consumption_csv("/".join([report_directory, "Prometheus_results.csv"]))
#
    ##print(cpu_core_consumption)
#
    #cpu_usage_aggregated = aggregate_resource_usage(cpu_usage)
#
#
    left  = 0.125  # the left side of the subplots of the figure
    right = 0.9    # the right side of the subplots of the figure
    bottom = 0.2   # the bottom of the subplots of the figure
    top = 0.9      # the top of the subplots of the figure
    wspace = 0.3   # the amount of width reserved for blank space between subplots
    hspace = 0.3   # the amount of height reserved for white space between subplots
    plt.subplots_adjust(left=left, bottom=bottom, right=right, top=top, wspace=wspace, hspace=hspace)
#
    #plot_power_consumption_on_load(cpu_core_consumption, cpu_misc_consumption, memory_consumption, cpu_usage_aggregated, load_events)
    plot_cpu_efficiency([], load_events)
    #plot_cpu_scores([], load_events)
    plot_power_consumption(cpu_consumption, system_consumption, load_events)
    #plot_averaged_monitored_cpu_usage(cpu_usage_aggregated, cpu_usage_docker_aggregated, load_events)
    #plot_load_consumption_dispersion(cpu_usage_aggregated, cpu_core_consumption)
    ##plot_score_on_assigned_resources(load_events)
    #plot_load_on_assigned_resources(cpu_usage_aggregated, load_events)
    