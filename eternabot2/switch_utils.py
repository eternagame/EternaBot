import argparse
import os
import sys
import imp
import inv_utils
import json
import re
import vienna_parameters
import csv
import ast
import random

UNSCORABLE = -99999

RNAELEMENT_LOOP = "LOOP"
RNAELEMENT_STACK = "STACK"
DEFAULT_TEMPERATURE = 37.0

class RNAElement:
    def __init__(self):
        self.indices_ = []
        self.type_ = -1
        self.branching_stacks_ = 0
        self.score_ = 0
        self.parent_ = False
        self.children_ = []
        self.quad_scores_ = []

    def get_loop_groups(self):
        if(self.type_ != RNAELEMENT_LOOP):
            return []

        last_index = -999
        last_group = []
        groups = []
        for ii in range(0,len(self.indices_)):
            if(self.indices_[ii] != last_index+1 and last_index >= 0):
                groups.append(last_group)
                last_group = []

            last_group.append(self.indices_[ii])
            last_index = self.indices_[ii]

        if(len(last_group) > 0):
            groups.append(last_group)

        return groups

    def get_stack_length(self):
        if(self.type_ != RNAELEMENT_STACK):
            return 0
        return len(self.indices_)/2

    def get_pair_from_stack(self,pair_index,sequence):
        pair = sequence[self.indices_[pair_index * 2]] + sequence[self.indices_[pair_index * 2 + 1]]
        return pair.upper()

    def get_loop_closing_pairs(self,sequence,pairmap):
        if(self.type_ != RNAELEMENT_LOOP):
            return []

        pairs = []
        pair_indices = []

        if(self.parent_):
            parent = self.parent_
            if(parent.type_ != RNAELEMENT_STACK):
                print "ERROR Loop's parent is not a stack"
                sys.exit(0)

            npi = len(parent.indices_)
            pair = sequence[parent.indices_[npi-2]] + sequence[parent.indices_[npi-1]]
            pairs.append(pair)

        for ii in range(0,len(self.children_)):
            child = self.children_[ii]
            if(child.type_ != RNAELEMENT_STACK):
                print "ERROR Loop's child is not a stack"
                sys.exit(0)

            nci = len(child.indices_)
            pair = sequence[child.indices_[0]] + sequence[child.indices_[1]]
            pairs.append(pair)

        return pairs

def get_pairmap_from_secstruct(secstruct):
    """
    generates dictionary containing pair mappings

    args:
    secstruct contains secondary structure string

    returns:
    dictionary with pair mappings
    """
    pair_stack = []
    pairs_array = []
    i_range = range(0,len(secstruct))

    # initialize all values to -1, meaning no pair
    for ii in i_range:
        pairs_array.append(-1)

    # assign pairs based on secstruct
    for ii in i_range:
        if(secstruct[ii] == "("):
            pair_stack.append(ii)
        elif(secstruct[ii] == ")"):
            index = pair_stack.pop()
            pairs_array[index] = ii
            pairs_array[ii] = index

    return pairs_array

def get_rna_elements_from_secstruct(secstruct):
    """
    get array of pairs and stacks

    args:
    secstruct is the secondary structure

    return:
    list of RNA elements
    """
    elements = []
    pair_stack = []
    pairs_array = []
    i_range = range(0,len(secstruct))

    for ii in i_range:
        pairs_array.append(-1)

    for ii in i_range:
        if(secstruct[ii] == "("):
            pair_stack.append(ii)
        elif(secstruct[ii] == ")"):
            index = pair_stack.pop()
            pairs_array[index] = ii
            pairs_array[ii] = index

    get_rna_elements_from_secstruct_recursive(pairs_array,0,len(secstruct)-1,elements,-999,-999, False)
    return elements

def get_rna_elements_from_secstruct_recursive(pairs_array,start_index,end_index,elements, last_pair_start, last_pair_end, last_parent):
    """
    args:
    pairs_array is array containing the index of the pair of each nucleotide, negative if no pair
    start_index represents the begining of the current sequence
    end_index represents the end of the current sequence
    elements is a list of RNA elements
    last_pair_start contains the start index of the last pair
    last_pair_end contains the end index of the last pair
    last_parent is most recent parent element
    """

    # create a loop element
    new_element = RNAElement()
    new_element.type_ = RNAELEMENT_LOOP

    ii = start_index
    while( ii <= end_index):
        # unpaired nucleotides
        if(pairs_array[ii] < 0):
            new_element.indices_.append(ii)

            # create new stack element including all nucleotides since last pair
            if(last_pair_start >= 0):
                stack_element = RNAElement()
                stack_element.type_ = RNAELEMENT_STACK
                stack_element.parent_ = last_parent
                if(last_parent):
                    last_parent.children_.append(stack_element)

                for jj in range(last_pair_start,ii):
                    stack_element.indices_.append(jj)
                    stack_element.indices_.append(pairs_array[jj])

                elements.append(stack_element)
                last_pair_start = -999
                last_pair_end = -999
                new_element.parent_ = stack_element
                stack_element.children_.append(new_element)

            ii += 1
        # paired nucleotides
        elif(ii < pairs_array[ii]):
            # no unpaired since start of this iteration
            if(ii == start_index and pairs_array[ii] == end_index):
                if(last_pair_start < 0):
                    last_pair_start = ii
                    last_pair_end = pairs_array[ii]
                    last_parent = new_element
                get_rna_elements_from_secstruct_recursive(pairs_array,ii+1,pairs_array[ii]-1,elements,last_pair_start,last_pair_end, last_parent)
                return
            # at least one unpaired since start of this iteration
            else:
                # create stack element including all nucleotides since last pair
                if(last_pair_start >= 0):
                    stack_element = RNAElement()
                    stack_element.type_ = RNAELEMENT_STACK
                    stack_element.parent_ = last_parent
                    if(last_parent):
                        last_parent.children_.append(stack_element)

                    for jj in range(last_pair_start,ii):
                        stack_element.indices_.append(jj)
                        stack_element.indices_.append(pairs_array[jj])

                    elements.append(stack_element)
                    new_element.parent_ = stack_element
                    stack_element.children_.append(new_element)
                    last_pair_start = -999
                    last_pair_end = -999
                # recursively run for every pair
                get_rna_elements_from_secstruct_recursive(pairs_array,ii+1,pairs_array[ii]-1,elements,ii,pairs_array[ii], new_element)
            # skip parts of sequence covered by recursion
            ii = pairs_array[ii]+1
        else:
            print(str(start_index) + " " + str(end_index))
            print("ERROR : should not get here " + str(ii) + " " + str(pairs_array[ii]))
            sys.exit(0)

    if(len(new_element.indices_) > 0):
        elements.append(new_element)

def fill_energy(elements,sequence,pairmap):
    for ii in range(0,len(elements)):

        if(elements[ii].type_ == RNAELEMENT_LOOP):
            loop_groups = elements[ii].get_loop_groups()

            num_loop_groups = len(loop_groups)

            closing_pairs = elements[ii].get_loop_closing_pairs(sequence,pairmap)
            
            num_closing_pairs = len(closing_pairs)

            if(elements[ii].indices_.count(0) > 0 or elements[ii].indices_.count(len(sequence) -1) >0):
                elements[ii].score_ = vienna_parameters.ml_energy(pairmap,sequence,0,True) / 100.0
            else:
                if(num_closing_pairs == 1 and num_loop_groups == 1):
                    hp_start = loop_groups[0][0]
                    hp_end = loop_groups[0][len(loop_groups[0])-1]
                    pair_type = vienna_parameters.pair_type(sequence[hp_start-1],sequence[hp_end+1])
                    size = hp_end - hp_start + 1
                    elements[ii].score_ = vienna_parameters.hairpin_energy(size, pair_type, vienna_parameters.letter_to_sequence_type(sequence[hp_start]), vienna_parameters.letter_to_sequence_type(sequence[hp_end]), sequence, hp_start-1,hp_end+1) / 100.0

                elif(num_closing_pairs == 2):
                    if(num_loop_groups > 2):
                        print "ERROR 2 closing pairs but 3 or more loop groups"
                        sys.exit(0)

                    n1 = 0
                    n2 = 0

                    if(num_loop_groups == 1):
                        n1 = len(loop_groups[0])
                        pi = loop_groups[0][0]-1
                        pj = pairmap[pi]

                        if(pi < pj):
                            i = loop_groups[0][0]-1
                            j = pairmap[i]

                            p = loop_groups[0][n1-1]+1
                            q = pairmap[p]
                        else:
                            q = loop_groups[0][0]-1
                            p = pairmap[q]

                            j = loop_groups[0][n1-1]+1
                            i = pairmap[j]
                    else:
                        n1 = len(loop_groups[0])
                        n2 = len(loop_groups[1])

                        i = loop_groups[0][0]-1
                        j = pairmap[i]

                        p = loop_groups[0][n1-1]+1
                        q = pairmap[p]

                    type1 = vienna_parameters.pair_type(sequence[i],sequence[j])
                    type2 = vienna_parameters.pair_type(sequence[q],sequence[p])

                    if i + 1 >= len(sequence) or j - 1 < 0 or p - 1 < 0 or q + 1 >= len(sequence):
                        elements[ii].score_ = vienna_parameters.ml_energy(pairmap,sequence,0,True) / 100.0
                    else:
                        elements[ii].score_ = vienna_parameters.loop_energy(n1,n2,type1,type2,
                                vienna_parameters.letter_to_sequence_type(sequence[i+1]),
                                vienna_parameters.letter_to_sequence_type(sequence[j-1]),
                                vienna_parameters.letter_to_sequence_type(sequence[p-1]),
                                vienna_parameters.letter_to_sequence_type(sequence[q+1]), True, True) / 100.0
                else:
                    if(num_loop_groups > 0):
                        elements[ii].score_ = vienna_parameters.ml_energy(pairmap,sequence,loop_groups[0][0],False) / 100.0
                    else:
                        parent_elem = elements[ii].parent_

                        if(parent_elem.type_ != RNAELEMENT_STACK):
                            print "ERROR: Multiloop parent is not a stack"
                            sys.exit(0)

                        elements[ii].score_ = vienna_parameters.ml_energy(pairmap,sequence,parent_elem.indices_[len(parent_elem.indices_) -2] + 1,False) / 100.0

        elif(elements[ii].type_ == RNAELEMENT_STACK):
            indices = elements[ii].indices_
            elements[ii].quad_scores_ = []
            total_energy = 0
            type1 = vienna_parameters.pair_type(sequence[indices[0]],sequence[indices[1]])
            for jj in range(2,len(indices)):
                if(jj % 2 == 1):
                    continue
                type2 = vienna_parameters.pair_type(sequence[indices[jj+1]],sequence[indices[jj]])
                quad_energy = vienna_parameters.get_stack_score(type1,type2,True, True)
                total_energy += quad_energy
                type1 = vienna_parameters.reverse_pair_type[type2]
                elements[ii].quad_scores_.append(quad_energy)

            elements[ii].score_ = total_energy / 100.0
        
def load_strategy_from_file(filepath, file_prefix):
    class_inst = None
    expected_class = 'Strategy'

    mod_name,file_ext = os.path.splitext(os.path.split(filepath)[-1])

    if file_ext.lower() == '.py':
        py_mod = imp.load_source(mod_name, filepath)

    elif file_ext.lower() == '.pyc':
        py_mod = imp.load_compiled(mod_name, filepath)

    if expected_class in dir(py_mod):
        class_inst = py_mod.Strategy()

    class_inst.file_prefix_ = file_prefix

    return class_inst

def is_int(str):
    try: 
        int(str)
        return True
    except ValueError:
        return False

def is_float(str):
    try:
        float(str)
        return True
    except ValueError:
        return False

# CSV file should contain the following parameters:
# sequence, site, oligo-seq, on_state, off_state, type
# labtitle, puztitle, soltitle
# for optimization should also include score
def get_switch_designs_from_csv(filename, normalize=False):

    designs = []

    with open(filename) as f:
        # lines = [line.split() for line in f]
        lines = list(csv.reader(f))

        #skip = random.randrange(0, (len(lines) - 100))
        #lineskip = [lines[0]]
        #lineskip.extend(lines[skip:])
        #originallen = len(lines)
        #lines = lineskip

        for i in range(1, len(lines)):

            designs.append({})

            for j in range(0, len(lines[i])):

                designs[i-1][lines[0][j]] = lines[i][j]

                if is_int(designs[i-1][lines[0][j]]):
                    designs[i-1][lines[0][j]] = int(designs[i-1][lines[0][j]])

                elif is_float(designs[i-1][lines[0][j]]):
                    designs[i-1][lines[0][j]] = float(designs[i-1][lines[0][j]])

                if lines[0][j] == "site":
                    designs[i-1][lines[0][j]] = ast.literal_eval(lines[i][j])
                    for k in range(0, len(designs[i-1][lines[0][j]])):
                        designs[i-1][lines[0][j]][k] = int(designs[i-1][lines[0][j]][k])

            # print "Getting design from sequence for " + str(designs[i-1]["soltitle"]) + " (" + str(i + skip) + "/" + str(originallen - 1) + ")"
            print "Getting design from sequence for " + str(designs[i-1]["soltitle"]) + "(" + str(i) + "/" + str(len(lines) - 1) + ")"
            get_design_from_sequence(designs[i-1]["sequence"], designs[i-1])
            print designs[i-1]["state1"]["Vienna1"]["secstruct"]
            print designs[i-1]["state2"]["Vienna1"]["secstruct"]
            print designs[i-1]["state1"]["Vienna2"]["secstruct"]
            print designs[i-1]["state2"]["Vienna2"]["secstruct"]

            #if i -1 > 10: ### TODO Remove
            #    break


        if normalize:
            scores = []
            scoresum = 0
            for i in range(0, len(designs)):
                scores.append(designs[i]['score'])
                scoresum += designs[i]['score']

            mean = scoresum
            if(len(designs) > 0):
                mean = mean / float(len(designs))

            stdev = 0
            for i in range(0, len(designs)):
                stdev += (designs[i]['score'] - mean) * (designs[i]['score'] - mean)

            if(len(designs) > 0):
                stdev = stdev / float(len(designs))

            stdev = math.sqrt(stdev)

            for i in range(0, len(designs)):
                designs[i]['score'] = (designs[i]['score'] - mean) / stdev
                designs[i]['normalize_mean'] = mean
                designs[i]['normalize_stdev'] = stdev

    return designs

def get_fold(sequence, vienna, type, state, on_state, oligoseq, constraint):

    fold_sequence = sequence
    if type == 'miRNA' and state == on_state:
        fold_sequence = sequence + '&' + oligoseq

    if state == on_state and type == "FMN":
        fold = inv_utils.fold(fold_sequence, False, constraint, vienna)[0]
    else:
        fold = inv_utils.fold(fold_sequence, False, False, vienna)[0]

    if type == "miRNA" and state == on_state:
        fold = fold.split('&')[0]

    # Get dotplot without oligo
    """
    if state == on_state and type == "FMN":
        inv_utils.fold(sequence, False, constraint, vienna)[0]
    else:
        inv_utils.fold(sequence, False, False, vienna)[0]
    """

    try:
        file = open("dot.ps", "r")
    except IOError:
        print "Can't find dot.ps!"
        sys.exit()

    dotps = file.read()
    file.close()

    linesU = re.findall('(\d+)\s+(\d+)\s+(\d*\.*\d*)\s+ubox',dotps)
    linesL = re.findall('(\d+)\s+(\d+)\s+(\d*\.*\d*)\s+lbox',dotps)

    dotsU = []
    dotsL = []

    for i in range(0,len(linesU)):
        dotsU.append([int(linesU[i][0]) - 1, int(linesU[i][1]) - 1, float(linesU[i][2])])

    for i in range(0, len(linesL)):
        dotsL.append([int(linesL[i][0]) - 1, int(linesL[i][1]) - 1, float(linesL[i][2])])

    return fold, dotsU, dotsL

# Takes in a partially created design with a sequence, site, etc. and
# calculates information for state1, and state2. This includes the 
# dotplot, secstruct, secstruct_elements, pairmap, and base pair info
# for both vienna1 and vienna2. The exact object format is below.

"""
design = get_design_from_sequence(sequence, design)    

Return format:

    # Calculated
    state1 = design['state1'] # Information for state 1 of the design
    design['state2'] # Information for state 2 of the design

        model = state1['default'] # Foldings using default energy model
        state1['Vienna1'] # Vienna1 is the default energy model 
        state1['Vienna2'] # Vienna2 is the alternate energy model

            model['secstruct']
            model['dotplotU'] # main one
            model['dotplotL']
            model['secstruct_elements']
            model['pairmap']
            model['gc']
            model['gu']
            model['ua']
            model['fe']
            model['meltpoint']
"""

def get_design_from_sequence(sequence, design):

    models = ["Vienna1", "Vienna2"]

    for n in range(1, 3):  # for now only 2 states
        state = 'state' + str(n)
        design[state] = {}
        for m in models:
            design[state][m] = {}
            
            # 1/2): get secstruct and dotplot (upper box and lower box)
            design[state][m]['secstruct'], design[state][m]['dotplotU'], design[state][m]['dotplotL'] = get_fold(sequence, m, design['type'], n, design['on_state'], design['oligoseq'], design['viennaconstraint'])

            """ Just random debugging, ignore me :)
            print "yo: " + sequence
            print "yo: " + m
            print "yo: " + str(design['site'])
            print "yo: " + design['viennaconstraint']
            print "yo: " + design['oligoseq']
            print "yo: " + str(n)
            print "yo: " + design['type']
            print "yo: " + str(design['on_state'])
            print "yo: " + design[state][m]['secstruct']
            """

            # 3) calculate the pairmap
            design[state][m]['pairmap'] = get_pairmap_from_secstruct(design[state][m]['secstruct'])

            # 4): get the elements of the secondary structure
            design[state][m]['secstruct_elements'] = get_rna_elements_from_secstruct(design[state][m]['secstruct'])

            # print sequence
            # print design[state][m]['secstruct']
            # for i in design[state][m]['secstruct_elements']:
               # print i.type_
               # print i.indices_

            # print

            fill_energy(design[state][m]['secstruct_elements'], sequence, design[state][m]['pairmap'])

            # 5): Calculate the total free energy and the melting point
            elements = design[state][m]['secstruct_elements']
            total_energy = 0.0
            for kk in range(0,len(elements)):
                total_energy += elements[kk].score_
            design[state][m]['fe'] = total_energy
            design[state][m]['meltpoint'] = 97

            # 6): Calculate base pair information
            gc_count = 0
            gu_count = 0
            au_count = 0

            pairmap = design[state][m]['pairmap']

            for ii in range(0,len(pairmap)):
                if(pairmap[ii] > ii):
                    pair = sequence[ii] + sequence[pairmap[ii]]
                    pair = pair.upper()

                    if(pair == "GC" or pair == "CG"):
                        gc_count += 1
                    elif(pair == "GU" or pair == "UG"):
                        gu_count += 1
                    elif(pair == "AU" or pair == "UA"):
                        au_count += 1
                    else:
                        print("Wrong pair type " + pair)

            design[state][m]['gc'] = gc_count
            design[state][m]['gu'] = gu_count
            design[state][m]['ua'] = au_count

        design[state]['default'] = design[state][models[0]]

    return design