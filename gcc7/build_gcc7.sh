#!/bin/bash
# Use this script on a MAC OSX platform with homebrew installed.

set -e
set -x
cd ~/

# Install gcc7 (/opt/gcc7)
wget ftp://ftp.fu-berlin.de/unix/languages/gcc/releases/gcc-7.2.0/gcc-7.2.0.tar.gz
tar -xzf gcc-7.2.0.tar.gz
cd gcc-7.2.0
pwd
./contrib/download_prerequisites
mkdir -p ~/gcc_build
cd ~/gcc_build
~/gcc-7.2.0/configure --prefix ~/gcc7_install/ --enable-languages=c --disable-bootstrap --enable-nls
make 2> ~/gcc_build.err || true
tail ~/gcc_build.err
make install

