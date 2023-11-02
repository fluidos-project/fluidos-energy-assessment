#!/bin/bash
touch ./data/cpu_usage
#touch ./data/cpu_usage_docker
touch ./data/memory_usage

hostname=$(hostname)
thread=$(nproc --all)

echo "#how to read {pid, name, pcpu}" >> ./data/cpu_usage
echo "#how to read {timestamp, aggregated_cpu}" >> ./data/cpu_usage_docker
echo "#how to read {pid, name, pmem}" >> ./data/memory_usage


while sleep 5
do
    echo "#### $(date +%s)" >> ./data/memory_usage
    echo "#### $(date +%s)" >> ./data/cpu_usage


    # --------------------------------------
    # | Resource usage metrics with docker |
    # --------------------------------------

    check=$(docker stats --no-stream | grep "passmark_container")
    
    if [ $? -eq 0 ]; then 
        cpuDocker=$(echo $check | gawk '{print $3}' | cut -d "%" -f 1)
    else
        cpuDocker=0
    fi

    echo "$(date +%s) $cpuDocker" >> ./data/cpu_usage_docker

    cpumetric="scraper_docker_cpu_usage_percentage{hostname=\"${hostname}\"} ${cpuDocker}"$'\n'
    curl -X POST -H  "Content-Type: text/plain" --data "$cpumetric" http://192.168.0.218:9091/metrics/job/top/instance/machine

    # -----------------------------------------
    # | Resource usage metrics without docker |
    # -----------------------------------------
    #cmd=$(top -b -n2 -d 0.1)  
    #ntask=$(echo "$cmd" | grep "Tasks:" | tail -n 1 | cut -d " " -f 2)
    #taskList=$(echo "$cmd" | tail -n $ntask | gawk '{print $1,$9,$10,$12}')

    #totcpu=0
    #totram=0
    #while read z
    #do
    #    process=$(echo $z | cut -d " " -f 4)
    #    pid=$(echo $z | cut -d " " -f 1)
    #    pcpu=$(echo $z | cut -d " " -f 2 | tr "," ".")
    #    pmem=$(echo $z | cut -d " " -f 3 | tr "," ".")

        #echo "$pid $process $pcpu" >> ./data/cpu_usage
        #echo "$pid $process $pmem" >> ./data/memory_usage

    #    totcpu=$(echo "scale=3;$totcpu+$pcpu" | bc)
    #    totram=$(echo "scale=3;$totram+$pmem" | bc)

        #cpu="${cpu}scraper_cpu_usage_percentage{process=\"${process}\", pid=\"${pid}\", hostname=\"${hostname}\"} ${pcpu}"$'\n'
        #mem="${mem}scraper_memory_usage_percentage{process=\"${process}\", pid=\"${pid}\", hostname=\"${hostname}\"} ${pmem}"$'\n'
    #done <<< "$taskList"
    
    #echo "$(date +%s) $(echo "scale=3;$totcpu/$thread" | bc)" >> ../data/cpu_usage
    #echo "$(date +%s) $totcpu" >> ./data/cpu_usage
    #echo "$(date +%s) $totram" >> ./data/memory_usage
    #cpumetric="scraper_cpu_usage_percentage{hostname=\"${hostname}\"} ${totcpu}"$'\n'
    #memmetric="scraper_memory_usage_percentage{hostname=\"${hostname}\"} ${totram}"$'\n'
    #curl -X POST -H  "Content-Type: text/plain" --data "$cpumetric" http://192.168.0.218:9091/metrics/job/top/instance/machine
    #curl -X POST -H  "Content-Type: text/plain" --data "$memmetric" http://192.168.0.218:9091/metrics/job/top/instance/machine

    #echo $(date)
done
