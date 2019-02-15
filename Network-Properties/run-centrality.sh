#!/bin/bash
export JAVA_HOME=`/usr/libexec/java_home -v 1.8`
export SPARK_HOME=~/spark-1.6.2-bin-hadoop2.6
export PYSPARK_PYTHON=/Users/achauhan/anaconda3/envs/py27/bin/python
export PYSPARK_DRIVER_PYTHON=/Users/achauhan/anaconda3/envs/py27/bin/python

$SPARK_HOME/bin/pyspark --packages graphframes:graphframes:0.1.0-spark1.6 centrality.py
