#!/bin/bash
#PBS -o job.out
#PBS -e job.err
#PBS -l walltime=48:00:00
cd $PBS_O_WORKDIR
source ~/.bashrc 

python2.7 run_optimization.py
