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
~/gcc_src/configure --prefix ~/gcc7_install/ --enable-languages=c --disable-bootstrap --enable-nls --disable-lto --disable-multilib
make &> log.txt
make install
cd ~/gcc7_install/
ls
ls -Rlh
du -sh
cd share
du -sh
cd locale
du -sh



