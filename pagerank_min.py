#!/usr/bin/env python3
# Samuel Oersnaes
# Last modified:
# 2018-11-13

import sys
import time
import random
import networkx as nx
from math import log10

# Tested using:
# Python 3.7.1
# networkx 2.2

m = 0.15
MIN_SCORE = 10000
DELTA_NORMAL = 1e-06
CMP_SIZE = 10


def surfs_up(dg):
    scores = [0] * len(dg.nodes)
    current_node = random.randrange(len(dg.nodes))
    scores[current_node] += 1
    largest = 1

    while largest < MIN_SCORE:
        action = random.uniform(0, 1)
        if action <= m or not dg.edges(current_node):
            current_node = random.randrange(len(dg.nodes))
        else:
            edge = random.choice(list(dg.edges(current_node)))
            current_node = edge[1]
        scores[current_node] += 1
        if scores[current_node] > largest:
            largest = scores[current_node]

    top_nodes = [(index, scores[index]) for index in range(len(scores))]
    top_nodes.sort(key=lambda item: item[1], reverse=True)
    total = sum([score for (_, score) in top_nodes])
    normalized_total = sum([(score / total) for (_, score) in top_nodes])
    if len(top_nodes) > CMP_SIZE:
        top_nodes = top_nodes[:CMP_SIZE]
    top_nodes_normal = [(node, score / total) for (node, score) in top_nodes]
    return (total, normalized_total, top_nodes, top_nodes_normal)


def check_deltas(old_nodes, new_nodes):
    if not old_nodes or not new_nodes:
        return False
    close_enough = True
    old_just_nodes = [node for (node, _) in old_nodes]
    for (new_node, new_score) in new_nodes:
        if new_node in old_just_nodes:
            index = old_just_nodes.index(new_node)
            old_score = old_nodes[index][1]
            delta = abs(new_score - old_score)
            if delta > DELTA_NORMAL:
                close_enough = False
                break
    return close_enough


def check_stability(old_nodes, new_nodes):
    if not old_nodes or not new_nodes:
        return False
    old_just_nodes = [node for (node, _) in old_nodes]
    new_just_nodes = [node for (node, _) in new_nodes]
    if old_just_nodes == new_just_nodes:
        return True
    else:
        return False


def rank_it(dg):
    edges = list(dg.edges)
    iterations = 0
    NUM_NODES = len(dg.nodes)
    stability = 0
    stable = False
    old_top_nodes = []
    top_nodes = []
    x = {node : 1.0 / NUM_NODES for node in dg.nodes}
    x3 = m / NUM_NODES
    links = {node : len(dg.edges(node)) for node in dg.nodes}
    A = {}
    x1 = {}
    non_dangling_nodes = set()

    for node in dg.nodes:
        backlinks = [n1 for (n1, n2) in edges if n2 == node]
        non_dangling_nodes |= set(backlinks)
        if backlinks:
            A[node] = {}
            for page in backlinks:
                A[node][page] = (1.0 - m) / links[page]

    D = dg.copy()
    D.remove_nodes_from(non_dangling_nodes)
    DANGLING_NODE_FACTOR = (1.0 - m) / NUM_NODES

    while not check_deltas(old_top_nodes, top_nodes):
        for node in A:
            x1[node] = sum([A[node][page] * x[page] for page in A[node]])
        x2 = 0.0
        for node in D.nodes:
            x2 += DANGLING_NODE_FACTOR * x[node]
        other_xs = x2 + x3
        for node in dg.nodes:
            x[node] = other_xs
            if node in x1:
                x[node] += x1[node]

        norm_divisor = sum(x.values())
        x = {node : score / norm_divisor for (node, score) in x.items()}
        iterations += 1
        old_top_nodes = top_nodes

        if not stable:
            top_nodes = list(x.items())
            top_nodes.sort(key=lambda item: item[1], reverse=True)
            if len(top_nodes) > CMP_SIZE:
                top_nodes = top_nodes[:CMP_SIZE]
            if check_stability(old_top_nodes, top_nodes):
                stable = True
                stability = iterations
        else:
            top_nodes = [(node, x[node]) for (node, _) in top_nodes]
            top_nodes.sort(key=lambda item: item[1], reverse=True)

    return (iterations, stability, sum([x[node] for node in x]), top_nodes)


def print_surfer_results(dg):
    NODES_FORMAT_LENGTH = int(log10(len(dg.nodes))) + 1
    NODES_SCORE_LENGTH = int(log10(MIN_SCORE)) + 1
    start = time.time()
    total, normalized_total, top_nodes, top_nodes_normal = surfs_up(dg)
    elapsed = time.time() - start

    print()
    print('##########')
    print()
    print('m =', m)
    print('MIN_SCORE:', MIN_SCORE)
    print()
    print('Most visited nodes according to random surfer:')
    print()
    print('Time: {0:f}'.format(elapsed))
    print('Iterations: {0:d} (total score)'.format(total))
    print('Normalized score: {0:f}'.format(normalized_total))
    print()

    index = 0
    for (node, score) in top_nodes:
        print('Node {1:>{0}}'.format(NODES_FORMAT_LENGTH, node)
            + ' (normalized: {0:f};'.format(top_nodes_normal[index][1])
            + ' score: {0:{1}d})'.format(score, NODES_SCORE_LENGTH))
        index += 1

    return top_nodes_normal


def print_rank_results(dg):
    NODES_FORMAT_LENGTH = int(log10(len(dg.nodes))) + 1
    start = time.time()
    iterations, stability, total, top_nodes = rank_it(dg)
    elapsed = time.time() - start

    print()
    print('##########')
    print()
    print('m =', m)
    print('DELTA_NORMAL:', DELTA_NORMAL)
    print()
    print('Highest ranking nodes according to PageRank:')
    print()
    print('Time: {0:f}'.format(elapsed))
    print('Iterations: {0:d}'.format(iterations))
    print('Stable at: {0:d}'.format(stability))
    print('Sum of scores: {0:f}'.format(total))
    print()

    for (node, score) in top_nodes:
        print('Node {1:>{0}}'.format(NODES_FORMAT_LENGTH, node)
            + ' (score: {0:f})'.format(score))

    return top_nodes


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Please provide a filepath to the dataset")
        sys.exit(1)

    with open(sys.argv[1], 'rb') as data:
        dg = nx.read_adjlist(data, create_using=nx.DiGraph(), nodetype=int)

    reflexive_edges = []
    for (a, b) in dg.edges:
        if a == b:
            reflexive_edges.append((a, b))
    dg.remove_edges_from(reflexive_edges)
    print_surfer_results(dg)
    print_rank_results(dg)
