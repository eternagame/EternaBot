#!/bin/bash

BASE_DIR=$HOME/private/das
DATA_DIR=$BASE_DIR/EteRNABot/nupack/data
CODE_DIR=$BASE_DIR/EteRNABot/nupack/code
export PYTHONPATH=$PYTHONPATH:$BASE_DIR/EteRNABot/eternabot/
export NUPACKHOME=$BASE_DIR/EteRNABot/nupack/code/nupack3.0.5c-clean

id=${1}

if grep -Fxq $id $DATA_DIR/done.txt; then
    echo "puzzle $id already done"
    exit 1
fi
if grep -Fq $id $DATA_DIR/not_done.txt; then
    echo "puzzle $id already tried"
    exit 1
fi


echo "getting puzzle $id"
return=$(python $CODE_DIR/json_to_fold.py $id 2>&1)
if [[ -n ${return// } ]]; then
    echo "$id: $return" >> $DATA_DIR/not_done.txt
    echo $return
    exit
fi

echo "designing rna"

$NUPACKHOME/bin/design -material rna1999 -prevent $DATA_DIR/puzzles/$id".prevent" $DATA_DIR/puzzles/$id;

return=$(python $CODE_DIR/get_sequence_info.py $id 2>&1)
if [[ -n ${return// } ]]; then
    echo "$id: $return" >> $DATA_DIR/not_done.txt
    echo $return
    exit
fi

return=$(curl -s -X POST -b $CODE_DIR/cookiefile -d @$DATA_DIR/puzzles/$id.post http://eternagame.org/post/)
if [[ $return != *'"success":true'* ]]; then
    grep -P -o '"error":"(.*?)"' <<< $return
fi

echo $id >> $DATA_DIR/done.txt
