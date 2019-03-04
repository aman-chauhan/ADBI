import pandas as pd
import random
import copy
import math
import sys


random.seed(0)


def get_revenue(algorithm, bid_data, budget_data, queries):
    revenue = 0.0
    for q in queries:
        subdata = {k: bid_data[q][k] for k in bid_data[q].keys() if budget_data[k]['budget'] > bid_data[q][k]}
        if len(subdata) == 0:
            continue
        else:
            maxbidder = None
            maxbid = float('-inf')
            if algorithm == 'greedy':
                for bidder in subdata.keys():
                    if subdata[bidder] > maxbid:
                        maxbidder = bidder
                        maxbid = subdata[bidder]
                    elif subdata[bidder] == maxbid and bidder < maxbidder:
                        maxbidder = bidder
            elif algorithm == 'balance':
                for bidder in subdata.keys():
                    if budget_data[bidder]['budget'] > maxbid:
                        maxbidder = bidder
                        maxbid = budget_data[bidder]['budget']
                    elif budget_data[bidder]['budget'] == maxbid and bidder < maxbidder:
                        maxbidder = bidder
            else:
                for bidder in subdata.keys():
                    adjusted = budget_data[bidder]['budget'] + budget_data[bidder]['spent']
                    adjusted = budget_data[bidder]['spent'] / adjusted
                    adjusted = subdata[bidder] * (1 - math.exp(adjusted - 1))
                    if adjusted > maxbid:
                        maxbidder = bidder
                        maxbid = adjusted
                    elif adjusted == maxbid and bidder < maxbidder:
                        maxbidder = bidder
            revenue += subdata[maxbidder]
            budget_data[maxbidder]['budget'] -= subdata[maxbidder]
            budget_data[maxbidder]['spent'] += subdata[maxbidder]
    del budget_data
    return round(revenue, 2)


def init(df):
    bid_data = {}
    budget_data = {}
    for query in df['Keyword'].unique():
        if query not in bid_data:
            bid_data[query] = {}
        subdf = df[df['Keyword'] == query]
        for row in subdf.itertuples():
            bid_data[query][row[1]] = round(row[3], 2)
            if row[1] not in budget_data:
                budget_data[row[1]] = {'budget': 0.0, 'spent': 0}
            if round(row[4], 2) > budget_data[row[1]]['budget']:
                budget_data[row[1]]['budget'] = round(row[4], 2)
    return bid_data, budget_data


def main(match_type):
    df = pd.read_csv('bidder_dataset.csv')
    optimal = df['Budget'].sum()
    queries = [x.strip() for x in open('queries.txt', 'r').readlines()]
    df = df.fillna(0)
    bid_data, budget_data = init(df)
    revenue = get_revenue(match_type, bid_data, copy.deepcopy(budget_data), queries)
    print(revenue)
    comp = 0.0
    for _ in range(100):
        random.shuffle(queries)
        sub = get_revenue(match_type, bid_data, copy.deepcopy(budget_data), queries)
        comp += (sub / optimal)
    print(round(comp / 100, 2))


if __name__ == '__main__':
    main(sys.argv[1])
