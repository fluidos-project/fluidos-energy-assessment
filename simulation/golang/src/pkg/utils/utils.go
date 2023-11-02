package utils

import (
	"encoding/csv"
	"fmt"
	"log"
	"os"
	"strconv"
	"time"
)

type SchedulingType int64

const (
	Original  SchedulingType = 1
	Basic     SchedulingType = 0
	Optimized SchedulingType = 2
	Enhanced  SchedulingType = 3
)

func (s SchedulingType) String() string {
	switch s {
	case Original:
		return "ORIGINAL"
	case Optimized:
		return "OPTIMIZED"
	case Basic:
		return "BASIC"
	case Enhanced:
		return "ENHANCED"
	default:
		return fmt.Sprintf("%d", int(s))

	}
}

func CreateDirectory(path string) error {
	return os.Mkdir(path, os.ModePerm)
}

func SummarizeReportsDeviceResourceConsumption(nInfra int, report_path string) {
	csvFileResourceUsageExcel, err := os.Create(report_path + "/overall_device_resource_usage_excel.csv")
	if err != nil {
		log.Fatalf("failed creating file: %s", err)
	}

	csvwriterExcel := csv.NewWriter(csvFileResourceUsageExcel)

	deviceResourceUsageExcel := make([][]string, 0, 5)

	for i := 0; i < nInfra; i++ {
		if i == 0 {
			for j := 0; j < 5; j++ {
				deviceResourceUsageExcel = append(deviceResourceUsageExcel, make([]string, 0, 1))
				if j == 0 {
					deviceResourceUsageExcel[j] = append(deviceResourceUsageExcel[j], "")
				}
			}
			deviceResourceUsageExcel[1] = append(deviceResourceUsageExcel[1], Basic.String())
			deviceResourceUsageExcel[2] = append(deviceResourceUsageExcel[2], Original.String())
			deviceResourceUsageExcel[3] = append(deviceResourceUsageExcel[3], Optimized.String())
			deviceResourceUsageExcel[4] = append(deviceResourceUsageExcel[4], Enhanced.String())
		}

		csvResourceUsageBasic, err := os.Open(report_path + "/infrastructure" + strconv.Itoa(i) + "/device_percentual_resource_usage-" + Basic.String() + ".csv")
		if err != nil {
			log.Fatal(err)
		}
		defer csvResourceUsageBasic.Close()

		csvLinesResourceUsageBasic, err := csv.NewReader(csvResourceUsageBasic).ReadAll()
		if err != nil {
			fmt.Println(err)
		}

		csvResourceUsageOriginal, err := os.Open(report_path + "/infrastructure" + strconv.Itoa(i) + "/device_percentual_resource_usage-" + Original.String() + ".csv")
		if err != nil {
			log.Fatal(err)
		}
		defer csvResourceUsageOriginal.Close()

		csvLinesResourceUsageOriginal, err := csv.NewReader(csvResourceUsageOriginal).ReadAll()
		if err != nil {
			fmt.Println(err)
		}

		csvResourceUsageOptimized, err := os.Open(report_path + "/infrastructure" + strconv.Itoa(i) + "/device_percentual_resource_usage-" + Optimized.String() + ".csv")
		if err != nil {
			log.Fatal(err)
		}
		defer csvResourceUsageOptimized.Close()

		csvLinesResourceUsageOptimized, err := csv.NewReader(csvResourceUsageOptimized).ReadAll()
		if err != nil {
			fmt.Println(err)
		}

		csvResourceUsageEnhanced, err := os.Open(report_path + "/infrastructure" + strconv.Itoa(i) + "/device_percentual_resource_usage-" + Enhanced.String() + ".csv")
		if err != nil {
			log.Fatal(err)
		}
		defer csvResourceUsageEnhanced.Close()

		csvLinesResourceUsageEnhanced, err := csv.NewReader(csvResourceUsageEnhanced).ReadAll()
		if err != nil {
			fmt.Println(err)
		}

		for j := 1; j < len(csvLinesResourceUsageEnhanced[0]); j++ {
			deviceResourceUsageExcel[0] = append(deviceResourceUsageExcel[0], csvLinesResourceUsageEnhanced[0][j])
		}

		for j := 1; j < len(csvLinesResourceUsageEnhanced[0]); j++ {
			deviceResourceUsageExcel[1] = append(deviceResourceUsageExcel[1], csvLinesResourceUsageBasic[1][j])
			deviceResourceUsageExcel[2] = append(deviceResourceUsageExcel[2], csvLinesResourceUsageOriginal[1][j])
			deviceResourceUsageExcel[3] = append(deviceResourceUsageExcel[3], csvLinesResourceUsageOptimized[1][j])
			deviceResourceUsageExcel[4] = append(deviceResourceUsageExcel[4], csvLinesResourceUsageEnhanced[1][j])
		}
	}

	for _, empRow := range deviceResourceUsageExcel {
		_ = csvwriterExcel.Write(empRow)
	}

	csvwriterExcel.Flush()
	csvFileResourceUsageExcel.Close()

}

func SummarizeReportsConsumption(nInfra int, reportPath string, start time.Time, end time.Time) {
	csvFileConsumption, err := os.Create(reportPath + "/overall_infrastructure_consumption.csv")
	if err != nil {
		log.Fatalf("failed creating file: %s", err)
	}

	csvwriter := csv.NewWriter(csvFileConsumption)

	csvFileConsumptionExcel, err := os.Create(reportPath + "/overall_infrastructure_consumption_excel.csv")
	if err != nil {
		log.Fatalf("failed creating file: %s", err)
	}

	csvwriterExcel := csv.NewWriter(csvFileConsumptionExcel)

	slotCount := 0
	for d := start; !d.After(end); d = d.Add(time.Duration(time.Minute)) {
		slotCount++
	}

	infrastructureConsumption := make([][]string, slotCount)
	infrastructureConsumptionExcel := make([][]string, 4)
	infrastructureConsumption[0] = make([]string, 0, nInfra*4+1)
	infrastructureConsumption[0] = append(infrastructureConsumption[0], "date")

	for i := 1; i < slotCount; i++ {
		infrastructureConsumption[i] = make([]string, 1, nInfra*4+1)
	}

	for i := 0; i < nInfra; i++ {
		infrastructureConsumption[0] = append(infrastructureConsumption[0], "infrastructure"+strconv.Itoa(i)+"-"+Basic.String())
		infrastructureConsumption[0] = append(infrastructureConsumption[0], "infrastructure"+strconv.Itoa(i)+"-"+Original.String())
		infrastructureConsumption[0] = append(infrastructureConsumption[0], "infrastructure"+strconv.Itoa(i)+"-"+Optimized.String())
		infrastructureConsumption[0] = append(infrastructureConsumption[0], "infrastructure"+strconv.Itoa(i)+"-"+Enhanced.String())
	}

	for i := 0; i < 4; i++ {
		infrastructureConsumptionExcel[i] = make([]string, nInfra+1)
		infrastructureConsumptionExcel[i][0] = SchedulingType(i).String()
	}

	for i := 0; i < nInfra; i++ {

		csvConsumptionBasic, err := os.Open(reportPath + "/infrastructure" + strconv.Itoa(i) + "/consumption-" + Basic.String() + ".csv")
		if err != nil {
			log.Fatal(err)
		}
		defer csvConsumptionBasic.Close()

		csvLinesConsumptionBasic, err := csv.NewReader(csvConsumptionBasic).ReadAll()
		if err != nil {
			fmt.Println(err)
		}

		csvConsumptionOriginal, err := os.Open(reportPath + "/infrastructure" + strconv.Itoa(i) + "/consumption-" + Original.String() + ".csv")
		if err != nil {
			log.Fatal(err)
		}
		defer csvConsumptionOriginal.Close()

		csvLinesConsumptionOriginal, err := csv.NewReader(csvConsumptionOriginal).ReadAll()
		if err != nil {
			fmt.Println(err)
		}

		csvConsumptionOptimized, err := os.Open(reportPath + "/infrastructure" + strconv.Itoa(i) + "/consumption-" + Optimized.String() + ".csv")
		if err != nil {
			log.Fatal(err)
		}
		defer csvConsumptionOptimized.Close()

		csvLinesConsumptionOptimized, err := csv.NewReader(csvConsumptionOptimized).ReadAll()
		if err != nil {
			fmt.Println(err)
		}

		csvConsumptionEnhanced, err := os.Open(reportPath + "/infrastructure" + strconv.Itoa(i) + "/consumption-" + Enhanced.String() + ".csv")
		if err != nil {
			log.Fatal(err)
		}
		defer csvConsumptionEnhanced.Close()

		csvLinesConsumptionEnhanced, err := csv.NewReader(csvConsumptionEnhanced).ReadAll()
		if err != nil {
			fmt.Println(err)
		}

		for j := 1; j < slotCount; j++ {
			infrastructureConsumption[j][0] = csvLinesConsumptionOptimized[j][0]
			sumBasic := 0.0
			sumOriginal := 0.0
			sumOptimized := 0.0
			sumEnhanced := 0.0
			for k := 1; k < len(csvLinesConsumptionOptimized[j]); k++ {

				if k < len(csvLinesConsumptionBasic[j]) {
					bas, err := strconv.ParseFloat(csvLinesConsumptionBasic[j][k], 64)
					if err != nil {
						log.Fatal(err)
					}
					sumBasic += bas
				}

				ori, err := strconv.ParseFloat(csvLinesConsumptionOriginal[j][k], 64)
				if err != nil {
					log.Fatal(err)
				}
				sumOriginal += ori

				opt, err := strconv.ParseFloat(csvLinesConsumptionOptimized[j][k], 64)
				if err != nil {
					log.Fatal(err)
				}
				sumOptimized += opt

				enh, err := strconv.ParseFloat(csvLinesConsumptionEnhanced[j][k], 64)
				if err != nil {
					log.Fatal(err)
				}
				sumEnhanced += enh
			}

			infrastructureConsumption[j] = append(infrastructureConsumption[j], fmt.Sprintf("%.3f", sumBasic))
			infrastructureConsumption[j] = append(infrastructureConsumption[j], fmt.Sprintf("%.3f", sumOriginal))
			infrastructureConsumption[j] = append(infrastructureConsumption[j], fmt.Sprintf("%.3f", sumOptimized))
			infrastructureConsumption[j] = append(infrastructureConsumption[j], fmt.Sprintf("%.3f", sumEnhanced))

			infrastructureConsumptionExcel[0][i+1] = fmt.Sprintf("%.3f", sumBasic)
			infrastructureConsumptionExcel[1][i+1] = fmt.Sprintf("%.3f", sumOriginal)
			infrastructureConsumptionExcel[2][i+1] = fmt.Sprintf("%.3f", sumOptimized)
			infrastructureConsumptionExcel[3][i+1] = fmt.Sprintf("%.3f", sumEnhanced)
		}
	}

	for _, empRow := range infrastructureConsumption {
		_ = csvwriter.Write(empRow)
	}

	for _, empRow := range infrastructureConsumptionExcel {
		_ = csvwriterExcel.Write(empRow)
	}

	csvwriter.Flush()
	csvwriterExcel.Flush()
	csvFileConsumption.Close()
	csvFileConsumptionExcel.Close()
}
