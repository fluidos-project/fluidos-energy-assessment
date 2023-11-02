import infrastructure as infra
import time
import utils

N_INFRA = 10

if __name__ == "__main__":
    start_time = time.time()
    report_path = "./reports-" + str(int(time.time()))
    utils.create_report_directory(report_path)
    infrastructures = []

    for i in range(N_INFRA):
        infrastructure = infra.Infrastructure('./example_infrastructures/infrastructure' + str(i) + '.json', infra.compare_by_consumption, report_path)
        infrastructures.append(infrastructure)

    # Start all threads
    for x in infrastructures:
        x.start()

    # Wait for all of them to finish
    for x in infrastructures:
        x.join()

    utils.summarize_reports(N_INFRA, report_path)

    print("Simulation ended in: " + str(int(time.time() - start_time)) + "s\n")
    for i in infrastructures:
        print("Analyzed solutions for infra " + i.infra_name + ": \t" + str(i.number_of_solutions) + "/" + str(i.total_number_of_solutions) + " (lower result may derive from pruning)\n")
