
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import tikzplotlib


bare_metal_results_directory = "../data/data_bare_metal"
docker_results_directory = "../data/data_docker"
base_directory = "../data"

def read_passmark_score():
    file_path = "/".join([bare_metal_results_directory, "load_events"])
    with open(file_path, 'r') as fileRead:
        data = fileRead.readlines()
        samples_bare = []
        for line in data:
            if "#how" in line:
                continue

            sample = {}
            sample["start"] = int(line.split(" ")[0])
            sample["load"] = float(line.split(" ")[1])
            sample["score"] = float(line.split(" ")[2])
            sample["end"] = int(line.split(" ")[3])
            samples_bare.append(sample)

    file_path = "/".join([docker_results_directory, "load_events"])
    with open(file_path, 'r') as fileRead:
        data = fileRead.readlines()
        samples_docker = []
        for line in data:
            if "#how" in line:
                continue

            sample = {}
            sample["start"] = int(line.split(" ")[0])
            sample["load"] = float(line.split(" ")[1])
            sample["score"] = float(line.split(" ")[2])
            sample["end"] = int(line.split(" ")[3])
            samples_docker.append(sample)

    return pd.DataFrame(samples_bare), pd.DataFrame(samples_docker)

def compute_power_consumption(score_bare, score_docker):
    bare_consumption = []
    docker_consumption = []

    consumption_path = "/".join([base_directory, "Consumption.csv"])
    df = pd.read_csv(consumption_path)

    for i in range(0, len(score_bare.index)):
        tmp_df = df.loc[df['timestamp'] > score_bare["start"][i]]
        rslt_df = tmp_df.loc[tmp_df['timestamp'] < score_bare["end"][i]]
        bare_consumption.append(rslt_df['power consumption'].to_numpy())

    for i in range(0, len(score_docker.index)):
        tmp_df = df.loc[df['timestamp'] > score_docker["start"][i]]
        rslt_df = tmp_df.loc[tmp_df['timestamp'] < score_docker["end"][i]]
        docker_consumption.append(rslt_df['power consumption'].to_numpy())   

    return bare_consumption, docker_consumption 

def set_box_color(bp, color):
    plt.setp(bp['boxes'], color=color)
    plt.setp(bp['whiskers'], color=color)
    plt.setp(bp['caps'], color=color)
    plt.setp(bp['medians'], color=color)

def plot_power_consumption(data1, data2, ticks):    
    fig, ax = plt.subplots()
    
    # Creating plot
    bp1 = ax.boxplot(data1, positions=np.array(range(len(data1)))*2-0.3, sym='', widths=0.6)
    bp2 = ax.boxplot(data2, positions=np.array(range(len(data2)))*2+0.3, sym='', widths=0.6)

    set_box_color(bp1, '#D7191C') # colors are from http://colorbrewer2.org/
    set_box_color(bp2, '#2C7BB6')

    ax.legend([bp1["boxes"][0], bp2["boxes"][0]], ['Bare Metal', 'Docker'], loc='upper right')

    plt.xticks(range(0, len(ticks) * 2, 2), ticks)

    #plt.show()
    
    # show plot
    tikzplotlib.save("test.tex")

    

if __name__ == "__main__":
    score_bare_metal, score_docker = read_passmark_score()
    consumption_bare_metal, consumption_docker = compute_power_consumption(score_bare_metal, score_docker)

    plot_power_consumption(consumption_bare_metal, consumption_docker, score_bare_metal['load'].values.tolist())

    #prova()