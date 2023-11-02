package main

import (
	"log"
	"runtime"

	//_ "net/http/pprof"
	"strconv"
	"time"

	infra "github.com/stegala/PowerConsumptionAnalysis/pkg/infrastructure"
	"github.com/stegala/PowerConsumptionAnalysis/pkg/utils"
)

var numberOfInfrastructure = 15
var safeThreadMargin = 1

func main() {
	//go func() {
	//	http.ListenAndServe(":1234", nil)
	//}()
	currCPU := runtime.NumCPU()
	//currCPU := 4
	log.Println("Detected " + strconv.Itoa(currCPU) + " virtual CPUs")

	curTime := int(time.Now().Unix())
	report_path := "./report-" + strconv.Itoa(curTime)
	infrastructures := make([]infra.Infrastructure, 0, numberOfInfrastructure)
	infraChannel := make([]chan bool, 0, numberOfInfrastructure)
	computationStart := make([]bool, 0, numberOfInfrastructure)
	computationEnd := make([]bool, 0, numberOfInfrastructure)

	if err := utils.CreateDirectory(report_path); err != nil {
		log.Fatal(err)
	} else {
		log.Println("Successfully created report directory " + report_path)
	}

	for i := 0; i < numberOfInfrastructure; i++ {
		infrastructures = append(infrastructures, *infra.NewInfrastructure("./paper_infrastructures_optimized_3/infrastructure"+strconv.Itoa(i)+".json", report_path))
		computationStart = append(computationStart, false)
		computationEnd = append(computationEnd, false)
		infraChannel = append(infraChannel, make(chan bool))
	}

	runningInstances := 0
	for id, i := range infrastructures {
		if runningInstances >= currCPU-safeThreadMargin {
			for runningInstances >= currCPU-safeThreadMargin {
				for id2, start := range computationStart {
					if start && !computationEnd[id2] {
						select {
						case _, ok := <-infraChannel[id2]:
							if ok {
								//log.Printf("Infrastructure %d finished the simulation.\n", id2)
								computationEnd[id2] = true
								printStatus(computationStart, computationEnd)
								runningInstances--
							} else {
								log.Println("Channel closed!")
							}
						default:
						}
					}
				}
				time.Sleep(time.Duration(1) * time.Second)
			}
		}
		runningInstances++
		computationStart[id] = true
		printStatus(computationStart, computationEnd)
		//log.Printf("Infrastructure %d started the simulation.\n", id)
		go i.ComputeOptimizedPlacement(infraChannel[id])
		//time.Sleep(time.Duration(15) * time.Second)
	}

	for runningInstances > 0 {
		for id, start := range computationStart {
			if start && !computationEnd[id] {
				select {
				case _, ok := <-infraChannel[id]:
					if ok {
						//log.Printf("Infrastructure %d finished the simulation.\n", id2)
						computationEnd[id] = true
						printStatus(computationStart, computationEnd)
						runningInstances--
					} else {
						log.Println("Channel closed!")
					}
				default:
				}
			}
		}
		time.Sleep(time.Duration(1) * time.Second)
	}

	utils.SummarizeReportsConsumption(numberOfInfrastructure, report_path, infrastructures[0].GetSimulationStartTime(), infrastructures[0].GetSimulationEndTime())
	utils.SummarizeReportsDeviceResourceConsumption(numberOfInfrastructure, report_path)
	elapsedTime := time.Now().Unix() - int64(curTime)
	log.Printf("Simulation ended in %ds\n", elapsedTime)

}

func printStatus(start []bool, end []bool) {
	//log.Println("-----------------------------------------")
	str := ""
	for i := 0; i < len(start); i++ {
		if end[i] == true {
			str += "|F"
		} else if start[i] == true {
			str += "|W"
		} else {
			str += "|."
		}
	}
	str += "|"

	log.Println(str)
	//log.Println("-----------------------------------------")
}
