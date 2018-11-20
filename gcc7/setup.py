#!/usr/bin/env python

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
from distutils.dir_util import mkpath, copy_tree
from codecs import open
import os
from os.path import join
import sys
import re
import shutil
import glob
import subprocess
import argparse
import platform
from wheel.bdist_wheel import bdist_wheel, pep425tags

# We overload the setup.py with some extra arguments
parser = argparse.ArgumentParser()
parser.add_argument(
    '--gcc-install-prefix',
    help='Path to the GCC install prefix.'
)
(args_extra, argv) = parser.parse_known_args()
sys.argv = [sys.argv[0]] + argv  # Write the remaining arguments back to `sys.argv` for distutils to read
assert (args_extra.gcc_install_prefix)


def _script_path():
    """Returns the path to the dir this script is in"""
    return os.path.dirname(os.path.realpath(__file__))


def _find_data_files(root_path, regex_exclude=None, regex_include=None):
    """Return a list of paths relative to `root_path` of all files rooted in `root_path`"""
    root_path = os.path.abspath(root_path)
    ret = []
    for root, _, filenames in os.walk(root_path):
        for fname in filenames:
            fullname = join(root, fname)
            if regex_exclude is None or not re.search(regex_exclude, fullname):
                if regex_include is None or re.search(regex_include, fullname):
                    ret.append(fullname.replace("%s/" % root_path, ""))
    return ret


def _copy_files(glob_str, dst_dir):
    """Copy files using the `glob_str` and copy to `dst_dir`"""
    mkpath(dst_dir)
    for fname in glob.glob(glob_str):
        if os.path.isfile(fname):
            if ".dylib" in fname:
                # We need this HACK because osx might not preserve the write and exec permission
                out_path = join(dst_dir, os.path.basename(fname))
                shutil.copyfile(fname, out_path)
                subprocess.check_call("chmod a+x %s" % out_path, shell=True)
            else:
                shutil.copy(fname, dst_dir)
            print("copy: %s => %s" % (fname, dst_dir))


def _copy_dirs(src_dir, dst_dir):
    """Copy dir"""
    mkpath(dst_dir)
    copy_tree(src_dir, dst_dir)
    print("copy %s => %s" % (src_dir, dst_dir))


def _update_rpath(filename_list, rpath):
    """Update the RPATH of the files in `filename_list`"""

    if platform.system() == "Darwin":
        return

    for filename in filename_list:
        cmd = "patchelf --set-rpath '%s' %s" % (rpath, filename)
        print(cmd)
        subprocess.check_call(cmd, shell=True)


# Copy the GCC installation into the python package root
_copy_dirs(args_extra.gcc_install_prefix, join(_script_path(), "gcc7", "gcc_root"))

if platform.system() == "Linux" and False:
    libs = glob.glob(join(_script_path(), "gcc7", "gcc_root", "lib64", "libatomic*.so"))
    libs += glob.glob(join(_script_path(), "gcc7", "gcc_root", "lib64", "libgcc*.so"))
    libs += glob.glob(join(_script_path(), "gcc7", "gcc_root", "lib64", "libgomp*.so"))
    libs += glob.glob(join(_script_path(), "gcc7", "gcc_root", "lib64", "libquadmath*.so"))
    libs += glob.glob(join(_script_path(), "gcc7", "gcc_root", "lib64", "libssp*.so"))
    print(libs)

    all_files = {}
    for file_path in libs:
        file_name = os.path.basename(file_path)
        assert (file_name not in all_files)
        all_files[file_name] = file_path

    # Update the RPATH of the Python extensions to look in the current directory
    _update_rpath(all_files, '$ORIGIN')

elif platform.system() == "Darwin":
    libs = glob.glob(join(_script_path(), "gcc7", "gcc_root", "lib", "libatomic*"))
    libs += glob.glob(join(_script_path(), "gcc7", "gcc_root", "lib", "libgcc_s*"))
    libs += glob.glob(join(_script_path(), "gcc7", "gcc_root", "lib", "libgomp*"))
    libs += glob.glob(join(_script_path(), "gcc7", "gcc_root", "lib", "libquadmath*"))
    libs += glob.glob(join(_script_path(), "gcc7", "gcc_root", "lib", "libssp*"))
    print(libs)

    all_files = {}
    for file_path in libs:
        file_name = os.path.basename(file_path)
        assert (file_name not in all_files)
        all_files[file_name] = file_path

    # Make the search paths relative
    for file_path in libs:
        cmd = "otool -L %s" % file_path
        otool_res = subprocess.check_output(cmd, shell=True).decode('utf-8')
        for line in otool_res.splitlines()[1:]:  # Each line in `otool_res` represents a linking path (except 1. line)
            dylib_path = line.strip().split()[0]
            dylib_name = os.path.basename(dylib_path)
            if os.path.basename(dylib_path) in all_files:
                load_path = " @loader_path%s" % all_files[dylib_name].replace(os.path.dirname(file_path), "")
                cmd = "install_name_tool -change %s %s %s" % (dylib_path, load_path, file_path)
                print(cmd)
                subprocess.check_output(cmd, shell=True)

    # Make the install_name relative
    gcc_lib_path = join(args_extra.gcc_install_prefix, "lib")
    for file_path in libs:
        cmd = "otool -D %s" % file_path
        otool_res = subprocess.check_output(cmd, shell=True).decode('utf-8')
        for line in otool_res.splitlines()[1:]:  # Each line in `otool_res` represents a linking path (except 1. line)
            dylib_path = line.strip().split()[0]
            if gcc_lib_path in dylib_path:
                run_path = dylib_path.replace(gcc_lib_path, "@rpath")
                cmd = 'install_name_tool -id %s %s' % (run_path, file_path)
                print(cmd)
                subprocess.check_output(cmd, shell=True)

# Get the long description from the README file
with open(os.path.join(_script_path(), '../README.md'), encoding='utf-8') as f:
    long_description = f.read()


# We have to manually set the package tags. At this point, setuptools thinks that this is a pure python package.
class taged_bdist_wheel(bdist_wheel):
    def finalize_options(self):
        bdist_wheel.finalize_options(self)
        self.root_is_pure = False

    def get_tag(self):
        if platform.system() == "Linux":  # Building on Linux, we assume `manylinux1_x86_64`
            plat_name = "manylinux1_x86_64"
        else:
            plat_name = pep425tags.get_platform()
        return ("py2.py3", "none", plat_name)


setup(
    cmdclass={'bdist_wheel': taged_bdist_wheel},
    name='gcc7',
    version="0.0.6",
    description='GCC v7 binaries',
    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/bh107/python-gcc',

    # Author details
    author='Mads R. B. Kristensen',
    author_email='madsbk@gmail.com',

    # Choose your license
    license='GPL',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: End Users/Desktop',
        'Topic :: Multimedia',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: GNU General Public License (GPL)',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
    ],

    # What does your project relate to?
    keywords='gcc',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    # packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    packages=['gcc7'],

    package_data={
        'gcc7': _find_data_files(join(_script_path(), "gcc7"), regex_exclude="\.pyc|\.py")
    },
)
