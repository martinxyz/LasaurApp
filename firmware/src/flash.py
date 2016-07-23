#!/usr/bin/env python3
"build and flash using the backend's scripts and config"

import os, sys, subprocess

def run(args):
    print(*args)
    subprocess.check_call(args)

# os.chdir('../../backend')
try:
    run(['python3', '../../backend/build.py'] + sys.argv[1:])
    run(['python3', '../../backend/flash.py'] + sys.argv[1:])
except subprocess.CalledProcessError:
    sys.exit(1)
