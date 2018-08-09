import os
import platform

file_path = os.path.realpath(__file__)
spl = file_path.split("/")
base_dir = "/".join(spl[:-1])

S = None
if platform.system() == 'Linux':
    OS = 'linux'
elif platform.system() == 'Darwin':
    OS = 'osx'
else:
    raise SystemError(platform.system() + " is not supported currently")

RESOURCE_DIR = os.path.join(base_dir, "resources")
STRATEGY_DIR = os.path.join(base_dir, "strategies")
PUZZLE_DIR = os.path.join(RESOURCE_DIR, "puzzles")
VIENNA_DIR = os.path.join(RESOURCE_DIR, "vienna") + "/" + OS + "/"
NUPACK_DIR = os.path.join(RESOURCE_DIR, "nupack")

