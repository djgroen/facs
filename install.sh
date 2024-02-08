#!/bin/bash

# Function to check if a package is installed
is_package_installed() {
  dpkg -l "$1" &> /dev/null || yum list installed "$1" &> /dev/null
}

# Install g++, gcc, make, and Python 3.10 development headers if needed
if ! is_package_installed g++; then
  echo "Installing g++..."
  sudo apt-get install -y g++ || sudo yum install -y gcc-c++
fi

if ! is_package_installed gcc; then
  echo "Installing gcc..."
  sudo apt-get install -y gcc || sudo yum install -y gcc
fi

if ! is_package_installed make; then
  echo "Installing make..."
  sudo apt-get install -y make || sudo yum install -y make
fi

if ! is_package_installed python3.10-dev; then
  echo "Installing Python 3.10 development headers..."
  sudo apt-get install -y python3.10-dev || sudo yum install -y python3.10-devel
fi

# Continue with the rest of your script

pip3 install -r requirements.txt

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

pip3 install -r requirements.txt
