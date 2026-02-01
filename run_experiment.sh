#!/bin/bash

echo "Running experiment on the Géant Topology"
python3 internet_topologies_experiment.py topologies/geant.txt results/geant.csv >> geant_results.out

echo "Running experiment on the RNP Topology"
python3 internet_topologies_experiment.py topologies/rnp_equal.txt results/rnp.csv >> rnp_results.out

echo "Running experiment on the Internet2 Topology"
python3 internet_topologies_experiment.py topologies/internet2.txt results/internet2.csv >> internet2_results.out