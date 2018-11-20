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
make &> log.txt # travis cannot handle that much output
make install
cd ~/gcc7_install/
#rm -R share
#find . -name "*.a" -type f|xargs rm -f

# Stripping unneeded data in the binaries
find ./libexec/gcc/x86_64-pc-linux-gnu/7.3.0 -maxdepth 1 -type f -size +10M -print0 | xargs -0 \
    strip --strip-unneeded --remove-section=.comment --remove-section=.note

ls -Rlh
du -sh

