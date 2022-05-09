#!/bin/bash

# Commands to enable modules, and then load an appropriate MP/MPI module
export PATH
. /etc/profile.d/modules.sh
module load mpi/mpich-3.2-x86_64

# Command to run your MP/MPI program
# (This example uses mpirun, other programs
# may use mpiexec, or other commands)
mpirun -np 4 /home/eepgmmg1/Downloads/facs/dist/run $1 $2 $3 $4 $5 $6 $7 $8 $9 ${10} ${11} ${12}
