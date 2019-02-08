from pyspark import SparkConf, SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
import operator
import re
import numpy as np
import matplotlib.pyplot as plt


def main():
    conf = SparkConf().setMaster("local[2]").setAppName("Streamer")
    sc = SparkContext(conf=conf)
    sc.setLogLevel("ERROR")
    ssc = StreamingContext(sc, 10)   # Create a streaming context with batch interval of 10 sec
    ssc.checkpoint("checkpoint")

    pwords = load_wordlist("positive.txt")
    nwords = load_wordlist("negative.txt")

    counts = stream(ssc, pwords, nwords, 100)
    make_plot(counts)


def make_plot(counts):
    """
    Plot the counts for the positive and negative words for each timestep.
    Use plt.show() so that the plot will popup.
    """
    pos = []
    neg = []
    for count in counts:
        for typecount in count:
            if typecount[0] == 'positive':
                pos.append(typecount[1])
            else:
                neg.append(typecount[1])
    times = np.arange(len(counts))
    plt.plot(times, pos, color='blue', marker='o')
    plt.plot(times, neg, color='red', marker='o')
    plt.legend(['positive', 'negative'])
    plt.xlabel('Time Step')
    plt.ylabel('Word Count')
    plt.xticks(times)
    plt.savefig('plot.png')
    plt.show()


def load_wordlist(filename):
    """
    This function should return a list or set of words from the given filename.
    """
    words = set()
    with open(filename, 'r') as fp:
        words.update([x.strip() for x in fp.readlines()])
    return words


def stream(ssc, pwords, nwords, duration):
    kstream = KafkaUtils.createDirectStream(
        ssc, topics=['twitterstream'], kafkaParams={"metadata.broker.list": 'localhost:9092'})
    tweets = kstream.map(lambda x: x[1])

    # Each element of tweets will be the text of a tweet.
    # You need to find the count of all the positive and negative words in these tweets.
    # Keep track of a running total counts and print this at every time step (use the pprint function).
    # tweets to words
    words = tweets.flatMap(lambda k: re.split('\W+', k)).filter(lambda k: len(k) != 0)
    # words to types
    word_types = words.map(lambda k: ('positive' if k in pwords else ('negative' if k in nwords else 'oov'), 1))
    # count types
    type_counts = word_types.reduceByKey(lambda k, l: k + l).filter(lambda k: k[0] != 'oov')
    # running counts
    total_counts = type_counts.updateStateByKey(lambda new, old: sum(new, 0) if old is None else sum(new, old))
    total_counts.pprint()

    # Let the counts variable hold the word counts for all time steps
    # You will need to use the foreachRDD function.
    # For our implementation, counts looked like:
    #   [[("positive", 100), ("negative", 50)], [("positive", 80), ("negative", 60)], ...]
    counts = []
    # YOURDSTREAMOBJECT.foreachRDD(lambda t,rdd: counts.append(rdd.collect()))
    type_counts.foreachRDD(lambda t, rdd: counts.append(rdd.collect()))
    ssc.start()                         # Start the computation
    ssc.awaitTerminationOrTimeout(duration)
    ssc.stop(stopGraceFully=True)

    return counts


if __name__ == "__main__":
    main()
