import json
import utils
import sys
import numpy as np

class Device:
    def __init__(self, device) -> None:
        self.name = device["name"]
        self.CPU_usage_baseline = int(float(device["CPU_usage_baseline"]))
        self.CPU_cores = int(float(device["CPU_cores"])) - self.CPU_usage_baseline
        self.constant_load_to_move = []
        self.variable_load_to_move = []
        self.device_type = int(device["device_type"])

        if device["constant_load"]["need_to_move"] == "true":
            self.has_constant_load_to_move = True
            self.constant_load_to_move = device["constant_load"]["load_to_move"]
        else:
            self.has_constant_load_to_move = False

        if device["variable_load"]["need_to_move"] == "true":
            self.has_variable_load_to_move = True
            self.variable_load_to_move = device["variable_load"]["load_to_move"]
        else:
            self.has_variable_load_to_move = False

        with open(device["consumption_details"]) as f:
            data_consumption = json.load(f)

        with open(device["performance_details"]) as f:
            data_performance = json.load(f)

        x_val = []

        for i in range(0, self.CPU_cores + self.CPU_usage_baseline):
            x_val.append(i)

        self.consumption = utils.generate_continous_function_from_discrete_data(data_performance["data"]["core_score"], data_consumption["data"]["core_consumption"], self.name.split("-")[0], "Energy_consumption")(x_val).astype(float)
        self.performance = utils.generate_continous_function_from_discrete_data(data_performance["data"]["core_score"], data_performance["data"]["core_usage"], self.name.split("-")[0], "Pasmark_score")(x_val).astype(float)
        
        if "server" in self.name:
            #print(x_val)
            print("consumption")
            print("[", end="")
            count = 0
            for i in self.consumption:
                if count == self.CPU_cores + self.CPU_usage_baseline - 1:
                    print(round(i, 3), end="")
                else:
                    print(round(i, 3), end=",")
                count += 1
            print("]")
            #print(self.consumption)
            #print("performance")
            #print(self.performance)
            sys.exit()

    
    def __str__(self) -> str:
        return "- Dev name: " + self.name + "\tCPU cores: " + str(self.CPU_cores)

    def compute_initial_workload_consumption(self):
        load = self.CPU_usage_baseline
        if self.has_constant_load_to_move:
            for l in self.constant_load_to_move:
                load = load + l

        return self.consumption[load]

    def compute_initial_score(self):
        score = self.CPU_usage_baseline
        if self.has_constant_load_to_move:
            for l in self.constant_load_to_move:
                score = score + l

        return score

    def get_consumption_at_load(self, load):            
        return (self.consumption[load + self.CPU_usage_baseline - 1])

    def get_score_at_load(self, load):            
        return (self.performance[load + self.CPU_usage_baseline - 1])

    def convert_remaining_score_to_CPU_core(self, remaining_score):
        score = self.CPU_cores + self.CPU_usage_baseline - remaining_score - 1
        return (self.performance[score])

    def convert_remaining_score_to_consumption(self, remaining_score):
        score = self.CPU_cores + self.CPU_usage_baseline - remaining_score - 1
        return (self.consumption[score])

    def check_same_device_type(self, dev2):
        if self.device_type == dev2.device_type:
            return True
        return False
