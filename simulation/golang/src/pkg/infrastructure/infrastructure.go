package infrastructure

import (
	"encoding/csv"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"math"
	"os"
	"strconv"
	"strings"
	"time"

	"github.com/stegala/PowerConsumptionAnalysis/pkg/device"
	"github.com/stegala/PowerConsumptionAnalysis/pkg/utils"
)

var frontendOverhead = 500
var frontendOverheadRaspberry = 200

type Infrastructure struct {
	reportPath          string
	infraName           string
	startSimulation     time.Time
	endSimulation       time.Time
	deviceList          []device.Device
	differentDeviceType int
	deviceNames         []string
}

type placementReport struct {
	availableCore int
	date          time.Time
}

func NewInfrastructure(infraPath string, reportPath string) *Infrastructure {
	i := Infrastructure{}
	iJson := infrastructureJson{}

	file, err := os.OpenFile(infraPath, os.O_RDWR, 0644)
	if err != nil {
		log.Fatal(err)
	}
	defer file.Close()

	byteValue, _ := ioutil.ReadAll(file)
	err = json.Unmarshal(byteValue, &iJson)
	if err != nil {
		log.Fatal(err)
	}

	i.infraName = iJson.Name
	i.startSimulation, err = time.Parse("2006-01-02 15:04:05", iJson.StartSimulation)
	if err != nil {
		log.Fatal(err)
	}
	i.endSimulation, err = time.Parse("2006-01-02 15:04:05", iJson.EndSimulation)
	if err != nil {
		log.Fatal(err)
	}
	i.reportPath = reportPath + "/" + strings.Split(strings.Split(infraPath, "/")[len(strings.Split(infraPath, "/"))-1], ".")[0]
	if err := os.Mkdir(i.reportPath, os.ModePerm); err != nil {
		log.Fatal(err)
	}

	i.deviceList = make([]device.Device, 0, len(iJson.Devices))

	devType := 0
	i.differentDeviceType = 0
	i.deviceNames = make([]string, 0, 1)
	for _, d := range iJson.Devices {
		i.differentDeviceType++
		nReplicas, err := strconv.Atoi(d.Replicas)
		if err != nil {
			log.Fatal(err)
		}
		baseName := d.Name
		i.deviceNames = append(i.deviceNames, baseName)
		for j := 0; j < nReplicas; j++ {
			d.Name = baseName + "-#" + strconv.Itoa(j)
			i.deviceList = append(i.deviceList, *device.NewDevice(d, devType))
		}
		devType++
	}

	return &i
}

func (infra Infrastructure) ComputeOptimizedPlacement(endChan chan bool) {
	originalPlacement := infra.computeOriginalPlacement()
	infra.generateReport(originalPlacement, utils.Original)
	infra.generateReport(originalPlacement, utils.Basic)

	optimizedPlacement := infra.computeOptimizedPlacement(utils.Optimized)
	enhancedPlacement := infra.computeOptimizedPlacement(utils.Enhanced)
	infra.generateReport(optimizedPlacement, utils.Optimized)
	infra.generateReport(enhancedPlacement, utils.Enhanced)

	endChan <- true
}

func (infra Infrastructure) computeOriginalPlacement() [][]placementReport {
	originalPlacement := make([][]placementReport, len(infra.deviceList))

	for i := 0; i < len(infra.deviceList); i++ {
		originalPlacement[i] = make([]placementReport, 0, 2)
		availableCPU := int(infra.deviceList[i].GetAvailableCPU())
		if infra.deviceList[i].HasConstantLoadToMove() {
			for _, l := range infra.deviceList[i].ConstantLoadToMove() {
				availableCPU -= l
			}
		}

		for d := infra.startSimulation; !d.After(infra.endSimulation); d = d.Add(time.Duration(time.Minute)) {
			originalPlacement[i] = append(originalPlacement[i], placementReport{
				availableCore: availableCPU,
				date:          d,
			})
		}
	}

	return originalPlacement
}

func (infra *Infrastructure) computeOptimizedPlacement(sType utils.SchedulingType) [][]placementReport {
	optimizedPlacement := make([][]placementReport, len(infra.deviceList))
	remainingCore := make([]int, len(infra.deviceList))
	constantWorkload := make([]int, 0)
	finalSolutionContinous := make([]int, 0)
	consumption := make([]float64, 0)

	c := 0.0
	for i := 0; i < len(infra.deviceList); i++ {
		remainingCore[i] = int(infra.deviceList[i].GetAvailableCPU())
		if sType == utils.Enhanced && !infra.deviceList[i].HasConstantLoadToMove() {
			c += infra.deviceList[i].GetEnhancedConsumptioAtLoad(0)
		} else {
			c += infra.deviceList[i].GetConsumptioAtLoad(0)
		}

		finalSolutionContinous = append(finalSolutionContinous, -1)
	}
	consumption = append(consumption, c)
	consumption = append(consumption, math.MaxFloat64)

	for _, d := range infra.deviceList {
		if d.HasConstantLoadToMove() {
			for _, l := range d.ConstantLoadToMove() {
				constantWorkload = append(constantWorkload, int(l))
			}
		}
	}

	infra.recursiveScheduleContinousLoad(remainingCore, constantWorkload, finalSolutionContinous, 0, consumption, 0, len(infra.deviceList), sType)

	for i := 0; i < len(infra.deviceList); i++ {
		optimizedPlacement[i] = make([]placementReport, 0, 2)

		for d := infra.startSimulation; !d.After(infra.endSimulation); d = d.Add(time.Duration(time.Minute)) {
			rem := finalSolutionContinous[i]
			load := 0
			for _, l := range infra.deviceList[i].ConstantLoadToMove() {
				load += l
			}

			if infra.deviceList[i].HasConstantLoadToMove() && rem > infra.deviceList[i].GetAvailableCPU()-load {
				if strings.Contains(strings.ToLower(infra.deviceList[i].GetDeviceName()), "rasp") {
					rem -= frontendOverheadRaspberry
				} else {
					rem -= frontendOverhead
				}

			}
			optimizedPlacement[i] = append(optimizedPlacement[i], placementReport{
				availableCore: rem,
				date:          d,
			})

		}
	}

	return optimizedPlacement
}

func (infra *Infrastructure) isTheSolutionAcceptable(remainingCore []int) bool {
	for id, dev := range infra.deviceList {
		if !dev.HasConstantLoadToMove() {
			if remainingCore[id] != dev.GetAvailableCPU() {
				return true
			}
		}
	}
	return false
}

func (infra *Infrastructure) recursiveScheduleContinousLoad(remainingCore []int, constantWorkload []int, finalSolutionContinous []int, id int, consumption []float64, start int, end int, sType utils.SchedulingType) {
	if id == len(constantWorkload) {
		//if !infra.isTheSolutionAcceptable(remainingCore) {
		//	return
		//}
		//correct consumption with frontend overhead
		consumptionCorrection := 0.0
		for i := 0; i < len(infra.deviceList); i++ {
			rem := remainingCore[i]

			load := 0
			for _, l := range infra.deviceList[i].ConstantLoadToMove() {
				load += l
			}

			if infra.deviceList[i].HasConstantLoadToMove() && rem > infra.deviceList[i].GetAvailableCPU()-load {
				// need to add frontend overhead
				if strings.Contains(strings.ToLower(infra.deviceList[i].GetDeviceName()), "rasp") {
					if rem < frontendOverheadRaspberry {
						return
					} else {
						consumptionCorrection += infra.deviceList[i].GetConsumptioFromRemainingResources(remainingCore[i]-frontendOverheadRaspberry, sType)
					}
				} else {
					if rem < frontendOverhead {
						return 
					} else {
						consumptionCorrection += infra.deviceList[i].GetConsumptioFromRemainingResources(remainingCore[i]-frontendOverhead, sType)
					}
				}
			} else {
				consumptionCorrection += infra.deviceList[i].GetConsumptioFromRemainingResources(remainingCore[i], sType)
			}
		}

		//final step of the recursion
		if finalSolutionContinous[0] == -1 {
			consumption[1] = consumptionCorrection
			for i := 0; i < len(finalSolutionContinous); i++ {
				finalSolutionContinous[i] = remainingCore[i]
			}
			return
		}

		if consumptionCorrection < consumption[1] {
			consumption[1] = consumptionCorrection
			for i := 0; i < len(finalSolutionContinous); i++ {
				finalSolutionContinous[i] = remainingCore[i]
			}
		}

		return
	}

	availableDevices := make([]int, 0, len(remainingCore))
	availableDevices = append(availableDevices, start)
	for i := start + 1; i < end; i++ {
		if remainingCore[i] == remainingCore[i-1] && infra.deviceList[i].CheckSameDeviceType(infra.deviceList[i-1]) {
			continue
		} else {
			availableDevices = append(availableDevices, i)
		}
	}

	for _, i := range availableDevices {

		if constantWorkload[id] <= remainingCore[i] {
			currentConsumption := infra.deviceList[i].GetConsumptioFromRemainingResources(remainingCore[i], sType)
			consumption[0] -= currentConsumption
			remainingCore[i] -= constantWorkload[id]
			newConsumption := infra.deviceList[i].GetConsumptioFromRemainingResources(remainingCore[i], sType)
			consumption[0] += newConsumption
			if consumption[0] < consumption[1] {
				infra.recursiveScheduleContinousLoad(remainingCore, constantWorkload, finalSolutionContinous, id+1, consumption, i, end, sType)
			}
			consumption[0] -= newConsumption
			consumption[0] += currentConsumption
			remainingCore[i] += constantWorkload[id]
		}
	}

	return
}

func (infra *Infrastructure) generateReport(solution [][]placementReport, sType utils.SchedulingType) {
	slotCount := 0
	for d := infra.startSimulation; !d.After(infra.endSimulation); d = d.Add(time.Duration(time.Minute)) {
		slotCount++
	}

	scoreUsagePercentual := make([][]string, slotCount)
	cpuUsagePercentual := make([][]string, slotCount)
	cpuUsageAbsolute := make([][]string, slotCount)
	infrastructureConsumption := make([][]string, slotCount)
	deviceResourceUsagePercentual := make([][]string, slotCount)

	scoreUsagePercentual[0] = make([]string, 0, len(infra.deviceList)+1)
	cpuUsagePercentual[0] = make([]string, 0, len(infra.deviceList)+1)
	cpuUsageAbsolute[0] = make([]string, 0, len(infra.deviceList)+1)
	infrastructureConsumption[0] = make([]string, 0, len(infra.deviceList)+1)
	deviceResourceUsagePercentual[0] = make([]string, 0, infra.differentDeviceType+1)

	scoreUsagePercentual[0] = append(scoreUsagePercentual[0], "date")
	cpuUsagePercentual[0] = append(cpuUsagePercentual[0], "date")
	cpuUsageAbsolute[0] = append(cpuUsageAbsolute[0], "date")
	infrastructureConsumption[0] = append(infrastructureConsumption[0], "date")
	deviceResourceUsagePercentual[0] = append(deviceResourceUsagePercentual[0], "date")

	for i := 0; i < len(infra.deviceList); i++ {
		if sType == utils.Basic && !infra.deviceList[i].HasConstantLoadToMove() {
			continue
		}
		scoreUsagePercentual[0] = append(scoreUsagePercentual[0], infra.deviceList[i].GetDeviceName())
		cpuUsagePercentual[0] = append(cpuUsagePercentual[0], infra.deviceList[i].GetDeviceName())
		cpuUsageAbsolute[0] = append(cpuUsageAbsolute[0], infra.deviceList[i].GetDeviceName())
		infrastructureConsumption[0] = append(infrastructureConsumption[0], infra.deviceList[i].GetDeviceName())
	}

	for _, name := range infra.deviceNames {
		deviceResourceUsagePercentual[0] = append(deviceResourceUsagePercentual[0], name)
	}

	start := infra.startSimulation
	for i := 1; i < slotCount; i++ {
		scoreUsagePercentual[i] = make([]string, 0, len(infra.deviceList)+1)
		cpuUsagePercentual[i] = make([]string, 0, len(infra.deviceList)+1)
		cpuUsageAbsolute[i] = make([]string, 0, len(infra.deviceList)+1)
		infrastructureConsumption[i] = make([]string, 0, len(infra.deviceList)+1)
		deviceResourceUsagePercentual[i] = make([]string, 0, infra.differentDeviceType+1)

		devResourceCount := make([]float64, 0, infra.differentDeviceType)
		count := 0
		sumCPU := 0
		prevDeviceType := infra.deviceList[0].GetDeviceType()

		for j := 0; j < len(infra.deviceList)+1; j++ {
			if j == 0 {
				scoreUsagePercentual[i] = append(scoreUsagePercentual[i], start.String())
				cpuUsagePercentual[i] = append(cpuUsagePercentual[i], start.String())
				cpuUsageAbsolute[i] = append(cpuUsageAbsolute[i], start.String())
				infrastructureConsumption[i] = append(infrastructureConsumption[i], start.String())
				deviceResourceUsagePercentual[i] = append(deviceResourceUsagePercentual[i], start.String())
			} else {
				remRes := solution[j-1][i-1].availableCore
				if sType == utils.Enhanced || sType == utils.Basic {
					if remRes == infra.deviceList[j-1].GetAvailableCPU() && !infra.deviceList[j-1].HasConstantLoadToMove() {
						remRes = infra.deviceList[j-1].GetMaxCPU()
					}
				}

				if prevDeviceType == infra.deviceList[j-1].GetDeviceType() {
					sumCPU += (infra.deviceList[j-1].GetMaxCPU() - remRes)
					count++
				} else {
					prevDeviceType = infra.deviceList[j-1].GetDeviceType()
					devResourceCount = append(devResourceCount, float64(sumCPU)/float64((count*infra.deviceList[j-2].GetMaxCPU()))*100)
					sumCPU = (infra.deviceList[j-1].GetMaxCPU() - remRes)
					count = 1
				}

				if sType == utils.Basic && !infra.deviceList[j-1].HasConstantLoadToMove() {
					sumCPU = 0
					count++
					continue
				}

				scoreUsagePercentual[i] = append(scoreUsagePercentual[i], fmt.Sprintf("%.3f", (1.0-float64(remRes)/float64(infra.deviceList[j-1].GetMaxCPU()))*100))
				cpuUsagePercentual[i] = append(cpuUsagePercentual[i], fmt.Sprintf("%.3f", (infra.deviceList[j-1].GetCpuUsageFromRemainingResources(remRes)/infra.deviceList[j-1].GetCpuUsageFromRemainingResources(0.0))*100))
				cpuUsageAbsolute[i] = append(cpuUsageAbsolute[i], fmt.Sprintf("%.3f", infra.deviceList[j-1].GetCpuUsageFromRemainingResources(remRes)))
				infrastructureConsumption[i] = append(infrastructureConsumption[i], fmt.Sprintf("%.3f", infra.deviceList[j-1].GetConsumptioFromRemainingResources(remRes, sType)))
			}
		}
		devResourceCount = append(devResourceCount, float64(sumCPU)/float64((count*infra.deviceList[len(infra.deviceList)-1].GetMaxCPU()))*100)

		for j := 0; j < len(devResourceCount); j++ {
			deviceResourceUsagePercentual[i] = append(deviceResourceUsagePercentual[i], fmt.Sprintf("%.3f", devResourceCount[j]))
		}
		start = start.Add(time.Duration(time.Minute))
	}

	csvFilePercentualScore, err := os.Create(infra.reportPath + "/percentual_score_usage-" + sType.String() + ".csv")
	if err != nil {
		log.Fatalf("failed creating file: %s", err)
	}

	csvwriter := csv.NewWriter(csvFilePercentualScore)

	for _, empRow := range scoreUsagePercentual {
		_ = csvwriter.Write(empRow)
	}
	csvwriter.Flush()
	csvFilePercentualScore.Close()

	csvFileAbsoluteCPU, err := os.Create(infra.reportPath + "/absolute_CPU_usage-" + sType.String() + ".csv")
	if err != nil {
		log.Fatalf("failed creating file: %s", err)
	}

	csvwriter = csv.NewWriter(csvFileAbsoluteCPU)

	for _, empRow := range cpuUsageAbsolute {
		_ = csvwriter.Write(empRow)
	}
	csvwriter.Flush()
	csvFileAbsoluteCPU.Close()

	csvFilePercentualCPU, err := os.Create(infra.reportPath + "/percentual_CPU_usage-" + sType.String() + ".csv")
	if err != nil {
		log.Fatalf("failed creating file: %s", err)
	}

	csvwriter = csv.NewWriter(csvFilePercentualCPU)

	for _, empRow := range cpuUsagePercentual {
		_ = csvwriter.Write(empRow)
	}
	csvwriter.Flush()
	csvFilePercentualCPU.Close()

	csvInfrastructureConsumption, err := os.Create(infra.reportPath + "/consumption-" + sType.String() + ".csv")
	if err != nil {
		log.Fatalf("failed creating file: %s", err)
	}

	csvwriter = csv.NewWriter(csvInfrastructureConsumption)

	for _, empRow := range infrastructureConsumption {
		_ = csvwriter.Write(empRow)
	}
	csvwriter.Flush()
	csvInfrastructureConsumption.Close()

	csvFileDeviceUsage, err := os.Create(infra.reportPath + "/device_percentual_resource_usage-" + sType.String() + ".csv")
	if err != nil {
		log.Fatalf("failed creating file: %s", err)
	}

	csvwriter = csv.NewWriter(csvFileDeviceUsage)

	for _, empRow := range deviceResourceUsagePercentual {
		_ = csvwriter.Write(empRow)
	}
	csvwriter.Flush()
	csvFileDeviceUsage.Close()

}

func (i *Infrastructure) GetSimulationStartTime() time.Time {
	return i.startSimulation
}

func (i *Infrastructure) GetSimulationEndTime() time.Time {
	return i.endSimulation
}
