import numpy as np
#import matplotlib.pyplot as plt
import os, shutil
import pandas
from enum import Enum

class SchedulingType(Enum):
    ORIGINAL = 1
    OPTIMIZED = 2

def generate_continous_function_from_discrete_data(x_val, y_val, device_name, y_label):
    file_name = "./check_values/" + device_name + "-" + y_label + ".png"
    
    # get x and y vectors
    x = np.array(x_val)
    y = np.array(y_val)

    # calculate polynomial
    z = np.polyfit(x, y, 5)
    f = np.poly1d(z)

    #x_new = np.linspace(x[0], x[-1], 50)
    #y_new = f(x_new)

    #if os.path.exists(file_name):
    #    return f

    #fig, ax = plt.subplots()

    #ax.plot(x,y,'o', label="discrete values")
    #ax.plot(x_new,y_new, label="continous values")
    #plt.xlim([x[0]-1, x[-1] + 1 ])

    #ax.set_xlabel("Passmark score")
    #ax.set_ylabel(y_label)
    #ax.legend()

    #fig.savefig(file_name)
    #plt.close(fig)

    return f

def remove_content_check_value_directory():
    folder = './check_values'
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))
            exit(-1)

def create_report_directory(report_path):
    try:
        os.mkdir(report_path)
    except OSError:
        print ("Creation of the directory %s failed" % report_path)
        exit(-1)
    else:
        print ("Successfully created the directory %s " % report_path)

def summarize_reports(N_INFRA, report_path):
    consumption_report = pandas.DataFrame()
    score_report = pandas.DataFrame()
    CPU_usage_report = pandas.DataFrame()

    for i in range(N_INFRA):
        consumption_optimized = pandas.read_csv(report_path + "/infrastructure" + str(i) + "/consumption-" + SchedulingType.OPTIMIZED.name + ".csv")
        #fig, ax = plt.subplots()
        #consumption_optimized.plot()
        ##ax.legend(loc=2)
        #ax.set_xlabel("Time (m)")
        #ax.set_ylabel("Consumption (W)")
        #plt.savefig(report_path + "/infrastructure" + str(i) + "/consumption-" + SchedulingType.OPTIMIZED.name + ".png")
        #plt.close(fig)
        score_optimized = pandas.read_csv(report_path + "/infrastructure" + str(i) + "/score-" + SchedulingType.OPTIMIZED.name + ".csv")
        #fig, ax = plt.subplots()
        #score_optimized.plot()
        ##ax.legend(loc=2)
        #ax.set_xlabel("Time (m)")
        #ax.set_ylabel("Passmark Score")
        #plt.savefig(report_path + "/infrastructure" + str(i) + "/score-" + SchedulingType.OPTIMIZED.name + ".png")
        #plt.close(fig)
        CPU_usage_optimized = pandas.read_csv(report_path + "/infrastructure" + str(i) + "/absolute_CPU_usage-" + SchedulingType.OPTIMIZED.name + ".csv")
        #fig, ax = plt.subplots()
        #CPU_usage_optimized.plot()
        ##ax.legend(loc=2)
        #ax.set_xlabel("Time (m)")
        #ax.set_ylabel("CPU Cores")
        #plt.savefig(report_path + "/infrastructure" + str(i) + "/absolute_CPU_usage-" + SchedulingType.OPTIMIZED.name + ".png")
        #plt.close(fig)
        consumption_original = pandas.read_csv(report_path + "/infrastructure" + str(i) + "/consumption-" + SchedulingType.ORIGINAL.name + ".csv")
        #fig, ax = plt.subplots()
        #consumption_original.plot()
        ##ax.legend(loc=2)
        #ax.set_xlabel("Time (m)")
        #ax.set_ylabel("Consumption (W)")
        #plt.savefig(report_path + "/infrastructure" + str(i) + "/consumption-" + SchedulingType.ORIGINAL.name + ".png")
        #plt.close(fig)
        score_original = pandas.read_csv(report_path + "/infrastructure" + str(i) + "/score-" + SchedulingType.ORIGINAL.name + ".csv")
        #ig, ax = plt.subplots()
        #core_original.plot()
        #ax.legend(loc=2)
        #x.set_xlabel("Time (m)")
        #x.set_ylabel("Passmark Score")
        #lt.savefig(report_path + "/infrastructure" + str(i) + "/score-" + SchedulingType.ORIGINAL.name + ".png")
        #lt.close()
        CPU_usage_original = pandas.read_csv(report_path + "/infrastructure" + str(i) + "/absolute_CPU_usage-" + SchedulingType.ORIGINAL.name + ".csv")
        #fig, ax = plt.subplots()
        #CPU_usage_original.plot()
        ##ax.legend(loc=2)
        #ax.set_xlabel("Time (m)")
        #ax.set_ylabel("CPU Cores")
        #plt.savefig(report_path + "/infrastructure" + str(i) + "/absolute_CPU_usage-" + SchedulingType.ORIGINAL.name + ".png")
        #plt.close()

        
        consumption_report["date"] = consumption_optimized['date']
        score_report["date"] = score_optimized["date"]
        CPU_usage_report["date"] = CPU_usage_optimized["date"]
        consumption_report["infrastructure" + str(i) + "-" + SchedulingType.OPTIMIZED.name] = consumption_optimized.sum(axis=1, numeric_only=True)
        score_report["infrastructure" + str(i) + "-" + SchedulingType.OPTIMIZED.name] = score_optimized.sum(axis=1, numeric_only=True)
        CPU_usage_report["infrastructure" + str(i) + "-" + SchedulingType.OPTIMIZED.name] = CPU_usage_optimized.sum(axis=1, numeric_only=True)
        consumption_report["infrastructure" + str(i) + "-" + SchedulingType.ORIGINAL.name] = consumption_original.sum(axis=1, numeric_only=True)
        score_report["infrastructure" + str(i) + "-" + SchedulingType.ORIGINAL.name] = score_original.sum(axis=1, numeric_only=True)
        CPU_usage_report["infrastructure" + str(i) + "-" + SchedulingType.ORIGINAL.name] = CPU_usage_original.sum(axis=1, numeric_only=True)

    consumption_report.to_csv(report_path + '/overall_infrastructure_consumption.csv', index=None)
    score_report.to_csv(report_path + '/overall_infrastructure_score.csv', index=None)
    CPU_usage_report.to_csv(report_path + '/overall_infrastructure_CPU_usage.csv', index=None)

