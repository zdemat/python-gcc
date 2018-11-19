#!/bin/bash
# Use this script on a MAC OSX platform with homebrew installed.

set -e
set -x

# Install gcc7 (/opt/gcc7)
pwd
ls
tar -xf deps/gcc-7.3.0.tar.xz
ls
ls deps
cd gcc-7.3.0
mv ../deps/* .
ls
./contrib/download_prerequisites --no-graphite
mkdir -p ~/gcc_build
cd ~/gcc_build
~/gcc-7.3.0/configure --prefix ~/gcc7_install/ --enable-languages=c --disable-bootstrap --enable-nls
make
make install

