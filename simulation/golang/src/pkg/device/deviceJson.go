package device

type DeviceJson struct {
	Name             string `json:"name"`
	Replicas         string `json:"replicas"`
	CPUCores         string `json:"CPU_cores"`
	CPUUsageBaseline string `json:"CPU_usage_baseline"`
	ConstantLoad     struct {
		NeedToMove string `json:"need_to_move"`
		LoadToMove []int  `json:"load_to_move"`
	} `json:"constant_load"`
	VariableLoad struct {
		NeedToMove string `json:"need_to_move"`
		LoadToMove []struct {
			Start string `json:"start"`
			End   string `json:"end"`
			Load  string `json:"load"`
		} `json:"load_to_move"`
	} `json:"variable_load"`
	ConsumptionDetails string `json:"consumption_details"`
	PerformanceDetails string `json:"performance_details"`
}
