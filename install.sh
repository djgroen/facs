#!/bin/bash

pip3 -r requirements.txt
mkdir -p $HOME/opt/openmpi
cd $HOME/Downloads
wget https://download.open-mpi.org/release/open-mpi/v4.1/openmpi-4.1.2.tar.gz
tar -xf openmpi-4.1.2.tar.gz
cd openmpi-4.1.2
./configure --prefix=$HOME/opt/openmpi
make all && make install
export CC=$HOME/opt/openmpi/bin/mpicc
export PATH=$PATH:$HOME/opt/openmpi/bin
pip3 install mpi4py
mkdir $HOME/workspace & cd $HOME/workspace
git clone https://github.com/djgroen/facs
cd facs/ & mpirun –n 8 python ./run.py 