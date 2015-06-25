import os
import argparse
import urllib
import json
import eterna_utils
import inv_utils


def string_dist(string1, string2):
    if len(string1) != len(string2):
        exit("sequences have different lengths")

    dist = 0
    for i in range(len(string1)):
        if string1[i] != string2[i]:
            dist += 1
    return dist


p = argparse.ArgumentParser()
p.add_argument('id', help="puzzle id number")
p.add_argument('-d', '--dir', help="directory to read file from", default="../data/puzzles")
p.add_argument('-o', '--outdir', help="directory to write file to", default="../data/puzzles")
args = p.parse_args()

# read secstruct and sequence from nupack output summary file and puzzle file
with open("%s/%s.summary" % (args.dir, args.id), 'r') as f:
    for line in f:
        if not line.startswith("%"):
            sequence = line.strip()
url = "http://eternagame.org/get/?type=puzzle&nid=%s" % args.id
puzzle = json.load(urllib.urlopen(url))['data']['puzzle']
secstruct = puzzle['secstruct'].replace(" ", "")
beginseq = puzzle['beginseq']
constraints = puzzle['constraints'].split(",")

# get fold and design info
fold = inv_utils.fold(sequence)
design = eterna_utils.get_design_from_sequence(sequence, secstruct)

# check all constraints
for i in range(len(constraints)/2):
    cname = constraints[2*i]
    cnum = int(constraints[2*i+1])
    if cname == "SHAPE" and cnum == 0:
        if fold[0] != secstruct:
            exit("secondary structure not satisfied")
    elif cname.startswith("CONSECUTIVE_"):
        nuc = cname[-1:]
        if nuc*cnum in sequence:
            exit("more than %s consecutive %s's" % (cnum, nuc))
    elif cname == "GC":
        if design['gc'] > cnum:
            exit("%s GC pairs found, max %s" % (design['gc'], cnum))
    elif cname == "AU":
        if design['ua'] < cnum:
            exit("%s AU pairs found, min %s" % (design['ua'], cnum))
    elif cname == "GU":
        if design['gu'] < cnum:
            exit("%s GU pairs found, min %s" % (design['gu'], cnum))
    elif cname == "PAIRS":
        pairs = design['gc'] + design['ua'] + design['gu']
        if pairs < cnum:
            exit("%s pairs found, min %s" % (pairs, cnum)) 
    elif cname == "MUTATION":
        dist = string_dist(sequence, beginseq)
        if dist > cnum:
            exit("%s mutations found, max %s" % (dist, cnum))
    else:
        exit("unknown constraint: %s" % cname)


# compile fields for post request
fields = {'type': 'post_solution',
          'puznid': args.id,
          'title': '"nupack design"',
          'body': '"designed by nupack 3.0.5"',
          'sequence': sequence,
          'energy': fold[1],
          'gc': design['gc'],
          'gu': design['gu'],
          'ua': design['ua'],
          'melt': design['meltpoint'],
          'pointsrank': 'false',
          'recommend-puzzle': 'true'}
result = '&'.join(['%s=%s' % (key, fields[key]) for key in fields])
with open("%s/%s.post" % (args.outdir, args.id), 'w') as f:
    f.write(result)

