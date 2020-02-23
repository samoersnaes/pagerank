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



####################
# MODULE CONSTANTS #
####################

# the damping factor that is used throughout the code
m = 0.15

# used by random surfer to determine the lowest score that the
# most visited node must reach before the algorithm stops; for
# testing, I recommend starting with 10000 as the default; keep
# in mind that the actual number of iterations scales both with
# <MIN_SCORE> and the number of nodes; can adjust as needed to
# find the number of steps needed for random surfer to stabilize
MIN_SCORE = 10000

# the maximum allowed difference between a top node's previous (normalized)
# score and its current score; determines the precision of the scores that the
# PageRank function calculates; see check_deltas() as well for more information
DELTA_NORMAL = 1e-06

# serves two purposes: 1) sets the maximum number of top nodes that will be
# stored and compared for each iteration of PageRank; 2) determines the maximum
# number of top nodes that will be outputted and compared for both algorithms
CMP_SIZE = 10



########################
# FUNCTION DEFINITIONS #
########################

def surfs_up(dg):
    """Implements the random surfer algorithm for a DiGraph <dg>"""

    # the goal of this function is to jump randomly from node to node until
    # the most visited node--kept track of by <largest>--reaches a score of
    # <MIN_SCORE>; 1 is added to the score of a node each time it is chosen

    # ASSUMPTIONS:
    # dg.nodes is not empty
    # dg.edges has no reflexive edges
    # the first node of dg.nodes (using lexical ordering) is 0
    # dg.nodes contains all nodes from 0 to (len(dg.nodes) - 1)

    scores = [0] * len(dg.nodes)

    # start with a random node, which will be updated in the loop below
    current_node = random.randrange(len(dg.nodes))
    scores[current_node] += 1
    largest = 1

    while largest < MIN_SCORE:
        action = random.uniform(0, 1)

        # probability <m>: jump to a random node;
        # also done if the node key of <current_node> has no outgoing edges
        if action <= m or not dg.edges(current_node):
            current_node = random.randrange(len(dg.nodes))

        # probability (1 - <m>): follow a random edge
        else:
            edge = random.choice(list(dg.edges(current_node)))
            current_node = edge[1]

        scores[current_node] += 1
        if scores[current_node] > largest:
            largest = scores[current_node]

    # this structure is used throughout the code;
    # see most variables ending in "nodes"
    top_nodes = [(index, scores[index]) for index in range(len(scores))]
    top_nodes.sort(key=lambda item: item[1], reverse=True)

    # <total> conveniently also represents the total number
    # of random jumps made (using an edge or otherwise);
    # however, due to the first value for <current_node>
    # being generated outside of the main loop, <total> is 1
    # greater than the number of iterations completed; still,
    # when we return the number of iterations below, we do
    # not care about this fact, as we would rather count
    # the initialization of <current_node> as an iteration
    total = sum([score for (_, score) in top_nodes])
    normalized_total = sum([(score / total) for (_, score) in top_nodes])
    if len(top_nodes) > CMP_SIZE:
        top_nodes = top_nodes[:CMP_SIZE]
    top_nodes_normal = [(node, score / total) for (node, score) in top_nodes]

    # return a 4-tuple containing:
    # [0]: the number of iterations completed (total score)
    # [1]: the sum of the normalized scores of all nodes
    # [2]: a list of 2-tuples in the form (node, score) of the top nodes
    # [3]: a list of 2-tuples in the form (node, normal_score) of the top nodes
    return (total, normalized_total, top_nodes, top_nodes_normal)


def check_deltas(old_nodes, new_nodes):
    """Determines whether the delta values between <old_nodes> and <new_nodes> are close enough"""

    # both arguments are expected to be a list of 2-tuples of the
    # form (node, score), where "node" is in fact a key to that node

    # ensures that the function will not return True when either one or both of the lists
    # are empty during the first couple of iterations in the PageRank algorithm (see below)
    if not old_nodes or not new_nodes:
        return False

    # tells us whether the deltas that we can compare
    # are close enough with respect to <DELTA_NORMAL>
    close_enough = True
    old_just_nodes = [node for (node, _) in old_nodes]

    # using <new_nodes> as our point of comparison
    for (new_node, new_score) in new_nodes:
        if new_node in old_just_nodes:
            # takes advantage of <old_nodes> and <old_just_nodes> having the same ordering
            index = old_just_nodes.index(new_node)
            old_score = old_nodes[index][1]
            delta = abs(new_score - old_score)

            # even if only one of the deltas is not small
            # enough, the whole function returns False
            if delta > DELTA_NORMAL:
                close_enough = False
                break
    return close_enough


def check_stability(old_nodes, new_nodes):
    """Determines whether the nodes of <old_nodes> share the same ordering as those in <new_nodes>"""

    # as with check_deltas(), avoid returning True
    # when either one or both lists are empty during
    # the first couple iterations of rank_it()
    if not old_nodes or not new_nodes:
        return False

    old_just_nodes = [node for (node, _) in old_nodes]
    new_just_nodes = [node for (node, _) in new_nodes]

    if old_just_nodes == new_just_nodes:
        return True
    else:
        return False


def rank_it(dg):
    """Implements the PageRank algorithm for a DiGraph <dg>"""

    # formula for reference: x = (1 - m)*A*x + (1 - m)*D*x + m*S*x
    edges = list(dg.edges)
    iterations = 0

    # value used often enough that a variable is convenient;
    # should be treated as a constant
    NUM_NODES = len(dg.nodes)

    # the number of iterations at which the top nodes become stable;
    # uses the "strict" definition of stable, i.e. the top nodes must
    # have been in the same ordering for at least the previous loop;
    # while it may be possible for the top nodes to change order after--
    # one would need to prove it impossible to be sure--it is certainly
    # unlikely that they will change if they are in the same order for
    # at least two iterations
    stability = 0
    stable = False

    # contains a list of 2-tuples of the top <CMP_SIZE> node
    # keys (or fewer if <dg> doesn't have that many nodes) and
    # their corresponding scores from the previous iteration;
    # i.e. same structure as <top_nodes> in surfs_up()
    old_top_nodes = []

    # same as <old_top_nodes>, except that it contains
    # the top nodes from after the iteration finishes
    top_nodes = []

    # stores the updated eigenvector in dict form, i.e. {n0: s0, n1: s1, ...};
    # implemented in this way to allow for fewer calculations in the main loop;
    # for the same reason, other terms in the formula (e.g. A) are implemented
    # in a way to minimize the number of computations; however, as these terms
    # are typically dicts in one form or another, the program is slower than it
    # could be due to the number of look-ups performed primarily in the main loop;
    # it would be more advantageous and efficient to use numpy
    x = {node : 1.0 / NUM_NODES for node in dg.nodes}

    # the m*S*x term, which can simply be represented as a constant
    x3 = m / NUM_NODES

    # assigns the number of edges that start at <node> to
    # the <links> dict under its own key; in other words,
    # it is the number of outgoing links from that node
    links = {node : len(dg.edges(node)) for node in dg.nodes}

    # <A> is in fact (1 - m)*A from the formula;  a "2D dict" of
    # the nonzero elements of the mathematical A, where the rows
    # are keys to the column dict, and the column the final key
    A = {}

    # stores the updated (1 - m)*A*x term for each iteration;
    # uses the same structure as <x>, except it only stores
    # the nonzero elements of the resulting column vector
    x1 = {}

    # used to find its complement, the dangling nodes (see below)
    non_dangling_nodes = set()

    for node in dg.nodes:
        # the list of nodes with an edge terminating at <node>, hence the name
        backlinks = [n1 for (n1, n2) in edges if n2 == node]
        # the above <n1> cannot be dangling nodes
        non_dangling_nodes |= set(backlinks)
        # if the row in the mathematical A is not all 0's
        if backlinks:
            A[node] = {}
            # use the number of outgoing links to calculate the
            # appropriate value for row <node>, column <page>
            for page in backlinks:
                A[node][page] = (1.0 - m) / links[page]

    # <D> does not function exactly like its mathematical counterpart;
    # it only stores the dangling nodes
    D = dg.copy()
    D.remove_nodes_from(non_dangling_nodes)

    # the mathematical D would have columns of 0 for non-dangling nodes,
    # and columns of the value given below for dangling nodes; this is
    # used to calculate the (1 - m)*D*x term below in the main loop
    DANGLING_NODE_FACTOR = (1.0 - m) / NUM_NODES

    # note that everything before this point in the function is only calculated once

    # while there is at least one node among <old_top_nodes>
    # and <top_nodes> that has a score difference greater than
    # <DELTA_NORMAL> (for those nodes that can be compared)
    while not check_deltas(old_top_nodes, top_nodes):
        #
        # UPDATE x1 -- (1- m)*A*x
        #

        # only loop through the nonzero rows of the mathematical A
        for node in A:
            x1[node] = sum([A[node][page] * x[page] for page in A[node]])

        #
        # UPDATE x2 -- (1 - m)*D*x
        #

        # when computing (1 - m)*D*x, the resulting column vector will have elements whose
        # values are all the same; <x2> will help find this value; reset to 0.0 each loop
        x2 = 0.0
        for node in D.nodes:
            x2 += DANGLING_NODE_FACTOR * x[node]

        #
        # UPDATE AND NORMALIZE x -- (1 - m)*A*x + (1 - m)*D*x + m*S*x
        #

        other_xs = x2 + x3

        # update every element in the eigenvector <x>
        for node in dg.nodes:
            # every eigenvector element is at least this value
            x[node] = other_xs
            # if the <node> element for (1 - m)*A*x is nonzero
            if node in x1:
                x[node] += x1[node]

        # normalize <x>
        norm_divisor = sum(x.values())
        x = {node : score / norm_divisor for (node, score) in x.items()}

        iterations += 1
        old_top_nodes = top_nodes

        #
        # CHECK FOR STABILITY
        #

        if not stable:
            top_nodes = list(x.items())
            top_nodes.sort(key=lambda item: item[1], reverse=True)
            if len(top_nodes) > CMP_SIZE:
                top_nodes = top_nodes[:CMP_SIZE]

            if check_stability(old_top_nodes, top_nodes):
                stable = True
                stability = iterations
        else:
            # update the scores for the top nodes and sort them again just in case;
            # we still update them due to the while loop's termination condition
            top_nodes = [(node, x[node]) for (node, _) in top_nodes]
            top_nodes.sort(key=lambda item: item[1], reverse=True)

    # return a 4-tuple containing:
    # [0]: the number of iterations completed
    # [1]: the iteration at which the top nodes stabilized ("strict" definition of stable)
    # [2]: the sum of the normalized scores of all nodes
    # [3]: a list of 2-tuples in the form (node, score) of the top nodes
    return (iterations, stability, sum([x[node] for node in x]), top_nodes)


def print_surfer_results(dg):
    """Prints formatted results for surfs_up(<dg>)"""

    # constants used to help with formatting
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

    # <top_nodes> and <top_nodes_normal> share the same ordering
    index = 0
    for (node, score) in top_nodes:
        print('Node {1:>{0}}'.format(NODES_FORMAT_LENGTH, node)
            + ' (normalized: {0:f};'.format(top_nodes_normal[index][1])
            + ' score: {0:{1}d})'.format(score, NODES_SCORE_LENGTH))
        index += 1

    return top_nodes_normal


def print_rank_results(dg):
    """Prints formatted results for rank_it(<dg>)"""

    # constant used to help with formatting
    NODES_FORMAT_LENGTH = int(log10(len(dg.nodes))) + 1

    start = time.time()
    iterations, stability, total, top_nodes = rank_it(dg)
    elapsed = time.time() - start

    # similar formatting as that for the random surfer output
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


# used for debugging and testing; has no relevance towards the
# requirements, but you can uncomment it and the corresponding
# line in the main code to see additional stats
def print_comparison_results(surf_top_nodes, rank_top_nodes, num_nodes):
    # expects <surf_top_nodes>'s scores to be normalized;
    # <num_nodes> is the number of nodes in the graph,
    # not the number of top nodes to be compared

    # constant used to help with formatting
    NODES_FORMAT_LENGTH = int(log10(num_nodes)) + 1

    # another constant used to correct the spacing if not
    # all top nodes are shared between the two algorithms
    DECIMAL_FORMAT_LENGTH = 8

    # each item is a tuple containing (node, difference) or None;
    # None is used when a top ranking node from PageRank is not
    # among the most visited nodes from random surfer, meaning
    # this list is created with respect to PageRank; <node>'s
    # values are thus a subset of the top nodes from PageRank;
    # <difference> is the absolute value of the difference between
    # one of these nodes and the same node from random surfer
    cmp_top_nodes = []

    # used below as a variable in some output strings and
    # as a limiting value to prevent any IndexErrors
    size = CMP_SIZE if num_nodes >= CMP_SIZE else num_nodes

    surf_just_nodes = [node for (node, _) in surf_top_nodes]
    rank_just_nodes = [node for (node, _) in rank_top_nodes]

    for (rank_node, rank_score) in rank_top_nodes:
        if rank_node in surf_just_nodes:
            # <surf_just_nodes> and <surf_nodes> share the same ordering of nodes
            index = surf_just_nodes.index(rank_node)
            surf_score = surf_top_nodes[index][1]
            cmp_top_nodes.append((rank_node, abs(rank_score - surf_score)))
        else:
            cmp_top_nodes.append(None)

    print()
    print('##########')
    print()
    print('Top {0:d} nodes for PageRank and random surfer respectively:'.format(size))
    print()
    print(rank_just_nodes)
    print(surf_just_nodes)

    print()
    print('##########')
    print()
    print('Absolute differences between the top {0:d} nodes:'.format(size))
    print('(Using top nodes of PageRank as point of comparison)')
    print()

    greatest = 0.0
    sum_diff = 0.0

    # print the differences between the nodes whose scores can
    # be compared, keeping track of which difference is greatest;
    # print a line with no relevant data for missing top nodes
    for index in range(size):
        # if the node is in both <rank_top_nodes> and <surf_top_nodes>
        if cmp_top_nodes[index]:
            difference = cmp_top_nodes[index][1]
            if difference > greatest:
                greatest = difference
            sum_diff += difference

            if rank_just_nodes[index] == surf_just_nodes[index]:
                print('Node {1:>{0}}'.format(NODES_FORMAT_LENGTH, cmp_top_nodes[index][0])
                    + ' (difference: {0:f})'.format(difference))
            # ordering is mismatched; add a '*' to the end of the line to indicate this
            else:
                print('Node {1:>{0}}'.format(NODES_FORMAT_LENGTH, cmp_top_nodes[index][0])
                    + ' (difference: {0:f}) *'.format(difference))

        # since this indicates a mismtached ordering, add '*' to the end
        else:
            print('Node {1:>{0}}'.format(NODES_FORMAT_LENGTH, '-')
                + ' (difference: {1:>{0}}) *'.format(DECIMAL_FORMAT_LENGTH, '-'))

    print()
    print('Greatest absolute difference: {0:f}'.format(greatest))
    print('Sum of differences: {0:f}'.format(sum_diff))



#############
# MAIN CODE #
#############

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Please provide a filepath to the dataset")
        sys.exit(1)

    # create a simple DiGraph from the file provided (as opposed to a MultiGraph or MultiDiGraph,
    # as the latter two would add the same edge each additional time it occurs in the dataset)
    with open(sys.argv[1], 'rb') as data:
        dg = nx.read_adjlist(data, create_using=nx.DiGraph(), nodetype=int)

    # the data we are expected to handle can be random, and thus some nodes may have
    # reflexive edges; we want to remove these edges, as they should not be counted
    reflexive_edges = []
    for (a, b) in dg.edges:
        if a == b:
            reflexive_edges.append((a, b))
    dg.remove_edges_from(reflexive_edges)

    surf_top_nodes = print_surfer_results(dg)
    rank_top_nodes = print_rank_results(dg)

    # uncomment the line below and the function definition to see additional stats
    print_comparison_results(surf_top_nodes, rank_top_nodes, len(dg.nodes))
