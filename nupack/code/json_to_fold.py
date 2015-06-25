import argparse
import urllib
import json

p = argparse.ArgumentParser()
p.add_argument('id', help="puzzle id number")
p.add_argument('-d', '--dir', help="directory to write file to", default="../data/puzzles")
args = p.parse_args()

url = "http://eternagame.org/get/?type=puzzle&nid=%s" % args.id
puzzle = json.load(urllib.urlopen(url))['data']['puzzle']
secstruct = puzzle['secstruct'].replace(" ","")
beginseq = puzzle['beginseq']
locks = puzzle['locks']
constraints = puzzle['constraints'].split(",")

accept_const = ["SOFT", "GC", "AU", "GU", "PAIRS", "MUTATION"]
fprev = open("%s/%s.prevent" % (args.dir, args.id), 'w')
for i in range(len(constraints)/2):
    cname = constraints[2*i]
    cnum = int(constraints[2*i+1])
    if cname == "SHAPE":
        if cnum != 0:
            exit("multi objective puzzle")
    elif cname == "ANTISHAPE":
        exit("anti shape objective puzzle")
    elif cname in ["CONSECUTIVE_%s" % nuc for nuc in ["A", "U", "G", "C"]]:
        nuc = cname[-1:]
        fprev.write("%s\n" % nuc*cnum)
    elif cname not in accept_const:
        exit("unknown constraint: %s" % cname)
fprev.close()

if not locks:
    constraint = "N"*len(secstruct)
else:
    constraint = ""
    for i in range(len(locks)):
        if locks[i] == "o":
            constraint += "N"
        else:
            constraint += beginseq[i]

with open("%s/%s.fold" % (args.dir, args.id), "w") as f:
    f.write("%s\n" % secstruct)
    f.write(constraint)
