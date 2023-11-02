#!/bin/bash
touch ./data/cpu_core_consumption
touch ./data/cpu_misc_consumption
touch ./data/memory_consumption
hostname=$(hostname)

while sleep 1
do
    powertop --time=10 --csv=output_cpu_power.csv -q > /dev/null

    core_consumption=$(cat output_cpu_power.csv | grep "CPU core" | cut -d ";" -f 3)
    misc_consumption=$(cat output_cpu_power.csv | grep "CPU misc" | cut -d ";" -f 3)
    memory_consumption=$(cat output_cpu_power.csv | grep ";DRAM" | cut -d ";" -f 3)

    echo "$(date +%s)$core_consumption" >> ./data/cpu_core_consumption
    echo "$(date +%s)$misc_consumption" >> ./data/cpu_misc_consumption
    echo "$(date +%s)$memory_consumption" >> ./data/memory_consumption

    usage=$(cat output_cpu_power.csv | grep "The system baseline power is estimated at:" | cut -d " " -f 9)

    usage_metric="scraper_cpu_usage_power{hostname=\"${hostname}\"} ${usage}"$'\n'
    
    curl -X POST -H  "Content-Type: text/plain" --data "$usage_metric" http://192.168.0.218:9091/metrics/job/top/instance/machine

    #echo $(date)
done