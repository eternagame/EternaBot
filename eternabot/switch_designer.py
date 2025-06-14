import eterna_utils, design_utils, inv_utils
import ensemble_design, sequence_graph
import varna, draw_utils
import settings
import math, random
import unittest
import sys
import multiprocessing

class SwitchDesigner(object):

    def __init__(self, id, type, beginseq, constraints, targets, **kwargs):
        # sequence information
        self.id = id
        self.type = type
        self.beginseq = beginseq
        self.sequence = beginseq
        self.n = len(self.sequence)
        self.constraints = constraints

        self.mode = kwargs.get("mode", "nupack")
        add_rcs = kwargs.get("add_rcs", False)
        self.strandbonus = kwargs.get("strandbonus", False)
        self.print_ = kwargs.get("print_", False)
        self.inputs = kwargs.get("inputs", {})
        self.aptamer = False

        self.targets = self.parse_targets(targets)
        self.sequence_graph = sequence_graph.SequenceGraph(self.inputs, targets, constraints, beginseq, add_rcs, False, autocomplement=True)
        self.target_oligo_conc = 1e-7

        # scoring
        if "scoring" in kwargs:
            if kwargs["scoring"] == "bpp":
                self.scoring_func = design_utils.get_bpp_scoring_func(targets)
            elif kwargs["scoring"] == "ensemble":
                self.scoring_func = design_utils.get_ensemble_scoring_func()
            elif kwargs["scoring"] == "landing":
                self.scoring_func = design_utils.get_strategy_scoring_func("eli_landing_lane")
            elif kwargs["scoring"] == "null":
                self.scoring_func = None
            else:
                raise ValueError("invalid scoring function: %s" % kwargs["scoring"])
        else:
            self.scoring_func = design_utils.get_bpp_scoring_func(targets)

        #if type == "multi_input_oligo":
        self.bp_distance_func = design_utils.bp_distance_with_unpaired
        self.greedy = False
        self.oligo_conc = 1e-7
        #else:
        #    self.bp_distance_func = design_utils.bp_distance_with_constraint
        if self.mode == "hairpin":
            self.hp_mismatch = False

        # target information
        self.n_targets = len(self.targets)
        if "pos" in self.inputs:
            self.input_pos = self.inputs['pos']
            self.input_pos.insert(0,0)
            del self.inputs['pos']
        else:
            self.input_pos = [0]*(len(self.inputs)+1)
        n_cores = min(16, self.n_targets)
        
        # update dependency graph

        #if type == "multi_input" or type == "multi_input_oligo":
        #    self.create_target_secstructs()
        self.cotrans = False
        
        # print puzzle info
        print self.constraints
        for i in targets:
            print self.get_fold_sequence(self.sequence, i)
            print i['secstruct']
            print i['constrained']
            if 'fold_constraint' in i:
                print i['fold_constraint']

        self.update_current(*self.get_sequence_info(self.sequence))
        
        # maintain sequences
        self.update_best()
        self.all_solutions = []

    def parse_targets(self, targets):
        """
        generate full secondary structure and constraint strings
        """
        for target in targets:
            secstruct = ""
            constrained = ""
            if target['type'] == 'oligos' and len(target['inputs']) > 0 and '&' not in target['secstruct']:
                for input in target['inputs']:
                    secstruct += '.'*len(self.inputs[input]) + '&'
                    constrained += 'o'*len(self.inputs[input]) + 'x'
                target['secstruct'] = secstruct + target['secstruct']
                target['constrained'] = constrained + target['constrained']
            elif target['type'] == 'aptamer':
                self.aptamer = float(target['concentration'])
                fold_constraint = list(target['secstruct'])
                for i, fold in enumerate(fold_constraint):
                    if i in target['site'] and fold == ".":
                        fold_constraint[i] = "x"
                    elif i not in target['site']:
                        fold_constraint[i] = "."
                target['fold_constraint'] = "".join(fold_constraint)
            if '&' in target['secstruct']:
                breaks = [i for i, char in enumerate(target['secstruct']) if char == '&']
                constrained = list(target['constrained'])
                for i in breaks:
                    constrained[i] = 'x'
                target['constrained'] = "".join(constrained)
        return targets

    def get_fold_sequence(self, sequence, objective):
        """ append oligo sequences separated by & for type oligo """
        if objective['type'] == 'oligo':
            return '&'.join([sequence, objective['oligo_sequence']])
        elif objective['type'] == 'oligos':
            if self.mode == "nupack" or self.mode == "vienna":
                return '&'.join([self.inputs[x] for x in sorted(objective['inputs'])] + [sequence])
            # get positions of inputs
            fold_seq = ""
            for i,input in enumerate(sorted(self.inputs)):
                # add portion of sequence between two inputs
                fold_seq += sequence[self.input_pos[i]:self.input_pos[i+1]]
                # add input sequence
                if input in objective['inputs']:
                    if self.mode == "ghost":
                        fold_seq += design_utils.rc(self.inputs[input])
                    elif i == len(self.inputs)-1:
                        fold_seq += self.get_hairpin(design_utils.rc(self.inputs[input]), False, self.hp_mismatch)
                    else:
                        fold_seq += self.get_hairpin(design_utils.rc(self.inputs[input]), True, self.hp_mismatch)
                else:
                    fold_seq += design_utils.rc(self.inputs[input])
            return fold_seq + sequence[self.input_pos[-1]:]
        else:
            return sequence 

    def get_solution(self):
        """
        return current best as solution
        """
        for i in range(self.n_targets):
            fold_sequence = self.get_fold_sequence(self.best_sequence, self.targets[i])
            print fold_sequence
            if self.mode == "ghost":
                print inv_utils.fold(fold_sequence, self.cotrans, self.targets[i]['fold_constraint'])[0]
            elif self.mode == "hairpin" or self.mode == "vienna":
                if self.targets[i]['type'] == "aptamer":
                    print inv_utils.fold(fold_sequence, self.cotrans, self.targets[i]['fold_constraint'])[0]
                else:
                    print inv_utils.fold(fold_sequence, self.cotrans)[0]
            else:
                print inv_utils.nupack_fold(fold_sequence, self.target_oligo_conc)[0]
        return [self.best_sequence, self.best_bp_distance, self.best_design_score]

    def draw_solution(self, name):
        """ draw each state for current solution """
        # initiate varna RNA visualizer
        v = varna.Varna()
        
        # get puzzle object and generate colormaps for each objective
        n = len(self.inputs)
        colormap = draw_utils.get_colormaps(self.targets, self.inputs, self.input_pos, self.n, self.linker_length, self.design_linker, n)
        
        # draw image for each condition
        for i, target in enumerate(self.targets):
            filename = "%s/images/%s_%s-%s.png" % (settings.PUZZLE_DIR, self.id, name, i)
            draw_utils.draw_secstruct_state(v, target, self.get_fold_sequence(self.sequence, target), colormap, filename)

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

    def get_design_score(self, sequence, secstruct, energies=False):
        """
        calculates design score using scoring function
        """
        # in a small number of cases, get_design function causes error
        # if this happens, assume 0 score
        #try:
        if energies:
            return energies[0] - energies[1]
        if not self.scoring_func:
            return 0
        designs = []
        for i in range(self.n_targets):
            if self.mode == "ghost":
                designs.append(eterna_utils.get_design_from_sequence(sequence[i], secstruct[i], self.targets[i]['fold_constraint']))
            elif self.mode == "nupack":
                designs.append(eterna_utils.get_design_from_sequence(sequence[i], secstruct[i], nupack=self.oligo_conc))
            else:
                designs.append(eterna_utils.get_design_from_sequence(sequence[i], secstruct[i]))
        score = self.scoring_func(designs)
        return score
        #except:
        #    return 0

    def get_hairpin(self, seq, begin, mismatch):
        """ turn sequence into hairpin """
        n = (len(seq)-4)/2
        if begin:
            hairpin = seq[0:n] + seq[n:len(seq)-n] + design_utils.rc(seq[0:n])
            i = -n/2
        else:
            hairpin = design_utils.rc(seq[-n:]) + seq[n:len(seq)-n] + seq[-n:]
            i = n/2
        if mismatch:
            hairpin = ensemble_design.get_sequence_array(hairpin)
            hairpin[i] = design_utils.get_different_base(hairpin[i])
            return ensemble_design.get_sequence_string(hairpin)
        return hairpin

    def get_sequence_info(self, sequence):
        """
        get sequence information - native fold, bp distance, pairmap, design
        for a particular sequence
        """
        native = [""] * self.n_targets
        energies = [0] * self.n_targets
        fold_sequences = []
        if self.mode == "nupack":
            p = multiprocessing.Pool(self.n_targets)
        for i in range(self.n_targets):
            fold_sequence = self.get_fold_sequence(sequence, self.targets[i])
            fold_sequences.append(fold_sequence)
            if self.mode == "ghost":
                native[i] = inv_utils.fold(fold_sequence, self.cotrans, self.targets[i]['fold_constraint'])[0]
            elif self.mode == "hairpin" or self.mode == "vienna":
                if self.targets[i]['type'] == "aptamer":
                    fold_list = inv_utils.fold(fold_sequences[i], self.cotrans, self.targets[i]['fold_constraint'])
                else:
                    fold_list = inv_utils.fold(fold_sequences[i], self.cotrans)
                fold = fold_list[0]
                energy = fold_list[1]
                native[i] = fold
            if self.aptamer:
                energies[i] = energy
            if self.mode == "nupack":
                if isinstance(self.targets[i]['inputs'], dict):
                    native[i] = p.apply_async(inv_utils.nupack_fold, args=(fold_sequence, self.targets[i]['inputs'].values()))
                else:
                    native[i] = p.apply_async(inv_utils.nupack_fold, args=(fold_sequence, self.oligo_conc))
        if self.mode == "nupack":
            p.close()
            p.join()
            native = [x.get() for x in native]
            native = [[x[0], x[2]] for x in native]
        if self.aptamer:
            design_score = self.get_design_score(fold_sequences, native, energies)
            bp_distance = self.score_secstructs(native, energies, sequence)
        else:
            design_score = max(self.get_design_score(fold_sequences, native),0)
            bp_distance = self.score_secstructs(native, sequence=sequence)
        return [sequence, native, bp_distance, fold_sequences, design_score]

    def reset_sequence(self):
        """
        reset sequence to the start sequence (for rerunning optimization)
        """
        self.sequence_graph.reset_sequence(self.beginseq)
        self.update_current(self.beginseq)
        self.update_best()
        self.all_solutions = []
        if self.print_:
            print "reset %s" % self.sequence

    def update_current(self, sequence, native=None, bp_distance=None, score=None, energies=None):
        """
        updates current sequence and related information
        """
        self.sequence = sequence
        if not native:
            [sequence, native, bp_distance, fold_sequences, design_score] = self.get_sequence_info(sequence)
            score = self.get_design_score(fold_sequences, native)
        self.native = native
        self.bp_distance = bp_distance
        self.design_score = score

    def update_best(self):
        """
        updates best to current sequence
        """
        self.best_sequence = self.sequence
        self.best_native = self.native
        self.best_bp_distance = self.bp_distance
        self.best_design_score = self.design_score

    def score_secstructs(self, secstruct, energies = False, sequence = False):
        """
        calculates sum of bp distances for with and without oligo

        returns:
        sum of bp distances with and without the oligo 
        """
        # test for secondary structure matches
        distance = 0.0
        strands_interacting = 0.0
        n_strands = 0.0
        for i in range(self.n_targets):
            if "threshold" in self.targets[i]:
                distance += self.bp_distance_func(secstruct[i], self.targets[i]['secstruct'], self.targets[i]['constrained'], self.targets[i]['threshold'])
            else:
                distance += self.bp_distance_func(secstruct[i], self.targets[i]['secstruct'], self.targets[i]['constrained'])
            if self.mode == "nupack":
                strands = secstruct[i][0].split("&")
                for strand in secstruct[i][1]:
                    if strand != len(strands):
                        n_strands += 1
                        if "(" in strands[strand-1] or ")" in strands[strand-1]:
                            strands_interacting += 1

        # add bonus for interaction of strands
        if self.strandbonus:
            if strands_interacting == 0:
                strands_interacting += 1
            distance /= strands_interacting/n_strands
            if self.print_:
                print "bonus: %d" % distance

        # test energies
        if energies:
            if energies[1] - 0.6 * math.log(self.aptamer/3.0) > energies[0]:
                distance += 4

        # test sequence
        if sequence:
            distance += 1 * sequence.count("GGGG")
            distance += 1 * sequence.count("CCCC")
            distance += 1 * sequence.count("AAAAA")

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
        return self.score_secstructs(self.best_native) == 0 and self.oligo_conc == self.target_oligo_conc

    def optimize_sequence(self, n_iterations, n_cool = 50, greedy = None, cotrans = None, print_ = None, start_oligo_conc=1, continue_opt=False):
        """
        monte-carlo optimization of the sequence

        args:
        n_interations is the total number of iterations
        n_cool is the number of times to cool the system
        """
        bases = "GAUC"
        pairs = ["GC", "CG", "AU", "UA"]
    
        if greedy != None:
            self.greedy = greedy
        if cotrans != None:
            self.cotrans = cotrans
        if print_ != None:
            self.print_ = print_

        #print self.targets
        #self.optimize_start_sequence()

        T = 5.0
        self.oligo_conc = start_oligo_conc

        def p_dist(dist, new_dist):
            """probability function"""
            return math.exp(-(new_dist-dist)/T)

        def p_greedy(dist, new_dist):
            if new_dist <= dist:
                return 1
            else:
                return 0

        if self.greedy:
            p_func = p_greedy
        else:
            p_func = p_dist

        niter = None

        # loop as long as bp distance too large or design score too small
        for i in range(n_iterations):
            #random.shuffle(index_array)
            
            # pick random nucleotide in sequence
            mut_sequence = self.sequence_graph.mutate()
            [mut_sequence, native, bp_distance, fold_sequences, design_score] = self.get_sequence_info(mut_sequence)

            if self.best_bp_distance != 0 and bp_distance == 0:
                niter = i
                print i
            
            # if distance or score is better for mutant, update the current sequence
            p = p_func(self.bp_distance, bp_distance)
            if(random.random() <= p):
                if self.bp_distance == bp_distance and p_func(self.design_score, design_score):
                    continue
                self.update_current(mut_sequence, native, bp_distance, design_score)
                if self.print_:
                    print self.sequence, self.bp_distance, self.design_score
                    print "conc: %s" % self.oligo_conc
                    for j in range(self.n_targets):
                        print self.native[j]
                    print ""
                        #print self.get_fold_sequence(self.sequence, self.targets[j])
            
                # if distance or score is better for mutant than best, update the best sequence    
                if(bp_distance < self.best_bp_distance or
                   (bp_distance == self.best_bp_distance and design_score > self.best_design_score)):
                    self.update_best()

            if self.best_bp_distance == 0 and self.oligo_conc == self.target_oligo_conc and not continue_opt:
                return i

            # decrease temperature
            #if i % (n_iterations/n_cool) == 0:
            wait = 0
            interval = n_iterations/(2*n_cool)
            if i % interval == 0 and i >= interval*wait and i < interval*(n_cool+wait):
                T -= 0.1
                if T < 1:
                    T = 1
            
            # update oligo_conc
            if self.best_bp_distance == 0:
                if self.oligo_conc > self.target_oligo_conc:
                    if self.oligo_conc/10 <= self.target_oligo_conc:
                        self.oligo_conc = self.target_oligo_conc
                    else:
                        self.oligo_conc /= 10
                self.update_current(self.sequence)
                self.update_best()
                print self.native, self.bp_distance
                print self.best_native, self.best_bp_distance
            #    self.all_solutions.append([mut_sequence, score])
        
        return niter

class test_functions(unittest.TestCase):

    def setUp(self):
        self.puzzle = read_puzzle_json('switch_input.json')

    def test_check_secstructs(self):
        sequence = "ACAAGCUUUUUGCUCGUCUUAUACAUGGGUAAAAAAAAAACAUGAGGAUCACCCAUGUAAAAAAAAAAAAAAAAAAA"
        self.puzzle.update_current(*self.puzzle.get_sequence_info(sequence))
        self.assertTrue(self.puzzle.check_current_secstructs())

    def test_optimize_sequence(self):
        sequence = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACAUGAGGAUCACCCAUGUAAAAAAAAAAAAAAAAAAA"
        self.puzzle.update_current(*self.puzzle.get_sequence_info(sequence))
        self.puzzle.optimize_sequence(1000)
        print self.puzzle.get_solution()

