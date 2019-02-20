#!/bin/bash
export JAVA_HOME=`/usr/libexec/java_home -v 1.8`
export SPARK_HOME=~/spark-1.6.2-bin-hadoop2.6
export PYSPARK_PYTHON=/Users/achauhan/anaconda3/envs/py27/bin/python
export PYSPARK_DRIVER_PYTHON=/Users/achauhan/anaconda3/envs/py27/bin/python

if [ -z "$1" ]; then
    $SPARK_HOME/bin/pyspark --packages graphframes:graphframes:0.1.0-spark1.6 degree.py
elif [ -z "$2" ]; then
    $SPARK_HOME/bin/pyspark --packages graphframes:graphframes:0.1.0-spark1.6 degree.py $1
else
    $SPARK_HOME/bin/pyspark --packages graphframes:graphframes:0.1.0-spark1.6 degree.py $1 $2
fi
