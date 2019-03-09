import numpy as np
import argparse, sys

def convert_dotbracket_to_matrix(s):
    triu_inds = np.triu_indices(len(s))
    m = np.zeros([len(s),len(s)])
    bp1=[]
    bp2=[]
    for i, char in enumerate(s):
        if char=='(':
            bp1.append(i)
        if char==')':
            bp2.append(i)
    for i in list(reversed(bp1)):
        for j in bp2:
            if j > i:
                m[i,j]=1.0
                bp2.remove(j)
                break
    return m

def convert_matrix_to_dotbracket(m):
    print('not implemented yet! whoops.')
    pass

def load_matrix_or_dbn(s):
    try:
        struct = np.loadtxt(s) # load as base pair matrix
        assert struct.shape[0] == struct.shape[1]
    except:
        try: # load as dot-bracket string

            dbn_struct = open("./%s" % s,'r').read().rstrip()
            
            struct = convert_dotbracket_to_matrix(dbn_struct)
        except:
            raise ValueError('Unable to parse structure %s' % s)
    return struct

def score_ground_truth(pred_matrix, true_matrix):
    '''Score a predicted structure against a true structure,
     input as NxN base pair matrix (takes top triangle).'''

    N = pred_matrix.shape[0]

    assert pred_matrix.shape[1] == N
    assert true_matrix.shape[0] == N
    assert true_matrix.shape[1] == N

    true = true_matrix[np.triu_indices(N)]
    pred = pred_matrix[np.triu_indices(N)]

    TP, FP, cFP, TN, FN = 0, 0, 0, 0, 0 

    for i in range(len(true)):
        if true[i] == 1:
            if pred[i] == 1: 
                TP += 1
            else:
                FN += 1
        elif true[i] == 0:
            if pred[i] == 0: 
                TN += 1
            else: 
                FP +=1
                #check for compatible false positive
                a,b = np.triu_indices(N)
                if np.sum(true_matrix,axis=0)[a[i]]+ np.sum(true_matrix,axis=0)[b[i]]==0:
                   cFP +=1

    sen = TP/(TP + FN)
    ppv = TP/(TP + FP - cFP)
    mcc = (TP*TN - (FP - cFP)*FN)/np.sqrt((TP + FP - cFP)*(TP + FN)*(TN + FP - cFP)*(TN + FN))
    fscore = 2*TP/(2*TP + FP - cFP + FN)
    return sen, ppv, mcc, fscore, N