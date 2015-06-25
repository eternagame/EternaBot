#!/bin/bash

#PBS -M mjwu@stanford.edu
#PBS -m ea
#PBS -l walltime=3:00:00:00
##PBS -l nodes=1:ppn=16
#$ -pe orte 16
#$ -M mjwu@stanford.edu
#$ -m es
#$ -cwd

BASE_DIR=$HOME/private/das
DATA_DIR=$BASE_DIR/EteRNABot/nupack/data
CODE_DIR=$BASE_DIR/EteRNABot/nupack/code
start=`date +%s`

curl "http://eternagame.org/get/?type=puzzles&sort=solved&puzzle_type=Challenge&skip=2&size=240&notcleared=true&uid=216582" -o $DATA_DIR/list.txt
grep -E -o "id.:.[0-9]+" $DATA_DIR/list.txt | cut -c 6- >| $DATA_DIR/list.puzzles
#curl "http://eternagame.org/get/?type=puzzles&sort=date&puzzle_type=PlayerPuzzle&skip=0&size=8000&notcleared=true&uid=216582" -o $DATA_DIR/list.txt
#grep -E -o "id.:.[0-9]+" $DATA_DIR/list.txt | cut -c 6- >| $DATA_DIR/list.player
#curl "http://eternagame.org/get/?type=puzzles&sort=solved&puzzle_type=PlayerPuzzle&skip=0&size=8000&notcleared=true&uid=216582" -o $DATA_DIR/list.txt
#grep -E -o "id.:.[0-9]+" $DATA_DIR/list.txt | cut -c 6- >| $DATA_DIR/list.easy

return=$(curl -s -X POST -c $CODE_DIR/cookiefile -d "type=login&name=nupackbot&pass=nilespierce&workbranch&main"  http://eternagame.org/login/)
if [[ $return != *'"success":true'* ]]
then
    grep -P -o '"error":"(.*?)"' <<< $return
fi

xargs < $DATA_DIR/list.puzzles -P 16 -I % $CODE_DIR/design_puzzle.sh %
#xargs < $DATA_DIR/list.player -P 16 -I % $CODE_DIR/design_puzzle.sh %
#xargs < $DATA_DIR/list.easy -P 16 -I % $CODE_DIR/design_puzzle.sh %

end=`date +%s`
echo $((end-start))
