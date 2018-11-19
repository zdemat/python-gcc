#!/bin/bash
# Use this script on a MAC OSX platform with homebrew installed.

set -e
set -x

# Install gcc7 (/opt/gcc7)
tar -xf deps/gcc-7.3.0.tar.xz
mv gcc-7.3.0 ~/gcc_src
mv deps/* ~/gcc_src/
cd ~/gcc_src
./contrib/download_prerequisites --no-graphite
mkdir ~/gcc_build
cd ~/gcc_build
~/gcc_src/configure --prefix ~/gcc7_install/ --enable-languages=c --disable-bootstrap --enable-nls &> log.txt
make &> log.txt
make install
cd ~/gcc7_install/
ls -Rlh
du -sh



