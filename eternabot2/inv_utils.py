import sys
import random
import vienna_parameters
import os
import subprocess
import random
import re
from subprocess import Popen, PIPE, STDOUT
import thread, time, sys
from threading import Timer


DEFAULT_TEMPERATURE = 37.0
BASES = ['A','U','G','C']

def fold(seq, cotransc=False, constraint=False, viennaVersion="Vienna1"):

    # run ViennaRNA
    if constraint:
        options = "-C"
        input = seq + "\n" + constraint
    else:
        options = ""
        input = ''.join(seq)

    op = "--noPS"
    if viennaVersion == "Vienna1":
        op = "-noPS"

    if cotransc:
        p = Popen(['./rnafold/CoFold' + viennaVersion, '--distAlpha', '0.5', '--distTau', '640', op, '-p', options], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
    elif '&' in seq:
        p = Popen(['./rnafold/RNAcofold' + viennaVersion, '-T','37.0', op, '-p', options], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
    else:
        p = Popen(['./rnafold/RNAfold' + viennaVersion, '-T','37.0', op, '-p', options], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
    pair= p.communicate(input=input)[0]
    p.wait()

    # split result by whitespace
    toks = re.split('\s+| \(?\s?',pair)
    ret= []
    ret.append(toks[1])
    ret.append(toks[2][1:-1])

    return ret
