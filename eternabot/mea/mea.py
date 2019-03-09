import numpy as np
import argparse, sys, os
from mea_utils import *
from subprocess import *
import settings

def predict_MEA_structure(sequence, contrafold=False,
    gamma_min=-7, gamma_max=7, 
    verbose=True, metric='mcc'):
    '''Estimate maximum expected pseudoaccuracy structures per Hamada et al. BMC Bioinf 2010 11:586.
    
    Note: Files in matrix_dir and true_structs need to have the same names corresponding
        to their same constructs, but suffixes don't matter.
        
    Inputs:

    sequence: nucleotide sequence.
    gamma_min, gamma_max: min/max log_2(gamma) value used, defaults are -7 and 7.
    metric: keyword-based, which metric to use to select structure. Options are 'sen', 'ppv', 'mcc', 'fscore'.

    verbose: print output or not (for command line use)

    Returns:

    str, float: predicted MEA structure, value of maximum expected accuracy

    '''

    metric_ind = ['sen', 'ppv', 'mcc', 'fscore'].index(metric)
    gamma_vals = [x for x in range(gamma_min, gamma_max)]
    metrics_across_gammas = {k:[] for k in gamma_vals}
    running_best_value = 0
    running_best_metrics = []

    matrix = bpps(sequence, contrafold=contrafold)

    for g in gamma_vals:

        cls = MEA(matrix, gamma=2**g)

        metrics = cls.score_expected() #sen, ppv, mcc, fscore
        metrics_across_gammas[g].append(metrics)

        if metrics[metric_ind] > running_best_value:
            running_best_value = metrics[metric_ind]
            running_best_metrics = metrics
            running_best_gamma = g
            running_best_struct = cls.structure

    for g in gamma_vals:

        [sen, ppv, mcc, fscore] = np.mean(metrics_across_gammas[g], axis=0)
        #print('gamma_avg\t%d\t%.3f\t%.3f\t%.3f\t%.3f' % (g, sen, ppv, mcc, fscore))

    # print('Best avg metrics using individual gammas')
    #[sen, ppv, mcc, fscore] = np.mean(np.array(best_metrics), axis=0)

    # if not os.path.exists(output_dir):
    #     os.mkdir(output_dir)

    # for struct, ind in list(zip(best_structs, pdb_indices)):
    #     if os.path.exists('%s/%s.dbn' % (output_dir, ind)):
    #         print('NB: overwriting existing predicted structure')
    #     with open('%s/%s.dbn' % (output_dir, ind), 'w') as f:
    #         f.write(struct)

    return running_best_struct, running_best_value

def bpps(sequence, contrafold=False):
    if contrafold:
        return bpps_contrafold_(sequence)
    else:
        return bpps_vienna_(sequence)

def bpps_vienna_(sequence):
    p = Popen([settings.VIENNA_DIR + 'RNAfold', '-p'], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
    pair = p.communicate(input=''.join(sequence))[0]
    os.remove('rna.ps')
    probs=np.zeros([len(sequence), len(sequence)])
    with open('dot.ps','r') as f:
        for line in f.readlines():
            if 'ubox' in line and len(line.split())==4:
                try:
                    i, j, p, _ = line.split()
                    i, j, p = int(i)-1, int(j)-1, float(p)
                    probs[i,j] = p
                except:
                    pass
    os.remove('dot.ps')
    return probs

def bpps_contrafold_(sequence):
    contrafold_fname = 'contrafold_tmp.fasta'
    posterior_fname = 'tmp.posteriors'

    with open(contrafold_fname,'w') as f:
        f.write(sequence)

    p = Popen([settings.CONTRA_DIR+'contrafold', 'predict', contrafold_fname, '--posteriors', '0.001', posterior_fname],stdout=PIPE, stdin=PIPE, stderr=STDOUT)
    stdout, stderr = p.communicate()

    probs=np.zeros([len(sequence), len(sequence)])

    for line in open(posterior_fname).readlines():
        if len(line.split(':')) > 1:
            first_ind = int(line.split()[0])-1
            for x in line.split()[2:]:
                second_ind = int(x.split(':')[0])-1
                p = float(x.split(':')[1])
                probs[first_ind, second_ind] = p

    os.remove(contrafold_fname)
    os.remove(posterior_fname)
    return probs

class MEA:
    def __init__(self, bpps, gamma = 1.0, debug=False):
        self.debug = debug
        self.bpps = bpps
        self.N=self.bpps.shape[0]
        self.gamma = gamma
        self.W = np.zeros([self.N,self.N])
        self.MEA_bp_list = []
        self.structure = ['.']*self.N
        self.MEA_bp_matrix = np.zeros([self.N,self.N])
        self.tb = np.zeros([self.N,self.N])
        self.min_hp_length=3
        self.evaluated = False
        
    def fill_W(self, i, j):
        options = [self.W[i+1, j], self.W[i, j-1], (self.gamma+1)*self.bpps[i,j] + self.W[i+1, j-1] - 1,\
                np.max([self.W[i,k] + self.W[k+1, j] for k in range(i+1,j)])]
        self.W[i,j] = np.max(options) 
        self.tb[i,j] = np.argmax(options) #0: 5' pass, 1: 3' pass, 2: bp, 3: multiloop
        
    def run_MEA(self):
        # fill weight matrix
        for length in range(self.min_hp_length, self.N):
            for i in range(self.N-length):
                j = i + length
                self.fill_W(i,j)
                
        self.traceback(0,self.N-1)
        
        for x in self.MEA_bp_list:
            self.MEA_bp_matrix[x[0],x[1]]=1
            self.structure[x[0]]='('
            self.structure[x[1]]=')'
        
        self.structure = ''.join(self.structure)
        if not self.evaluated: self.evaluated = True
        
    def traceback(self, i, j):
        if j <= i:
            return
        elif self.tb[i,j] == 0: #5' neighbor
            if self.debug: print(i,j, "5'")
            self.traceback(i+1,j)
        elif self.tb[i,j] == 1: #3' neighbor
            if self.debug: print(i,j, "3'")
            self.traceback(i,j-1)
        elif self.tb[i,j] == 2: # base pair
            if self.debug: print(i,j,'bp')
            self.MEA_bp_list.append((i,j))
            self.traceback(i+1,j-1)
        else: #multiloop
            for k in range(i+1,j):
                if self.W[i,j] == self.W[i, k] + self.W[k+1,j]:
                    if self.debug: print(i,j,"multiloop, k=",k)
                    self.traceback(i,k)
                    self.traceback(k+1,j)
                    break

    def score_expected(self):
        '''Compute expected values of TP, FP, etc from predicted MEA structure.

         Returns: 
         pseudoexpected SEN, PPV, MCC, F-score'''

        if not self.evaluated: self.run_MEA()

        pred_m = self.MEA_bp_matrix[np.triu_indices(self.N)]
        probs = self.bpps[np.triu_indices(self.N)]

        TP = np.sum(np.multiply(pred_m, probs)) + 1e-6
        TN = 0.5*self.N*self.N-1 - np.sum(pred_m) - np.sum(probs) + TP + 1e-6
        FP = np.sum(np.multiply(pred_m, 1-probs)) + 1e-6
        FN = np.sum(np.multiply(1-pred_m, probs)) + 1e-6

        a,b = np.triu_indices(self.N)
        cFP = 1e-6
        for i in range(len(pred_m)):
            if np.sum(self.MEA_bp_matrix,axis=0)[a[i]] + np.sum(self.MEA_bp_matrix,axis=0)[b[i]]==0:
               cFP += np.multiply(pred_m[i], 1-probs[i])

        sen = TP/(TP + FN)
        ppv = TP/(TP + FP - cFP)
        mcc = (TP*TN - (FP - cFP)*FN)/np.sqrt((TP + FP - cFP)*(TP + FN)*(TN + FP - cFP)*(TN + FN))
        fscore = 2*TP/(2*TP + FP - cFP + FN)

        return [sen, ppv, mcc, fscore]
