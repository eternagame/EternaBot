import sys, os
import numpy as np

sys.path.append('eternabot')

from sequence_designer import SequenceDesigner
from mea.mea import predict_MEA_structure

n_solutions=1
puzzle_ind=4

puzzle=[
'......((((((((((((((....(((((((((((((....)))))))))))))))))))))))))))(((((((....))))))).....................',
'......(((((.((((....((......(((((.(((....))).))))).)))))).))))).....(((((((....))))))).....................',
'........((.((((.(.((((.((...((((....)).)).)).)).)).)..))))..))......(((((((....))))))).....................',
'......(((..((((.(((((((....))).))))....((((.(((....))))))).))))..)))(((((((....))))))).....................',
'........((((..((((....)))).(((..(((...(((.(....).))).)))..)))..)))).(((((((....))))))).....................']

constraints = 'GGAAA' + 'N'*(len(puzzle[puzzle_ind])-22)+'AAAAGAAACAACAACAACAAC'
designer = SequenceDesigner()
vienna_solutions = designer.design(puzzle[puzzle_ind], constraints, count=n_solutions)


designer = SequenceDesigner()
contrafold_solutions = designer.design(puzzle[puzzle_ind], constraints, contrafold=True, count=n_solutions)

print "Vienna check vienna"
for x in vienna_solutions:
	mea_struct, mea = predict_MEA_structure(x.sequence)
	if mea_struct == puzzle[puzzle_ind]:
		print mea
	else:
		print 'Doesnt match', mea_struct, mea

print "Contrafold check vienna"
for x in vienna_solutions:
	mea_struct, mea = predict_MEA_structure(x.sequence, contrafold=True)
	if mea_struct == puzzle[puzzle_ind]:
		print mea
	else:
		print 'Doesnt match', mea_struct, mea


print "Vienna check contrafold"
for x in contrafold_solutions:
	mea_struct, mea = predict_MEA_structure(x.sequence)
	if mea_struct == puzzle[puzzle_ind]:
		print mea
	else:
		print 'Doesnt match', mea_struct, mea


print "Contrafold check contrafold"
for x in contrafold_solutions:
	mea_struct, mea = predict_MEA_structure(x.sequence, contrafold=True)
	if mea_struct == puzzle[puzzle_ind]:
		print mea
	else:
		print 'Doesnt match', mea_struct, mea
