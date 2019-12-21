#!/usr/bin/env python

# Postprocessing performs basic algorithms on Redis data
#
# This software is part of the EEGsynth project, see <https://github.com/eegsynth/eegsynth>.
#
# Copyright (C) 2017-2019 EEGsynth project
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from numpy import log, log2, log10, exp, power, sqrt, mean, median, var, std, mod
<<<<<<< HEAD
from numpy.random import rand, randn
=======
from numpy import random
>>>>>>> 71c0d3df8c6df126a86dc2ac9929dc17977a9f1c
import configparser
import argparse
import numpy as np
import os
import redis
import sys
import time

if hasattr(sys, 'frozen'):
    path = os.path.split(sys.executable)[0]
    file = os.path.split(sys.executable)[-1]
elif sys.argv[0] != '':
    path = os.path.split(sys.argv[0])[0]
    file = os.path.split(sys.argv[0])[-1]
else:
    path = os.path.abspath('')
    file = os.path.split(path)[-1] + '.py'

# eegsynth/lib contains shared modules
sys.path.insert(0, os.path.join(path,'../../lib'))
import EEGsynth

# these function names can be used in the equation that gets parsed
from EEGsynth import compress, limit, rescale, normalizerange, normalizestandard

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--inifile", default=os.path.join(path, os.path.splitext(file)[0] + '.ini'), help="optional name of the configuration file")
args = parser.parse_args()

config = configparser.ConfigParser(inline_comment_prefixes=('#', ';'))
config.read(args.inifile)

try:
    r = redis.StrictRedis(host=config.get('redis', 'hostname'), port=config.getint('redis', 'port'), db=0, charset='utf-8', decode_responses=True)
    response = r.client_list()
except redis.ConnectionError:
    raise RuntimeError("cannot connect to Redis server")

# combine the patching from the configuration file and Redis
patch = EEGsynth.patch(config, r)

# this can be used to show parameters that have changed
monitor = EEGsynth.monitor()

# get the options from the configuration file
debug = patch.getint('general', 'debug')

<<<<<<< HEAD
=======
def rand(x):
    # the input variable is ignored
    return np.asscalar(random.rand(1))

def randn(x):
    # the input variable is ignored
    return np.asscalar(random.randn(1))
>>>>>>> 71c0d3df8c6df126a86dc2ac9929dc17977a9f1c

def sanitize(equation):
    equation.replace(' ', '')
    equation = equation.replace('(', '( ')
    equation = equation.replace(')', ' )')
    equation = equation.replace('+', ' + ')
    equation = equation.replace('-', ' - ')
    equation = equation.replace('*', ' * ')
    equation = equation.replace('/', ' / ')
    equation = equation.replace(',', ' , ')
<<<<<<< HEAD
=======
    equation = equation.replace('>', ' > ')
    equation = equation.replace('<', ' < ')
>>>>>>> 71c0d3df8c6df126a86dc2ac9929dc17977a9f1c
    equation = ' '.join(equation.split())
    return equation

# assign the initial values
for item in config.items('initial'):
    val = patch.getfloat('initial', item[0])
    patch.setvalue(item[0], val, debug=(debug>0))
    monitor.update(item[0], val)

# get the input and output options
<<<<<<< HEAD
input_name, input_variable = list(zip(*config.items('input')))
output_name, output_equation = list(zip(*config.items('output')))
=======
if len(config.items('input')):
    input_name, input_variable = list(zip(*config.items('input')))
else:
    input_name, input_variable = ([], [])
if len(config.items('output')):
    output_name, output_equation = list(zip(*config.items('output')))
else:
    output_name, output_equation = ([], [])
>>>>>>> 71c0d3df8c6df126a86dc2ac9929dc17977a9f1c

# make the equations robust against sub-string replacements
output_equation = [sanitize(equation) for equation in output_equation]

if debug>0:
    print('===== input variables =====')
    for name,variable in zip(input_name, input_variable):
        monitor.update(name, variable)
    print('===== output equations =====')
    for name,equation in zip(output_name, output_equation):
        monitor.update(name, equation)
    print('============================')

while True:
    monitor.loop()
    time.sleep(patch.getfloat('general', 'delay'))

    if debug>1:
        print('============================')

    input_value = []
    for name in input_name:
        val = patch.getfloat('input', name, debug=(debug>1))
        input_value.append(val)

    for key, equation in zip(output_name, output_equation):
        # replace the variable names in the equation by the values
        for name, value in zip(input_name, input_value):
            if value is None and equation.count(name)>0:
                print('Undefined value: %s' % (name))
            else:
                equation = equation.replace(name, str(value))

        # try to evaluate the equation
        try:
            val = eval(equation)
            if debug>1:
                print('%s = %s = %g' % (key, equation, val))
            patch.setvalue(key, val)
        except ZeroDivisionError:
            # division by zero is not a serious error
            patch.setvalue(equation[0], np.NaN)
        except:
            print('Error in evaluation: %s = %s' % (key, equation))
