import json
import device
import utils
import time
from threading import Thread
import datetime
import os
import pandas as pd
import sys
import math

def compare_by_consumption(devices, sol1, sol2):
    consumption_sol1 = 0
    consumption_sol2 = 0

    if sol2[0] == -1:
        return -1

    for i in range(len(sol1)):
        CPU_used = devices[i].CPU_cores - sol1[i]
        consumption_sol1 = consumption_sol1 + devices[i].get_consumption_at_load(CPU_used)

    for i in range(len(sol2)):
        CPU_used = devices[i].CPU_cores - sol2[i]
        consumption_sol2 = consumption_sol2 + devices[i].get_consumption_at_load(CPU_used)

    #if consumption_sol1 < consumption_sol2:
    #    print("Found worst solution with consumption " + str(consumption_sol1))
    # lower consumption better
    return consumption_sol1 - consumption_sol2


def compare_by_score(devices, sol1, sol2):
    score_sol1 = 0
    score_sol2 = 0

    for i in range(len(sol1)):
        CPU_used = devices[i].get_total_core() - sol1[i]
        score_sol1 = score_sol1 + devices[i].get_score_at_load(CPU_used)

    for i in range(len(sol2)):
        CPU_used = devices[i].get_total_core() - sol2[i]
        score_sol2 = score_sol2 + devices[i].get_score_at_load(CPU_used)

    # higher score better
    return score_sol2 - score_sol1

def compare_by_efficiency(devices, sol1, sol2):
    efficiency_sol1 = 0
    efficiency_sol2 = 0

    for i in range(len(sol1)):
        CPU_used = devices[i].get_total_core() - sol1[i]
        consumption_sol1 = devices[i].get_consumption_at_load(CPU_used)
        score_sol1 = devices[i].get_score_at_load(CPU_used)
        efficiency_sol1 = efficiency_sol1 + score_sol1/consumption_sol1

    for i in range(len(sol2)):
        CPU_used = devices[i].get_total_core() - sol2[i]
        consumption_sol2 = devices[i].get_consumption_at_load(CPU_used)
        score_sol2 = devices[i].get_score_at_load(CPU_used)
        efficiency_sol2 = efficiency_sol2 + score_sol2/consumption_sol2

    return efficiency_sol2 - efficiency_sol1


class Infrastructure(Thread):
    def __init__(self, infra_file_name, optimization_function, directory) -> None:
        utils.remove_content_check_value_directory()

        Thread.__init__(self)

        with open(infra_file_name) as f:
            data = json.load(f)

        self.infra_name = data["name"]
        self.infra_file_name = infra_file_name
        self.directory = directory
        self.report_folder = self.directory + "/" + self.infra_file_name.split("/")[len(self.infra_file_name.split("/"))-1].split(".")[0]
        self.start_simulation = datetime.datetime.strptime(data["start_simulation"], "%Y-%m-%d %H:%M:%S")
        self.end_simulation = datetime.datetime.strptime(data["end_simulation"], "%Y-%m-%d %H:%M:%S")
        self.optimization_function = optimization_function
        self.devices = []
        self.number_of_solutions = 0
        self.total_number_of_solutions = 0
        device_type = 0

        for dt in data["devices"]:
            for i in range(int(dt["replicas"])):
                dev_json = {}
                dev_json["name"] = dt["name"] + "-#" + str(i)
                dev_json["constant_load"] = dt["constant_load"]
                dev_json["variable_load"] = dt["variable_load"]
                dev_json["CPU_cores"] = dt["CPU_cores"]
                dev_json["CPU_usage_baseline"] = dt["CPU_usage_baseline"]
                dev_json["consumption_details"] = dt["consumption_details"]
                dev_json["performance_details"] = dt["performance_details"]
                dev_json["device_type"] = device_type

                dev = device.Device(dev_json)
                self.devices.append(dev)
            device_type = device_type + 1

    def run(self):

        original_placement = self.compute_original_placement()
        self.generate_report(original_placement, utils.SchedulingType.ORIGINAL)

        final_solution_continous = self.schedule_continous_workloads()
        scheduling_solution = self.schedule_variable_workload(final_solution_continous) 
        self.generate_report(scheduling_solution, utils.SchedulingType.OPTIMIZED)

    def compute_original_placement(self):
        original_placement = []

        delta = datetime.timedelta(minutes=1)
        start_date = self.start_simulation
        end_date = self.end_simulation
        for i in range(len(self.devices)):
            original_placement.append({})
            start_date = self.start_simulation
            end_date = self.end_simulation
            available_core = self.devices[i].CPU_cores
            if self.devices[i].has_constant_load_to_move:
                for l in self.devices[i].constant_load_to_move:
                    available_core -= l
            while start_date <= end_date:
                delta_core = 0
                if self.devices[i].has_variable_load_to_move:
                    for l in self.devices[i].variable_load_to_move:
                        if datetime.datetime.strptime(l["start"], "%Y-%m-%d %H:%M:%S") <= start_date and datetime.datetime.strptime(l["end"], "%Y-%m-%d %H:%M:%S") >= start_date:
                            delta_core += int(l["load"])
                if available_core - delta_core < 0:
                    print("Infrastructure " + self.infra_name + " require more then the available core for " + self.devices[i].name)
                    exit(-1)
                original_placement[i][str(start_date)] = available_core - delta_core
                start_date += delta

        return original_placement

    def schedule_continous_workloads(self):
        remaining_core = []
        constant_workload = []
        final_solution_continous = []
        self.number_of_solutions = 0
        consumption = [0, sys.maxsize]

        for i in range(len(self.devices)):
            remaining_core.append(int(self.devices[i].CPU_cores))
            consumption[0] += self.devices[i].get_consumption_at_load(0)
            final_solution_continous.append(-1)
            

        for d in self.devices:
            if d.has_constant_load_to_move:
                for l in d.constant_load_to_move:
                    constant_workload.append(int(l))

        num = len(self.devices)+len(constant_workload)-1
        self.total_number_of_solutions = int(math.factorial(num)/(math.factorial(len(constant_workload)) * math.factorial(num-len(constant_workload))))

        # determine the scheduling baseline with continous worloads
        self.recursive_schedule_continous_load(remaining_core, constant_workload, final_solution_continous, 0, consumption, 0, len(self.devices))
        return final_solution_continous

    def schedule_variable_workload(self, final_solution_continous):
        variable_workloads = []
        for d in self.devices:
            if d.has_variable_load_to_move:
                for l in d.variable_load_to_move:
                    l["workload_scheduled_on_device"] = -1
                    variable_workloads.append(l)

        sorted_varialble_workloads = sorted(variable_workloads, key=lambda d: datetime.datetime.strptime(d["start"], "%Y-%m-%d %H:%M:%S"))

        scheduling_solution = []
        delta = datetime.timedelta(minutes=1)
        start_date = self.start_simulation
        end_date = self.end_simulation
        for i in range(len(self.devices)):
            scheduling_solution.append({})
            start_date = self.start_simulation
            end_date = self.end_simulation
            while start_date <= end_date:
                scheduling_solution[i][str(start_date)] = final_solution_continous[i]
                start_date += delta

        start_date = self.start_simulation
        end_date = self.end_simulation
        while start_date <= end_date:
            variable_workload_to_schedule = []
            final_solution_variable = []
            for i in range(len(self.devices)):
                final_solution_variable.append(-1)

            workload_placement = []
            final_workload_placement = []

            for wl in sorted_varialble_workloads:
                if datetime.datetime.strptime(wl["start"], "%Y-%m-%d %H:%M:%S") == start_date:
                    variable_workload_to_schedule.append(wl)

            if len(variable_workload_to_schedule) > 0: 
                for i in range(len(variable_workload_to_schedule)):
                    workload_placement.append(-1)
                    final_workload_placement.append(-1)

                for i in range(len(final_solution_continous)):
                    final_solution_continous[i] = scheduling_solution[i][str(start_date)]
                    
                self.recursive_schedule_variable_load(final_solution_continous, variable_workload_to_schedule, 0, final_solution_variable, workload_placement, final_workload_placement)

                for i in range(len(variable_workload_to_schedule)):
                    start = datetime.datetime.strptime(variable_workload_to_schedule[i]["start"], "%Y-%m-%d %H:%M:%S")
                    end = datetime.datetime.strptime(variable_workload_to_schedule[i]["end"], "%Y-%m-%d %H:%M:%S")
                    while start <= end:
                        scheduling_solution[final_workload_placement[i]][str(start)] -= int(variable_workload_to_schedule[i]["load"])
                        start += delta

            start_date += delta
        return scheduling_solution

    def recursive_schedule_variable_load(self, remaining_core, workloads, id, final_solution, workload_placement, final_workload_placement):
        if id == len(workloads):
            if final_solution[0] == -1:
                for i in range(len(final_solution)):
                    final_solution[i] = remaining_core[i]
                for i in range(len(workload_placement)):
                    final_workload_placement[i] = workload_placement[i]
                return

            if self.optimization_function(self.devices, remaining_core, final_solution) < 0:
                for i in range(len(final_solution)):
                    final_solution[i] = remaining_core[i]
                for i in range(len(workload_placement)):
                    final_workload_placement[i] = workload_placement[i]
            return

        for i in range(len(remaining_core)):
            if int(workloads[id]["load"]) <= remaining_core[i]:
                workload_placement[id] = i
                remaining_core[i] = remaining_core[i] - int(workloads[id]["load"])
                self.recursive_schedule_variable_load(remaining_core, workloads, id+1, final_solution, workload_placement, final_workload_placement)
                remaining_core[i] = remaining_core[i] + int(workloads[id]["load"])
                workload_placement[id] = -1

    
    def recursive_schedule_continous_load(self, remaining_core, workload, final_solution, id, consumption, start, end):
        if id == len(workload):
            self.number_of_solutions = self.number_of_solutions + 1
            #print(consumption)
            # final step of the recursion
            if final_solution[0] == -1:
                consumption[1] = consumption[0]
                for i in range(len(final_solution)):
                    final_solution[i] = remaining_core[i]
                return

            if consumption[0] < consumption[1]:
                consumption[1] = consumption[0]
                for i in range(len(final_solution)):
                    final_solution[i] = remaining_core[i]
            return

        available_devices = []
        available_devices.append(start)
        for i in range(start +1, end):
            if remaining_core[i] == remaining_core[i-1] and self.devices[i].check_same_device_type(self.devices[i-1]):
                continue
            else:
                available_devices.append(i)

        for i in available_devices:
            #skip_this_device = False
            
            #for j in range(start, i):
            #    if self.devices[i].check_same_device_type(self.devices[j]) and remaining_core[i] == remaining_core[j]:
            #        skip_this_device = True
            #        break
            
            #if skip_this_device:
            #    continue
            
            if workload[id] <= remaining_core[i]:
                current_consumption = self.devices[i].convert_remaining_score_to_consumption(remaining_core[i])
                consumption[0] -= current_consumption
                remaining_core[i] = remaining_core[i] - workload[id]
                new_consumption = self.devices[i].convert_remaining_score_to_consumption(remaining_core[i])
                consumption[0] += new_consumption
                if consumption[0] < consumption[1]:
                    self.recursive_schedule_continous_load(remaining_core, workload, final_solution, id+1, consumption, i, end)
                consumption[0] -= new_consumption
                consumption[0] += current_consumption
                remaining_core[i] = remaining_core[i] + workload[id]
 
        return

    def generate_report(self, final_solution, type):
        if not os.path.exists(self.report_folder):
            os.mkdir(self.report_folder)
        
        infrastructure_consumption = {}
        infrastructure_consumption["date"] = []
        infrastructure_cpu_usage_percentage = {}
        infrastructure_cpu_usage_percentage["date"] = []
        infrastructure_cpu_usage_absolute = {}
        infrastructure_cpu_usage_absolute["date"] = []
        infrastructure_score = {}
        infrastructure_score["date"] = []

        for i in range(len(self.devices)):
            infrastructure_consumption[self.devices[i].name] = []
            infrastructure_score[self.devices[i].name] = []
            infrastructure_cpu_usage_percentage[self.devices[i].name] = []
            infrastructure_cpu_usage_absolute[self.devices[i].name] = []

        delta = datetime.timedelta(minutes=1)
        start_date = self.start_simulation
        end_date = self.end_simulation
        while start_date <= end_date:
            infrastructure_consumption["date"].append(start_date)
            infrastructure_cpu_usage_percentage["date"].append(start_date)
            infrastructure_cpu_usage_absolute["date"].append(start_date)
            infrastructure_score["date"].append(start_date)

            partial_solution = []
            for i in range(len(self.devices)):
                partial_solution.append(final_solution[i][str(start_date)])

            for i in range(len(self.devices)):
                CPU_used = self.devices[i].convert_remaining_score_to_CPU_core(partial_solution[i])
                CPU_total = self.devices[i].convert_remaining_score_to_CPU_core(0)
                infrastructure_consumption[self.devices[i].name].append(round(self.devices[i].convert_remaining_score_to_consumption(partial_solution[i]), 2))
                infrastructure_cpu_usage_percentage[self.devices[i].name].append(round((CPU_used/CPU_total)*100, 2))
                infrastructure_cpu_usage_absolute[self.devices[i].name].append(round(CPU_used, 2))
                infrastructure_score[self.devices[i].name].append(round(self.devices[i].CPU_cores + self.devices[i].CPU_usage_baseline - partial_solution[i], 2))

            start_date += delta

        df_consumption = pd.DataFrame(infrastructure_consumption)
        df_consumption.to_csv(self.report_folder + '/consumption-' + type.name + '.csv', index=None)
        df_usage = pd.DataFrame(infrastructure_cpu_usage_percentage)
        df_usage.to_csv(self.report_folder + '/percentual_CPU_usage-' + type.name + '.csv', index=None)
        df_usage_absolute = pd.DataFrame(infrastructure_cpu_usage_absolute)
        df_usage_absolute.to_csv(self.report_folder + '/absolute_CPU_usage-' + type.name + '.csv', index=None)
        df_score = pd.DataFrame(infrastructure_score)
        df_score.to_csv(self.report_folder + '/score-' + type.name + '.csv', index=None)

    def print_report(self, final_solution, start_time):
        str_ret = " -- Final Scheduling Report ---\n"
        str_ret = str_ret + "Infrastructure name:    \t" + self.infra_name + "\n"
        str_ret = str_ret + "Number of devices:      \t" + str(len(self.devices)) + "\n"
        str_ret = str_ret + "Analyzed solutions:      \t" + str(self.number_of_solutions) + "/" + str(self.total_number_of_solutions) + " (lower result may derive from pruning of unfeasible solutions)" +  "\n"
        str_ret = str_ret + "Simulation time:        \t" + str(int(time.time() - start_time)) + " s\n"
        str_ret = str_ret + "Initial power consumption: \t" + str(self.compute_initial_consumption()) + " W" + "\n"
        str_ret = str_ret + "Final power consumption: \t" + str(round(self.compute_final_consumption(final_solution), 2)) + " W" + "\n"
        str_ret = str_ret + "Initial workload score: \t" + str(self.compute_initial_score()) + "\n"
        str_ret = str_ret + "Final workload score:   \t" + str(round(self.compute_final_score(final_solution), 2)) + "\n"
        str_ret = str_ret + "Devices: \n"

        for i in range(len(self.devices)):
            str_ret = str_ret + "\t- " + self.devices[i].name + "\tCPU (used/total) " + str(round(self.devices[i].convert_remaining_score_to_CPU_core(final_solution[i]), 3)) + "/" + str(int(self.devices[i].convert_remaining_score_to_CPU_core(0)), 3) + "\n"
        
        print(str_ret)
        
    def __str__(self) -> str:
        str_ret = "Infrastructure name: " + self.infra_name + "\n"
        str_ret = str_ret + "Number of devices: " + str(len(self.devices)) + "\n"
        str_ret = str_ret + "Initial power consumption: " + str(self.compute_initial_consumption()) + " W" + "\n"
        str_ret = str_ret + "Initial workload score: " + str(self.compute_initial_score()) + "\n"
        for d in self.devices:
            str_ret = str_ret + "\t" + str(d) + "\n"
        return str_ret

    def compute_initial_score(self):
        score = 0

        for d in self.devices:
            score = score + d.compute_initial_score()

        return round(score, 2)

    def compute_final_score(self, remaining_resources):
        score = 0.0
        for i in range(len(remaining_resources)):
            CPU_used = self.devices[i].CPU_cores + self.devices[i].CPU_usage_baseline  - remaining_resources[i]
            score = score + CPU_used

        return score

    def compute_initial_consumption(self):
        consumption = 0

        for d in self.devices:
            consumption = consumption + d.compute_initial_workload_consumption()

        return round(consumption, 2)

    def compute_final_consumption(self, remaining_resources):
        consumption = 0.0
        for i in range(len(remaining_resources)):
            CPU_used = self.devices[i].CPU_cores - remaining_resources[i]
            consumption = consumption + self.devices[i].get_consumption_at_load(CPU_used)

        return consumption
