#!python -u

# Copyright (c) 2013 Citrix Systems Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms,
# with or without modification, are permitted provided
# that the following conditions are met:
#
# * Redistributions of source code must retain the above
# copyright notice, this list of conditions and the
# following disclaimer.
# * Redistributions in binary form must reproduce the above
# copyright notice, this list of conditions and the
# following disclaimer in the documentation and/or other
# materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
# CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.

import os, sys
import tarfile
import subprocess

def get_configuration(debug):
    configuration = 'Windows Vista'

    if debug:
        configuration += ' Debug'
    else:
        configuration += ' Release'

    return configuration

def shell(command):
    print(command)
    sys.stdout.flush()

    process = subprocess.Popen(command, shell=True, bufsize=1, stdout=subprocess.PIPE)

    with process.stdout as pipe:
        for line in pipe:
            line = line.decode("utf-8")
            line = line.strip()
            print(line)

class msbuild_failure(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

def msbuild(name, arch, debug):
    configuration = get_configuration(debug)
    os.environ['CONFIGURATION'] = configuration

    set_platform(arch)

    cwd = os.getcwd()
    os.chdir('proj')
    status = shell('msbuild.bat')
    os.chdir(cwd)

    if (status != None):
        raise msbuild_failure(configuration)

def set_platform(arch):
    if arch == 'x86':
        os.environ['PLATFORM'] = 'Win32'
    elif arch == 'x64':
        os.environ['PLATFORM'] = 'x64'

def callfnout(cmd):
    print(cmd)

    sub = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    output = sub.communicate()[0]
    ret = sub.returncode

    if ret != 0:
        raise(Exception("Error %d in : %s" % (ret, cmd)))
    print("------------------------------------------------------------")
    return output.decode('utf-8')

def main(debug):

    set_version()
    set_build_number()
    set_build_variable("xenpong")

    if 'MERCURIAL_REVISION' in os.environ.keys():
        revision = open('revision', 'w')
        print(os.environ['MERCURIAL_REVISION'], file=revision)
        revision.close()

    msbuild('xenpong', 'x86', debug)
    msbuild('xenpong', 'x64', debug)

#    archive_source()
    archive('xenpong.tar', ['xenpong', 'revision'])

def archive_source():
    cmd = ['git', 'archive', '--format=tar.gz', '--prefix=source/', '-o', 'xenpong\\source.tgz', 'master']
    callfnout(cmd)

def archive(filename, files, tgz=False):
    access='w'
    if tgz:
        access='w:gz'
    with tarfile.open(filename, access) as tar:
        for name in files:
            try:
                print('adding ' + name)
                tar.add(name)
            except:
                pass

def set_version():
    os.environ['MAJOR_VERSION'] = '7'
    os.environ['MINOR_VERSION'] = '0'
    os.environ['MICRO_VERSION'] = '0'

def set_build_number():
    if 'BUILD_NUMBER' not in os.environ.keys():
        os.environ['BUILD_NUMBER'] = '0'

def set_build_variable(name):
    os.environ['TARGET'] = 'Build'
    os.environ['SOLUTION'] = name

def print_usage_and_exit():
    print ("Usage: %s <checked|free>" % (sys.argv[0], ))
    sys.exit(1)

if __name__ == '__main__':

    if len(sys.argv) < 2:
        print_usage_and_exit()

    if sys.argv[1] == "checked":
        debug = True
    elif sys.argv[1] == "free":
        debug = False
    else:
        print_usage_and_exit()

    main(debug)
