import pandas
from enum import Enum

N_INFRA = 10
report_path = "./report-app-size"

class SchedulingType(Enum):
    ORIGINAL = 1
    OPTIMIZED = 2

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

    #CPU_usage_optimized.drop("date")
    col_list = list(CPU_usage_optimized)
    #print(CPU_usage_optimized)
    col_list_desktop = col_list[1:21]
    col_list_server = col_list[21:32]

    desktop_sum = CPU_usage_optimized[col_list_desktop].sum(axis=1, numeric_only=True)
    server_sum = CPU_usage_optimized[col_list_server].sum(axis=1, numeric_only=True)
    
    #consumption_report["date"] = consumption_optimized['date']
    #score_report["date"] = score_optimized["date"]
    #CPU_usage_report["date"] = CPU_usage_optimized["date"]
    #consumption_report["infrastructure" + str(i) + "-" + SchedulingType.OPTIMIZED.name] = consumption_optimized.sum(axis=1, numeric_only=True)
    #score_report["infrastructure" + str(i) + "-" + SchedulingType.OPTIMIZED.name] = score_optimized.sum(axis=1, numeric_only=True)
    CPU_usage_report["infrastructure" + str(i) + "-desktop"] = desktop_sum.head(1)/(8*2)*10
    CPU_usage_report["infrastructure" + str(i) + "-server"] = server_sum.head(1)/(28)*10

    #consumption_report["infrastructure" + str(i) + "-" + SchedulingType.ORIGINAL.name] = consumption_original.sum(axis=1, numeric_only=True)
    #score_report["infrastructure" + str(i) + "-" + SchedulingType.ORIGINAL.name] = score_original.sum(axis=1, numeric_only=True)
    #CPU_usage_report["infrastructure" + str(i) + "-" + SchedulingType.ORIGINAL.name] = CPU_usage_original.sum(axis=1, numeric_only=True)

#consumption_report.to_csv(report_path + '/overall_infrastructure_consumption.csv', index=None)
#score_report.to_csv(report_path + '/overall_infrastructure_score.csv', index=None)
CPU_usage_report.to_csv(report_path + '/excel_CPU_usage.csv', index=None)

