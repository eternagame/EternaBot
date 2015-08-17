#!/bin/bash

#PBS -M mjwu@stanford.edu
#PBS -m ea
#PBS -l walltime=1:00:00:00
#PBS -l nodes=1:ppn=4

export PYTHONPATH=/home/mjwu/lib/python2.6/site-packages/:/home/mjwu/.local/lib/python2.7/site-packages/
export PATH=$PATH:/home/mjwu/EteRNABot/eternabot/resources/vienna/linux

#puzzle="parity_4input"
#options="-i 2000 -c 40"
cd EteRNABot/eternabot
python2.7 design_sequence.py ${puzzle} ${options}
