import sys
import re
import urllib
import random
import switch_utils
import httplib2
import json
import csv
import os

def run_all():

    trainingSet = switch_utils.get_switch_designs_from_csv("training.csv")

    dirList = os.listdir("strategy/")
    for fname in dirList:
        if re.search('\.py$', fname):
            strategy = switch_utils.load_strategy_from_file('strategy/' + fname, "strategy")
            strategy.load_opt_params()
            strategy.set_normalization(trainingSet, strategy.default_params_)


def main():
    run_all()

if __name__ == "__main__":
    main()