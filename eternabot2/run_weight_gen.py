import switch_utils
import inv_utils
import random
import sys
import re
import os
import math
import numpy
import scipy.linalg
import simplejson

def generate_ensemble(designs, strategies, method, title):
    
    # Any design will do, all designs are set to same normalize_mean
    scores_mean = designs[0]['normalize_mean']
    scores_stdev = designs[0]['normalize_stdev']
    my_weights = []

    if method == "L2":

        my_feature_array = []
        my_feature_array_t = []
        my_scores_array = []

        for ii in range(0,len(designs)):
            print "\tScoring " + designs[ii]['sequence']
            my_feature_vector = []
            for ss in range(0,len(strategies)):
                f_score =  strategies[ss].normalized_score(designs[ii],strategies[ss].default_params_)['normalized']
                my_feature_vector.append(f_score)

            my_feature_vector.append(1.0)
            my_feature_array.append(my_feature_vector)
            my_scores_array.append([designs[ii]['score']])

        for ss in range(0,len(strategies)+1):
            my_feature_vector_t = []
            for ii in range(0,len(designs)):
                my_feature_vector_t.append(my_feature_array[ii][ss])
            my_feature_array_t.append(my_feature_vector_t)

        lamb = 85.95482
        lamb_array = []
        for ii in range(0,len(strategies)+1):
            lamb_vector = []
            for jj in range(0,len(strategies)+1):
                lamb_vector.append(0)
            lamb_vector[ii] = lamb
            lamb_array.append(lamb_vector)

        my_feature_matrix = numpy.matrix(my_feature_array)
        my_feature_matrix_t = numpy.matrix(my_feature_array_t)
        my_scores_matrix = numpy.matrix(my_scores_array)
        lamb_diagonal = numpy.matrix(lamb_array)

        temp = (my_feature_matrix_t * my_feature_matrix + lamb_diagonal)
        tempi = scipy.linalg.pinv(temp)
        tempi = tempi * my_feature_matrix_t * my_scores_matrix

        for ii in range(0,len(strategies)+1):
            my_weights.append(float(tempi[ii][0]))

    else:
        # method is sparse model (L1)

        my_weights_walker = 0
        my_feature_array = []
        my_scores_array = []

        for ii in range(0,len(designs)):
            print "\tScoring " + designs[ii]['sequence']

            my_feature_vector = []
            for ss in range(0,len(strategies)):
                # if(weights[ss] != 0): # tab # tab
                f_score =  strategies[ss].normalized_score(designs[ii],strategies[ss].default_params_)['normalized']
                my_feature_vector.append(f_score)

            my_feature_vector.append(1.0)
            my_feature_array.append(my_feature_vector)
            my_scores_array.append([designs[ii]['score']])

        my_feature_matrix = numpy.matrix(my_feature_array)
        my_scores_matrix = numpy.matrix(my_scores_array)
        my_weights_res = scipy.linalg.lstsq(my_feature_matrix, my_scores_matrix)

        for ss in range(0,len(strategies)+1):
            # if(weights[ss] != 0): # tab # tab
            my_weights.append(my_weights_res[0][my_weights_walker][0])
            my_weights_walker += 1
            #else:
            #    my_weights.append(0)

        #num_of_non_zeros = 0
        #for ww in range(0,len(weights)):
        #    if(weights[ww] != 0):
        #        num_of_non_zeros += 1

        #if(my_weights_walker != num_of_non_zeros):
        #    print "Error in sparse ensemble %d %d %d" % (my_weights_walker, num_of_non_zeros, len(strategies)+1)
        #    sys.exit(0)


    fw = open("ensemble/weights_%s_%s.txt" % (method, title), "w")
    fs = open("ensemble/normmean_%s_%s.txt" % (method, title), "w")
    fn = open("ensemble/normstdev_%s_%s.txt" % (method, title), "w")

    fw.write(simplejson.dumps(my_weights))
    fs.write(simplejson.dumps(scores_mean))
    fn.write(simplejson.dumps(scores_stdev))

    fw.close()
    fs.close()
    fn.close()

def run_all():

    trainingSet = switch_utils.get_switch_designs_from_csv("training.csv", True) # normalized scores

    all_strats = []         # Any strategy

    dirList = os.listdir("strategies/")
    for fname in dirList:
        if re.search('\.py$', fname):
            strategy = switch_utils.load_strategy_from_file('strategies/' + fname, "strategies/")
            strategy.load_opt_params()
            strategy.get_normalization(strategy.default_params_)
            all_strats.append(strategy)

    print "L1 Gen for ensemble-all"
    generate_ensemble(trainingSet, all_strats, "L1", "Ensemble-all")

    print "L2 Gen for ensemble-all"
    generate_ensemble(trainingSet, all_strats, "L2", "Ensemble-all")


def main():
    run_all()

if __name__ == "__main__":
    main()