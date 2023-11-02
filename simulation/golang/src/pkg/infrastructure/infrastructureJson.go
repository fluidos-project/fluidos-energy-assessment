package infrastructure

import "github.com/stegala/PowerConsumptionAnalysis/pkg/device"

type infrastructureJson struct {
	Name            string              `json:"name"`
	StartSimulation string              `json:"start_simulation"`
	EndSimulation   string              `json:"end_simulation"`
	Devices         []device.DeviceJson `json:"devices"`
}
