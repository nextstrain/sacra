#!/usr/bin/env bash

WERE_ERRORS=0

function commandFailed {
  LINE="$(sed "${1}q;d" test.sh)"
  echo -e "WARNING: This command failed: ${LINE}\nDetails can be found in test/test.log"
  WERE_ERRORS=1
}

echo -e "\nClearing old test output and logs."
rm test/test.log
rm test/output/*

# TRAPS
trap 'commandFailed $LINENO' ERR


echo -e "\nRunning zika ViPR test data, with entrez queries"
echo "$ python src/run.py -f test/input/zika_test.fasta -o test/output/zika_test.json --pathogen zika --use_entrez_to_improve_data" >> test/test.log && echo "" >> test/test.log
python src/run.py -f test/input/zika_test.fasta -o test/output/zika_test.json --pathogen zika --use_entrez_to_improve_data >> test/test.log 2>&1

echo -e "Diffing against expected output"
diff -s test/expected-output/zika_test.json test/output/zika_test.json > /dev/null

echo "" >> test/test.log && echo "--------------------" >> test/test.log && echo "" >> test/test.log

echo -e "\nRunning zika USVI test data, with command line overrides"
echo "$ python src/run.py -f test/input/zika_usvi.fasta -o test/output/zika_usvi.json --pathogen zika --custom_fields authors:\"Black et al\" attribution_id:\"Black2017Zika\" attribution_url:\"https://github.com/blab/zika-usvi\" attribution_title:\"Genetic characterization of the Zika virus epidemic in the US Virgin Islands\" attribution_date:\"2017\" attribution_source:\"github\" --custom_fasta_header usvi" >> test/test.log && echo "" >> test/test.log
python src/run.py -f test/input/zika_usvi.fasta -o test/output/zika_usvi.json --pathogen zika --custom_fields authors:"Black et al" attribution_id:"Black2017Zika" attribution_url:"https://github.com/blab/zika-usvi" attribution_title:"Genetic characterization of the Zika virus epidemic in the US Virgin Islands" attribution_date:"2017" attribution_source:"github" --custom_fasta_header usvi >> test/test.log 2>&1

echo -e "Diffing against expected output"
diff -s test/expected-output/zika_usvi.json test/output/zika_usvi.json > /dev/null



if [[ $WERE_ERRORS -eq 1 ]]; then
  echo "Test script finished with errors."
  exit 2
else
  echo "Test script finished without errors."

fi
