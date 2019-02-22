#!/bin/bash
#
python ./src/pharmCounting.py ./input/itcont.txt ./output/top_cost_drug.txt

# add a parameter in the end if only need to output top k records, e.g.
#python ./src/pharmCounting.py ./input/itcont.txt ./output/top_cost_drug.txt 2
