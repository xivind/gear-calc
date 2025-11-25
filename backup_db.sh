#!/bin/bash
# Script to backup database for Gear Calc

set -o xtrace

docker container stop gear-calc
sleep 5
rm -vf /home/pi/backup/gear_calc.db
cp /home/pi/code/container_data/gear_calc.db /home/pi/backup/gear_calc.db
docker container start gear-calc
