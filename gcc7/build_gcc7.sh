#!/bin/bash
# Use this script on a MAC OSX platform with homebrew installed.

set -e
set -x

# Install gcc7 (/opt/gcc7)
tar -xf deps/gcc-7.3.0.tar.xz
mv gcc-7.3.0 ~/bh/gcc
mv deps/* ~/bh/gcc
cd ~/bh/gcc
./contrib/download_prerequisites --no-graphite
mkdir -p ~/gcc_build
cd ~/gcc_build
~/gcc/configure --prefix ~/gcc7_install/ --enable-languages=c --disable-bootstrap --enable-nls
make
make install

