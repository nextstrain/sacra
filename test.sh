#!/usr/bin/env bash

WERE_ERRORS=0

function commandFailed {
  LINE="$(sed "${1}q;d" test.sh)"
  echo -e "WARNING: This command failed: ${LINE}"
  WERE_ERRORS=1
}

# TRAPS
trap 'commandFailed $LINENO' ERR


echo "Running zika test using entrez"
python src/run.py -f test/input/zika_test.fasta -o test/output/zika_test.json --pathogen zika --use_entrez_to_improve_data > test/test.log 2>&1

echo "Diffing against expected output"
diff -s test/expected-output/zika_test.json test/output/zika_test.json > /dev/null

if [[ $WERE_ERRORS -eq 1 ]]; then
  echo "Test script finished with errors."
  exit 2
else
  echo "Test script finished without errors."

fi
