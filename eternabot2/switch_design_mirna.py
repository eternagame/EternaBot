import inv_utils
import switch_utils
import ensemble_utils
import unittest
import sys
import os
import random
import math
import json
import argparse
import requests
import re

def bp_distance_with_constraint(secstruct1, secstruct2, locks, antisecstruct2, antilocks):
    """
    calculates distance between two secondary structures
    
    args:
    secstruct1 is the first secondary structure
    secstruct2 is the second secondary structure
    locks specifies the positions that are constrained
    
    returns:
    bp distance between structures
    """
    # ensure that secondary structures are the same length
    if(len(secstruct1) != len(secstruct2)):
        print "SS1 and SS2 lengths don't match"
        sys.exit(0)
    
    # generate pair mappings
    pairmap1 = switch_utils.get_pairmap_from_secstruct(secstruct1)
    pairmap2 = switch_utils.get_pairmap_from_secstruct(secstruct2)
    
    # +1 for each pair or single that doesn't match
    dist = 0
    
    for ii in range(0,len(pairmap1)):
        if(locks[ii] == "o"):
            continue
        if(pairmap1[ii] != pairmap2[ii]):
            if(pairmap1[ii] > ii):
                dist += 1
            if(pairmap2[ii] > ii):
                dist += 1

    if not antisecstruct2:
        return dist
    
    antipositions = []
    previouslockwasanti = False

    for antilockindex, antilock in enumerate(antilocks):
        if antilock == "x" and not previouslockwasanti:
            antipositions.append(antilockindex)
            previouslockwasanti = True
        elif antilock != "x" and previouslockwasanti:
            antipositions.append(antilockindex - 1)
            previouslockwasanti = False

    for lockstart,lockend in zip(antipositions[0::2], antipositions[1::2]):
        secstructequals = True
        for lockindex in range(lockstart, lockend):
            if secstruct1[lockindex] != antisecstruct2[lockindex]:
                secstructequals = False
        if secstructequals:
            dist += (lockend - lockstart)

    return dist

def complement(base):
    if base == "G":
        return "C"
    elif base == "C":
        return "G"
    elif base == "U":
        return "A"
    elif base == "A":
        return "U"
    else:
        return "A"

def convert_sequence_constraints(sequence, constraints):
    """
    convert "xo" constraints to "N" constraint format
    """
    result = ""
    for i,letter in enumerate(constraints):
        if letter == 'o':
            result += 'N'
        else:
            result += sequence[i]
    return result

class OligoPuzzle:

    def __init__(self, id, beginseq, constraints, targets, scoring_func, designinfo, inputs = None):
        # sequence information
        self.id = id
        self.beginseq = beginseq
        self.sequence = beginseq
        self.n = len(self.sequence)
        self.constraints = constraints
        self.index_array = self.get_unconstrained_indices()
        self.designinfo = designinfo
        self.scoring_func = scoring_func

        # target information
        self.targets = targets
        self.n_targets = len(self.targets)
        self.single_index = 0
        self.target_pairmap = []
        for i, target in enumerate(self.targets):
            if target['type'] == 'single':
                self.single_index = i
            elif target['type'] == 'aptamer':
                viennaconstraint = list(target['secstruct'])
                for baseind, pair in enumerate(viennaconstraint):
                    if baseind in target["site"] and pair == ".":
                        viennaconstraint[baseind] = "x"
                    elif baseind not in target["site"]:
                        viennaconstraint[baseind] = "."
                target["viennaconstraint"] = "".join(viennaconstraint)

            self.target_pairmap.append(switch_utils.get_pairmap_from_secstruct(target['secstruct']))
        self.inputs = inputs
        self.linker_length = 5
        self.linker = "U"*self.linker_length

        self.update_sequence(*self.get_sequence_info(self.sequence))
        
        # maintain sequences
        self.update_best()
        self.all_solutions = []
        
    def get_unconstrained_indices(self):
        """
        get indices for positions that can change)
        """
        index_array = []
        for ii in range(0,self.n):
            if(self.constraints[ii] == "o"):
                index_array.append(ii)
        return index_array

    def get_solution(self):
        """
        return current best as solution
        """
        for i in range(self.n_targets):
            fold_sequence = self.get_fold_sequence(self.best_sequence, self.targets[i])
            print fold_sequence
            if self.targets[i]['type'] == "aptamer":
                print inv_utils.fold(fold_sequence, False, self.targets[i]['viennaconstraint'])
            else:
                print inv_utils.fold(fold_sequence)[0]
        return [self.best_sequence, self.best_bp_distance, self.best_design_score]

    def get_solutions(self):
        """
        return all possible solutions found
        """
        return self.all_solutions

    def get_random_solution(self):
        """
        return a random solution
        """
        r = random.randint(0, len(self.all_solutions)-1)
        solution = self.all_solutions[r]
        return [solution[0], 0, solution[1]]

    def get_design_score(self, sequence, secstruct):
        """
        calculates overall design score, which is sum of bp distance component and scoring function component
        """
        # in a small number of cases, get_design function causes error
        # if this happens, assume 0 score
        try:

            design = {}
            design['sequence'] = sequence
            design['site'] = self.designinfo['site']
            design['viennaconstraint'] = self.designinfo['viennaconstraint']
            design['oligoseq'] = self.designinfo['oligoseq']
            design['type'] = self.designinfo['type']
            design['on_state'] = self.designinfo['on_state']
            design['off_state'] = self.designinfo['off_state']
            design['puztitle'] = self.designinfo['puztitle']
            design['labtitle'] = self.designinfo['labtitle']

            switch_utils.get_design_from_sequence(sequence, design)
            score = self.scoring_func(design)['finalscore']
            return score
        except:
            return 0

    def get_fold_sequence(self, sequence, objective):
        """ append oligo sequences separated by & for type oligo """
        if objective['type'] == 'oligo':
            return '&'.join([sequence, objective['oligo_sequence']])
        elif objective['type'] == 'oligos':
            inputs = []
            for input in sorted(self.inputs):
                if input in objective['inputs']:
                    inputs.append(self.inputs[input])
                else:
                    inputs.append("U"*len(self.inputs[input]))
            input_sequence = self.linker.join(inputs)
            return '&'.join([sequence, input_sequence])
        else:
            return sequence 

    def get_sequence_info(self, sequence):
        """
        get sequence information - native fold, bp distance, pairmap, design
        for a particular sequence
        """
        native = []
        nativeenergy = []
        native_pairmap = []

        for i in range(self.n_targets):
            fold_sequence = self.get_fold_sequence(sequence, self.targets[i])
            if self.targets[i]['type'] == 'aptamer':
                fold = inv_utils.fold(fold_sequence, False, self.targets[i]['viennaconstraint'])
                foldenergy = fold[1]
                fold = fold[0]
            else:
                fold = inv_utils.fold(fold_sequence)
                foldenergy = fold[1]
                fold = fold[0]
            if self.targets[i]['type'] == "oligos":
                fold = fold.split('&')[0]

            native.append(fold)
            nativeenergy.append(foldenergy)
            native_pairmap.append(switch_utils.get_pairmap_from_secstruct(native[i]))

        bp_distance = self.score_secstructs(native, nativeenergy, sequence)
        design_score = self.get_design_score(sequence, native)
        return [sequence, native, native_pairmap, bp_distance, design_score, nativeenergy]

    def reset_sequence(self):
        """
        reset sequence to the start sequence (for rerunning optimization)
        """
        self.sequence = self.beginseq
        self.update_sequence(*self.get_sequence_info(self.sequence))
        self.update_best()
        self.all_solutions = []

    def optimize_start_sequence(self):
        """
        optimize start sequence to include pairs, etc
        """
        secstruct = self.targets[self.single_index]['secstruct']
        constraints = convert_sequence_constraints(self.beginseq, self.constraints)
        sequence = switch_utils.initial_sequence_with_gc_caps(secstruct, constraints, False)
        self.update_sequence(*self.get_sequence_info(sequence))
        return

    def update_sequence(self, sequence, native, native_pairmap, bp_distance, score, nativeenergy):
        """
        updates current sequence and related information
        """
        self.sequence = sequence
        [sequence, native, native_pairmap, bp_distance, score, nativeenergy] = self.get_sequence_info(sequence)
        self.native = native
        self.nativeenergy = nativeenergy
        self.native_pairmap = native_pairmap
        self.bp_distance = bp_distance
        self.design_score = score

    def update_best(self):
        """
        updates best to current sequence
        """
        self.best_sequence = self.sequence
        self.best_native = self.native
        self.best_nativeenergy = self.nativeenergy
        self.best_native_pairmap = self.native_pairmap
        self.best_bp_distance = self.bp_distance
        self.best_design_score = self.design_score

    def score_secstructs(self, secstruct, energies = False, sequence = False):
        """
        calculates sum of bp distances for with and without oligo

        returns:
        sum of bp distances with and without the oligo 
        """
        distance = 0
        for i in range(self.n_targets):
            distance += bp_distance_with_constraint(secstruct[i], self.targets[i]['secstruct'], self.targets[i]['constrained'], self.targets[i]['antistruct'], self.targets[i]['anticonstrained'])
        
        if energies and (energies[1] == '' or energies[0] == ''):
            #print "Penalty for empty energies"
            distance += 14

        if energies and energies[1] != '' and energies[0] != '' and (float(energies[1]) + 9.93) > (float(energies[0]) + -6.20):
            #print "Penalty for no-binding"
            distance += 14

        if sequence:
            gcount = sequence.count("GGGG")
            ccount = sequence.count("CCCC")
            acount = sequence.count("AAAAA")

            distance += 4 * gcount
            distance += 4 * ccount
            distance += 5 * acount

            #print "Penalty for gcount", str(gcount), "for ccount", str(ccount), "for acount", str(acount)

        if sequence and (sequence.count("A") > len(sequence) * 0.4):
            #print "Penalty for over-A", str(0.4*len(sequence))
            distance += 0.4 * len(sequence)

        #if energies and energies[1] != '' and energies[0] != '':
            #print energies[0], energies[1], distance
            #print

        return distance

    def check_secstructs(self, secstruct):
        """
        checks if current sequence matches target secondary structures
    
        return:
        boolean indicating whether the RNA folds to the targeted structure
        with and without the oligo
        """
        return self.score_secstructs(secstruct) == 0

    def check_current_secstructs(self):
        return self.score_secstructs(self.native, self.nativeenergy, self.sequence) == 0

    def optimize_sequence(self, n_iterations, n_cool):
        """
        monte-carlo optimization of the sequence

        args:
        n_interations is the total number of iterations
        n_cool is the number of times to cool the system
        """
        bases = "GAUC"
        pairs = ["GC", "CG", "AU", "UA"]
    
        if len(self.index_array) == 0:
            return

        #self.optimize_start_sequence()
        T = 5

        def p_dist(dist, new_dist):
            """probability function"""
            if dist == 0:
               return 0
            return math.exp(-(new_dist-dist)/T)

        def p_score(score, new_score):
            """probability function for design scores"""
            return math.exp((new_score-score)/T)
    
        # loop as long as bp distance too large or design score too small
        for i in range(n_iterations):
            #random.shuffle(index_array)
            
            # pick random nucleotide in sequence
            rindex = self.index_array[int(random.random() * len(self.index_array))]
                
            mut_array = switch_utils.get_sequence_array(self.sequence)
            mut_array[rindex] = switch_utils.get_random_base()
            
            mut_sequence = switch_utils.get_sequence_string(mut_array)
            [mut_sequence, native, native_pairmap, bp_distance, score, nativeenergy] = self.get_sequence_info(mut_sequence)

            # if current sequence is a solution, save to list
            if bp_distance == 0:
                self.all_solutions.append([mut_sequence, score])
            
            # if distance or score is better for mutant, update the current sequence
            if(random.random() < p_dist(self.bp_distance, bp_distance) or
               (bp_distance == self.bp_distance and random.random() < p_score(self.design_score, score))):
                self.update_sequence(mut_sequence, native, native_pairmap, bp_distance, score, nativeenergy)
            
                # if distance or score is better for mutant than best, update the best sequence    
                if(bp_distance < self.best_bp_distance or
                   (bp_distance == self.bp_distance and score > self.best_design_score)):
                    self.update_best()

            # decrease temperature
            if i % n_iterations/n_cool == 0:
                T -= 0.1
                if T < 1:
                    T = 1
        
        return

def read_puzzle_json(text):
    """
    read in puzzle as a json file
    """
    data = json.loads(text)['data']
    p = data['puzzle']
    id = data['nid']

    #if p['rna_type'] == 'single':
    #    return SequenceDesigner(id, p['secstruct'], p['locks'])

    # get basic parameters
    beginseq = p['beginseq']
    constraints = p['locks']
    if p['rna_type'] == "multi_input":
        inputs = p['inputs']
    else:
        inputs = None

    # load in objective secondary structures
    objective = json.loads(p['objective'])
    secstruct = [] 
    for o in objective:
        n = len(o['secstruct'])
        # if no constrained bases, all are unconstrained
        if 'structure_constrained_bases' not in o.keys() and 'anti_structure_constrained_bases' not in o.keys():
            constrained = switch_utils.get_sequence_array('x'*n)
            anticonstrained = switch_utils.get_sequence_array('x'*n)
        # otherwise, combine structure and antistructure constraints
        else:
            constrained = switch_utils.get_sequence_array('o'*n)
            anticonstrained = switch_utils.get_sequence_array('o'*n)

            struct = switch_utils.get_sequence_array(o['secstruct'])
            
            if 'anti_secstruct' in o.keys():
                antistruct = switch_utils.get_sequence_array(o['anti_secstruct'])
            else:
                antistruct = False

            # modified to include more than one sequence of constrained bases
            if 'structure_constrained_bases' in o.keys() and len(o['structure_constrained_bases']) > 0:

                for lo,hi in zip(o['structure_constrained_bases'][0::2], o['structure_constrained_bases'][1::2]):
                    # [lo, hi] = o['structure_constrained_bases']
                    for i in range(int(lo), int(hi)+1):
                        if i < len(constrained):
                            constrained[i] = 'x'
                del o['structure_constrained_bases']
            
            # modified to include more than one sequence of constrained bases
            if 'anti_structure_constrained_bases' in o.keys() and len(o['anti_structure_constrained_bases']) > 0:
                for lo,hi in zip(o['anti_structure_constrained_bases'][0::2], o['anti_structure_constrained_bases'][1::2]):
                    # [lo, hi] = o['anti_structure_constrained_bases']
                    for i in range(int(lo), int(hi)+1):
                        if i < len(anticonstrained):
                            anticonstrained[i] = 'x'
                        # struct[i] = '.'
                del o['anti_structure_constrained_bases']

            o['secstruct'] = switch_utils.get_sequence_string(struct)
            if antistruct:
                o['antistruct'] = switch_utils.get_sequence_string(antistruct)
            else:
                o['antistruct'] = False

        o['constrained'] = switch_utils.get_sequence_string(constrained)
        o['anticonstrained'] = switch_utils.get_sequence_string(anticonstrained)
        secstruct.append(o)

    # create design info for eternabot
    designinfo = {}
    designinfo["labtitle"] = ""
    designinfo["puztitle"] = p['title']

    objective = json.loads(p['objective'])
    for i in range(0, len(objective)):
        if objective[i]["type"] == "oligo":
            oligoseq = objective[i]["oligo_sequence"]
            site = []
            type = "miRNA"
            viennaconstraint = ""
        elif objective[i]["type"] == "aptamer":
            type = "FMN"
            site = objective[i]["site"]
            oligoseq = ""
            viennaconstraint = list(objective[i]["secstruct"])
            for baseind, pair in enumerate(viennaconstraint):
                if baseind in site and pair == ".":
                    viennaconstraint[baseind] = "x"
                elif baseind not in objective[i]["site"]:
                    viennaconstraint[baseind] = "."
            viennaconstraint = "".join(viennaconstraint)

        elif objective[i]["type"] == "single":
            off_state = (i + 1)
            on_state = (off_state % 2) + 1

    designinfo['oligoseq'] = oligoseq
    designinfo['type'] = type
    designinfo['viennaconstraint'] = viennaconstraint
    designinfo['site'] = site
    designinfo['off_state'] = off_state
    designinfo['on_state'] = on_state

    # create scoring function

    all_strats = []         # Any strategy

    dirList = os.listdir("strategies-Single/code/")
    for fname in dirList:
        if re.search('\.py$', fname):
            strategy = switch_utils.load_strategy_from_file('strategies-Single/code/' + fname, "strategies-Single/code/")
            strategy.load_opt_params()
            strategy.get_normalization(strategy.default_params_)
            all_strats.append(strategy)

    dirList = os.listdir("strategies-Both/code/")
    for fname in dirList:
        if re.search('\.py$', fname):
            if fname != "jandersonlee_shape_stable_against_mutation.py":
                strategy = switch_utils.load_strategy_from_file('strategies-Both/code/' + fname, "strategies-Both/code/")
                strategy.load_opt_params()
                strategy.get_normalization(strategy.default_params_)
                all_strats.append(strategy)

    dirList = os.listdir("strategies-FMN/code/")
    for fname in dirList:
        if re.search('\.py$', fname):
            strategy = switch_utils.load_strategy_from_file('strategies-FMN/code/' + fname, "strategies-FMN/code/")
            strategy.load_opt_params()
            strategy.get_normalization(strategy.default_params_)
            all_strats.append(strategy)

    dirList = os.listdir("strategies-miRNA/code/")
    for fname in dirList:
        if re.search('\.py$', fname):
            strategy = switch_utils.load_strategy_from_file('strategies-miRNA/code/' + fname, "strategies-miRNA/code/")
            strategy.load_opt_params()
            strategy.get_normalization(strategy.default_params_)
            all_strats.append(strategy)

    ensemble = ensemble_utils.Ensemble("L1", all_strats, "ensemble-all")

    puzzle = OligoPuzzle(id, beginseq, constraints, secstruct, ensemble.score, designinfo, inputs)
    return puzzle

class OneStratEnsemble:
    def __init__(self, strategy):
        self.title_ = strategy.title_
        self.author_ = strategy.author_
        self.strategy_ = strategy
        self.method_ = "Top"

    def score(self, design):
        return self.strategy_.score(input_designs[ii], self.strategy_.default_params_)


def optimize_n(puzzle, niter, ncool, n, submit, fout):
    if fout:
        with open(fout, 'a') as f:
	        f.write("# %s iterations, %s coolings\n" % (niter, ncool))

    # run puzzle n times
    solutions = []
    scores = []
    i = 0 
    attempts = 0
    while i < n:
        puzzle.reset_sequence()
        puzzle.optimize_sequence(niter, ncool)
        if puzzle.check_current_secstructs():
            sol = puzzle.get_solution()
            if sol[0] not in solutions:
                solutions.append(sol[0])
                scores.append(sol[2])
                print sol
                if submit:
                    post_solution(puzzle, 'solution %s' % i)
                if fout:
                    with open(fout, 'a') as f:
                        f.write("%s\t%1.6f\n" % (sol[0], sol[2]))
                i += 1
                attempts = 0
        else:
            #niter += 500
            attempts += 1
            if attempts == 10:
                break
        print "%s sequence(s) calculated" % i
    return [solutions, scores, f]

def get_puzzle(id):
    """
    get puzzle with id number id from eterna server
    """
    r = requests.get('http://nando.eternadev.org/get/?type=puzzle&nid=%s' % id)
    return read_puzzle_json(r.text)

"""
def post_solution(puzzle, title):
    sequence = puzzle.best_sequence
    fold = inv_utils.fold(sequence)
    design = switch_utils.get_design_from_sequence(sequence, fold[0])
    header = {'Content-Type': 'application/x-www-form-urlencoded'}
    login = {'type': 'login',
             'name': 'theeternabot',
             'pass': 'iamarobot',
             'workbranch': 'main'}
    solution = {'type': 'post_solution',
                'puznid': puzzle.id,
                'title': title,
                'body': 'eternabot switch v1, score %s' % puzzle.best_design_score,
                'sequence': sequence,
                'energy': fold[1],
                'gc': design['gc'],
                'gu': design['gu'],
                'ua': design['ua'],
                'melt': design['meltpoint'],
                'pointsrank': 'false',
                'recommend-puzzle': 'true'}

    url = "http://jnicol.eternadev.org"
    #url = 'http://eterna.cmu.edu'
    loginurl = "%s/login/" % url
    posturl = "%s/post/" % url
    with requests.Session() as s:
        r = s.post(loginurl, data=login, headers=header)
        r = s.post(posturl, data=solution, headers=header)
    return
"""

class test_functions(unittest.TestCase):

    def setUp(self):
        self.puzzle = read_puzzle_json('switch_input.json')

    def test_check_secstructs(self):
        sequence = "ACAAGCUUUUUGCUCGUCUUAUACAUGGGUAAAAAAAAAACAUGAGGAUCACCCAUGUAAAAAAAAAAAAAAAAAAA"
        self.puzzle.update_sequence(*self.puzzle.get_sequence_info(sequence))
        self.assertTrue(self.puzzle.check_current_secstructs())

    def test_optimize_sequence(self):
        sequence = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACAUGAGGAUCACCCAUGUAAAAAAAAAAAAAAAAAAA"
        self.puzzle.update_sequence(*self.puzzle.get_sequence_info(sequence))
        self.puzzle.optimize_sequence(1000)
        print self.puzzle.get_solution()

def main():
    p = argparse.ArgumentParser()
    p.add_argument('puzzleid', help="name of puzzle filename or eterna id number", type=str)
    p.add_argument('-s', '--nsol', help="number of solutions", type=int, default=1)
    p.add_argument('-i', '--niter', help="number of iterations", type=int, default=1000)
    p.add_argument('-c', '--ncool', help="number of times to cool", type=int, default=20)
    p.add_argument('--submit', help="submit the solution(s)", default=False, action='store_true')
    p.add_argument('--nowrite', help="suppress write to file", default=False, action='store_true')
    args = p.parse_args()

    puzzlefile = "puzzles/" + "%s.json" % args.puzzleid
    if os.path.isfile(puzzlefile): 
        with open(puzzlefile, 'r') as f:
            puzzle = read_puzzle_json(f.read())
    else:
        puzzle = get_puzzle(args.puzzleid)
    if not args.nowrite:
        fout = "puzzles/" + args.puzzleid + ".out"
    else:
        fout = False
    [solutions, scores, fout] = optimize_n(puzzle, args.niter, args.ncool, args.nsol, args.submit, fout)

    if fout:
        fout.close()

if __name__ == "__main__":
    #unittest.main()
    main()


