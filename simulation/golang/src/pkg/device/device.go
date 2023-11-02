package device

import (
	"encoding/json"
	"errors"
	"io/ioutil"
	"log"
	"os"
	"strconv"

	"github.com/stegala/PowerConsumptionAnalysis/pkg/utils"
)

type consumptionData struct {
	Data struct {
		CoreConsumption []float64 `json:"core_consumption"`
	} `json:"data"`
}

type performenceData struct {
	Data struct {
		CorePerformance []float64 `json:"core_score"`
	} `json:"data"`
}

type Device struct {
	deviceName            string
	deviceType            int
	cpuUsageBaseline      int
	cpuCores              int
	maxCPUCores           int
	hasConstantLoadToMove bool
	constantLoadToMove    []int
	hasVariableLoadToMove bool
	consumption           []float64
	performance           []float64
}

func NewDevice(deviceJson DeviceJson, deviceType int) *Device {
	var err error
	var cpuCores int
	d := Device{}

	d.deviceName = deviceJson.Name
	d.deviceType = deviceType
	d.cpuUsageBaseline, err = strconv.Atoi(deviceJson.CPUUsageBaseline)
	if err != nil {
		log.Fatal(err)
	}

	cpuCores, err = strconv.Atoi(deviceJson.CPUCores)
	if err != nil {
		log.Fatal(err)
	}

	d.maxCPUCores = cpuCores
	d.cpuCores = cpuCores - d.cpuUsageBaseline

	if deviceJson.ConstantLoad.NeedToMove == "true" {
		d.hasConstantLoadToMove = true
		d.constantLoadToMove = deviceJson.ConstantLoad.LoadToMove
	} else if deviceJson.ConstantLoad.NeedToMove == "false" {
		d.hasConstantLoadToMove = false
	} else {
		log.Fatal(errors.New("Device constant_load.need_to_move can only be either true or false"))
	}

	if deviceJson.VariableLoad.NeedToMove == "true" {
		d.hasVariableLoadToMove = true
	} else if deviceJson.VariableLoad.NeedToMove == "false" {
		d.hasVariableLoadToMove = false
	} else {
		log.Fatal(errors.New("Device variable_load.need_to_move can only be either true or false"))
	}

	fileConsumption, err := os.OpenFile(deviceJson.ConsumptionDetails, os.O_RDWR, 0644)
	if err != nil {
		log.Fatal(err)
	}
	defer fileConsumption.Close()

	cJson := consumptionData{}
	byteValueConsumption, _ := ioutil.ReadAll(fileConsumption)
	json.Unmarshal(byteValueConsumption, &cJson)

	d.consumption = cJson.Data.CoreConsumption

	filePerformance, err := os.OpenFile(deviceJson.PerformanceDetails, os.O_RDWR, 0644)
	if err != nil {
		log.Fatal(err)
	}
	defer filePerformance.Close()

	pJson := performenceData{}
	byteValuePerformance, _ := ioutil.ReadAll(filePerformance)
	err = json.Unmarshal(byteValuePerformance, &pJson)

	d.performance = pJson.Data.CorePerformance

	return &d
}

func (d *Device) GetAvailableCPU() int {
	return d.cpuCores
}

func (d *Device) GetMaxCPU() int {
	return int(d.maxCPUCores)
}

func (d *Device) HasConstantLoadToMove() bool {
	return d.hasConstantLoadToMove
}

func (d *Device) ConstantLoadToMove() []int {
	return d.constantLoadToMove
}

func (d *Device) GetDeviceName() string {
	return d.deviceName
}

func (d *Device) GetCpuUsageFromRemainingResources(rem int) float64 {
	if rem == d.maxCPUCores {
		return 0.0
	}
	usedCPU := d.maxCPUCores - rem - 2
	return d.performance[usedCPU]
}

func (d *Device) GetConsumptioFromRemainingResources(rem int, sType utils.SchedulingType) float64 {
	if rem == d.maxCPUCores || (sType == utils.Enhanced && rem == d.cpuCores && !d.hasConstantLoadToMove) {
		return 10.0
	}

	usedCPU := d.maxCPUCores - rem - 2
	//fmt.Println(d.maxCPUCores)
	return d.consumption[usedCPU]
}

func (d *Device) GetConsumptioAtLoad(load int) float64 {
	return d.consumption[load+d.cpuUsageBaseline]
}

func (d *Device) GetEnhancedConsumptioAtLoad(load int) float64 {
	if load == 0 {
		return 10.0
	}
	return d.consumption[load+d.cpuUsageBaseline]
}

func (d *Device) CheckSameDeviceType(d2 Device) bool {
	if d.deviceType == d2.deviceType {
		return true
	} else {
		return false
	}
}

func (d *Device) GetDeviceType() int {
	return d.deviceType
}
