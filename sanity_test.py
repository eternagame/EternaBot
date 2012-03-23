import eterna_utils
import test_utils
import os
import re
import sys
import math
import numpy
import scipy.linalg

weight_file = open(sys.argv[1],'r')
weights_list = []
for line in weight_file:
	tokens = line.split(' ')
	weights = []
	for ii in range(0,len(tokens)):
		weights.append(float(tokens[ii]))
	
	weights_list.append(weights)
	
weight_file.close()

is_sparse_test = re.search('L2',sys.argv[1]) == None


scores_file = open(sys.argv[2],'r')
scores = []
for line in scores_file:
	scores.append(float(line))
scores_file.close()

features_file = open(sys.argv[3],'r')
feature_score_vectors = []
for line in features_file:
	tokens = line.split(' ')
	score_vector = []
	for ii in range(0,len(tokens)):
		score_vector.append(float(tokens[ii]))
	feature_score_vectors.append(score_vector)
	if(len(score_vector) != len(weights_list[0]) - 1):
		print "feature scores vector does not match weights length"
		sys.exit(0)

if(len(feature_score_vectors) != len(scores)):
	print "AAAA"
	sys.exit(0)


print "Loaded %d scores" % len(scores)

strategy_names = ['merryskies_only_as_in_the_loops', 'aldo_repetition', 'dejerpha_basic_test', 'eli_blue_line', 'clollin_gs_in_place', 'quasispecies_test_by_region_boundaries', 'eli_gc_pairs_in_junction', 'eli_no_blue_nucleotides_in_hook', 'mat747_31_loops', 'merryskies_1_1_loop', 'xmbrst_clear_plot_stack_caps_and_safe_gc', 'jerryp70_jp_stratmark', 'eli_energy_limit_in_tetraloops', 'eli_double_AUPair_strategy', 'eli_green_blue_strong_middle_half', 'eli_loop_pattern_for_small_multiloops', 'eli_tetraloop_similarity', 'example_gc60', 'penguian_clean_dotplot', 'eli_twisted_basepairs', 'aldo_loops_and_stacks', 'eli_direction_of_gc_pairs_in_multiloops_neckarea', 'eli_multiloop_similarity', 'eli_green_line', 'ding_quad_energy', 'quasispecies_test_by_region_loops', 'eli_double_sameturning_GCPair_strategy', 'berex_berex_loop_basic', 'eli_legal_placement_of_GUpairs', 'merryskies_1_1_loop_energy', 'ding_tetraloop_pattern', 'aldo_mismatch', 'eli_tetraloop_blues', 'eli_red_line', 'eli_wrong_direction_of_gc_pairs_in_multiloops', 'deivad_deivad_strategy', 'eli_direction_of_gc_pairs_in_multiloops', 'eli_no_blue_nucleotides_strategy', 'berex_basic_test', 'eli_numbers_of_yellow_nucleotides_pr_length_of_string', 'kkohli_test_by_kkohli']

strategies = []

for ii in range(0,len(strategy_names)):
	strategies.append(eterna_utils.load_strategy_from_file('strategies\\' + strategy_names[ii] + ".py"))

designs = eterna_utils.get_synthesized_designs_from_eterna_server(True)
scores_mean = designs[0]['normalize_mean']
scores_stdev = designs[0]['normalize_stdev']


puznids = test_utils.get_puz_nids(designs)

my_scores = []

for ss in range(0,len(strategies)):
	strategies[ss].load_opt_params()
	strategies[ss].set_normalization(designs,strategies[ss].default_params_)


# feature score calculation sanity check
feature_error = 0
feature_count = 0
feature_max_error = 0
for ii in range(0,len(designs)):
	my_feature_vector = []
	
	for ss in range(0,len(strategies)):
		f_score =  strategies[ss].normalized_score(designs[ii],strategies[ss].default_params_)	
		my_feature_vector.append(f_score)
		
		"""
		if(math.fabs(f_score - feature_score_vectors[ii][ss]) > 0.01):
			print "Something's wrong on design %d %s" % (ii, designs[ii]['soltitle'])
			print strategies[ss].title_ 
			print "Denormalized %d" % strategies[ss].denormalized_
			print "%f %f %f" % (f_score, feature_score_vectors[ii][ss], strategies[ss].score(designs[ii],strategies[ss].default_params_))
		"""
		feature_error += math.fabs(f_score - feature_score_vectors[ii][ss])
		if(feature_max_error < math.fabs(f_score - feature_score_vectors[ii][ss])):
			feature_max_error = math.fabs(f_score - feature_score_vectors[ii][ss])
		feature_count += 1
		my_feature_vector.append(1.0)

print "AVG FEATURE ERROR %f" % (feature_error / float(feature_count))
print "MAX FEATURE ERROR %f" % feature_max_error
		
for kk in range(0,len(puznids)):
	weights = weights_list[kk]
	
	if(len(weights) != len(strategies) + 1):
		print "SHIT something's wrong with weights length"
		sys.exit(0)
	
	set = test_utils.get_leave_one_out_set(designs,puznids[kk])
	train_set = set['train']
	test_set = set['test']
	
	my_weights = []
	
	if(is_sparse_test):
		my_weights_walker = 0
	
		my_feature_array = []
		my_scores_array = []
	
		for ii in range(0,len(train_set)):
			
			my_feature_vector = []
			for ss in range(0,len(strategies)):
				if(weights[ss] != 0):
					f_score =  strategies[ss].normalized_score(train_set[ii],strategies[ss].default_params_)
					my_feature_vector.append(f_score)
					
			my_feature_vector.append(1.0)
			my_feature_array.append(my_feature_vector)	
			my_scores_array.append([train_set[ii]['score']])
					
		my_feature_matrix = numpy.matrix(my_feature_array)
		my_scores_matrix = numpy.matrix(my_scores_array)
		my_weights_res = scipy.linalg.lstsq(my_feature_matrix, my_scores_matrix)
		
		for ss in range(0,len(strategies)+1):
			if(weights[ss] != 0):
				my_weights.append(my_weights_res[0][my_weights_walker][0])
				my_weights_walker += 1
			else:
				my_weights.append(0)
		
		num_of_non_zeros = 0
		for ww in range(0,len(weights)):
			if(weights[ww] != 0):
				num_of_non_zeros += 1
		
		if(my_weights_walker != num_of_non_zeros):
			print "C8c8c8c8c %d %d" % (my_weights_walker, len(strategies)+1) 
			sys.exit(0)
				
		#print "MY WEIGHTS %s" % str(my_weights)
		
		weights_error = 0
		weights_max_error = 0
		for ss in range(0,len(strategies)+1):
			weights_error += math.fabs(my_weights[ss] - weights[ss])
			if(weights_max_error < math.fabs(my_weights[ss] - weights[ss])):
				weights_max_error = math.fabs(my_weights[ss] - weights[ss])
			
		print "LOO %d MY WEIGHTS AVG ERROR %f" % (kk,weights_error / float(num_of_non_zeros))
		print "LOO %d MY WEIGHTS MAX ERROR %f" % (kk,weights_max_error)
	
	else:
		my_feature_array = []
		my_feature_array_t = []
		my_scores_array = []
	
		for ii in range(0,len(train_set)):
			
			my_feature_vector = []
			for ss in range(0,len(strategies)):
				f_score =  strategies[ss].normalized_score(train_set[ii],strategies[ss].default_params_)
				my_feature_vector.append(f_score)
					
			my_feature_vector.append(1.0)
			my_feature_array.append(my_feature_vector)	
			my_scores_array.append([train_set[ii]['score']])
		
		for ss in range(0,len(strategies)+1):
			my_feature_vector_t = []
			for ii in range(0,len(train_set)):
				my_feature_vector_t.append(my_feature_array[ii][ss])
			my_feature_array_t.append(my_feature_vector_t)
		
		lambs = [284.718329387102, 80.6862348725417, 185.498967348039, 86.8083688022185, 80.8932410592556, 104.871964815312, 88.5243662215937, 97.0417665198446, 15.8674763173261, 91.3851019685528]
		lamb = lambs[kk]
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
			my_weights.append(tempi[ii][0])
		
		weights_error = 0
		weights_max_error = 0
		for ss in range(0,len(strategies)+1):
			weights_error += math.fabs(my_weights[ss] - weights[ss])
			if(weights_max_error < math.fabs(my_weights[ss] - weights[ss])):
				weights_max_error = math.fabs(my_weights[ss] - weights[ss])
			
		print "LOO %d MY WEIGHTS AVG ERROR %f" % (kk,weights_error / float(len(strategies)+1))
		print "LOO %d MY WEIGHTS MAX ERROR %f" % (kk,weights_max_error)
	
	for ii in range(0,len(test_set)):
		my_score = 0

		for ss in range(0,len(strategies)):
			if(weights[ss] != 0):
				f_score =  strategies[ss].normalized_score(test_set[ii],strategies[ss].default_params_)
				my_score += my_weights[ss] * f_score

		my_score += my_weights[len(weights)-1]
		my_score = my_score * scores_stdev + scores_mean
		
		my_scores.append(my_score)
				

if(len(my_scores) != len(designs)):
	print "AASDASDFASD"
	sys.exit(0)

errorsum = 0
error_max = 0
for ii in range(0,len(my_scores)):
	errorsum += math.fabs(scores[ii] - my_scores[ii]) 
	if(error_max < math.fabs(scores[ii] - my_scores[ii])):
		error_max = math.fabs(scores[ii] - my_scores[ii])


print "AVG SCORE ERROR %f" % (errorsum / len(my_scores))
print "MAX SCORE ERROR %f" % (error_max)


print "TESTING FINAL CLASSIFIER"

scores = []
sparse_final_scores_file = open(sys.argv[5],'r')
for line in sparse_final_scores_file:
	scores.append(float(line))
sparse_final_scores_file.close()



weights = []
sparse_final_weights_file = open(sys.argv[4],'r')
for line in sparse_final_weights_file:
	weights.append(float(line))
sparse_final_weights_file.close()

if(len(weights) != len(strategies) + 1):
	print "FSDAFASD"
	sys.exit(0)

if(len(scores) != len(designs)):
	print "AAAAAAAADASDFSDA %d %d" %(len(scores), len(designs))
	sys.exit(0)

my_weights_walker = 0
my_feature_array = []
my_scores_array = []
my_weights = []
for ii in range(0,len(designs)):
	
	my_feature_vector = []
	for ss in range(0,len(strategies)):
		if(weights[ss] != 0):
			f_score =  strategies[ss].normalized_score(designs[ii],strategies[ss].default_params_)
			my_feature_vector.append(f_score)
			
	my_feature_vector.append(1.0)
	my_feature_array.append(my_feature_vector)	
	my_scores_array.append([designs[ii]['score']])
			
my_feature_matrix = numpy.matrix(my_feature_array)
my_scores_matrix = numpy.matrix(my_scores_array)
my_weights_res = scipy.linalg.lstsq(my_feature_matrix, my_scores_matrix)

for ss in range(0,len(strategies)+1):
	if(weights[ss] != 0):
		my_weights.append(my_weights_res[0][my_weights_walker][0])
		my_weights_walker += 1
	else:
		my_weights.append(0)

num_of_non_zeros = 0
for ww in range(0,len(weights)):
	if(weights[ww] != 0):
		num_of_non_zeros += 1

if(my_weights_walker != num_of_non_zeros):
	print "C8c8c8c8c %d %d" % (my_weights_walker, len(strategies)+1) 
	sys.exit(0)
		
#print "MY WEIGHTS %s" % str(my_weights)

weights_error = 0
weights_max_error = 0
for ss in range(0,len(strategies)+1):
	weights_error += math.fabs(my_weights[ss] - weights[ss])
	if(weights_max_error < math.fabs(my_weights[ss] - weights[ss])):
		weights_max_error = math.fabs(my_weights[ss] - weights[ss])


print "SCORE NORMALIZATION %f %f" % (scores_mean, scores_stdev)
print "SPARSE FINAL WEIGHTS AVG ERROR %f" % (weights_error / float(num_of_non_zeros))
print "SPARSE FINAL WEIGHTS MAX ERROR %f" % (weights_max_error)



weights = []
L2_final_weights_file = open(sys.argv[6],'r')
for line in L2_final_weights_file:
	weights.append(float(line))
L2_final_weights_file.close()

my_feature_array = []
my_feature_array_t = []
my_scores_array = []

for ii in range(0,len(designs)):
	
	my_feature_vector = []
	for ss in range(0,len(strategies)):
		f_score =  strategies[ss].normalized_score(designs[ii],strategies[ss].default_params_)
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

my_weights = []
for ii in range(0,len(strategies)+1):
	my_weights.append(tempi[ii][0])

weights_error = 0
weights_max_error = 0
for ss in range(0,len(strategies)+1):
	weights_error += math.fabs(my_weights[ss] - weights[ss])
	if(weights_max_error < math.fabs(my_weights[ss] - weights[ss])):
		weights_max_error = math.fabs(my_weights[ss] - weights[ss])
	
print "L2 WEIGHTS AVG ERROR %f" % (weights_error / float(len(strategies)+1))
print "L2 WEIGHTS MAX ERROR %f" % (weights_max_error)
	









errorsum = 0
errormax = 0
for ii in range(0,len(designs)):
	my_score = 0

	for ss in range(0,len(strategies)):
		if(weights[ss] != 0):
			f_score =  strategies[ss].normalized_score(designs[ii],strategies[ss].default_params_)
			my_score += my_weights[ss] * f_score

	my_score += my_weights[len(weights)-1]
	my_score = my_score * scores_stdev + scores_mean
	s_error = math.fabs(my_score - scores[ii])
	
	errorsum += s_error
	if(errormax < s_error):
		errormax = s_error
		
print "FINAL SCORES AVG ERROR %f" % (errorsum / float(len(designs)))
print "FINAL SCORES MAX ERROR %f" % (errormax)

		
