# PageRank

PageRank forms the core of Google's search algorithm, as it allows webpages to be ranked in order of their relative importance to each other. Due to the self-referential nature of this importance ranking---a page's importance is dependent on the importance of the pages that link to it, and the page itself gives its importance to the pages it links to---representing the pages (nodes) as a matrix of directed links (edges) is a particularly useful and efficient way to solve the problem.

This program was part of an assignment for my Linear Algebra and Optimization course, and it implements two methods of calculating the importance ranking. The first is called "random surfer", and as the name implies, it randomly follows links from one page to another, incrementing the importance score of that page each time it is visited. As the network of pages may not be a single component, there is some probability of instead teleporting to a random page to account for this. In this case, the probability (damping factor) is set to 15%.

The second method is the PageRank algorithm itself. The graph of pages is represented as a square matrix, and the eigenvector of importance scores is approximated through the iterative formula below. Sample input and output is also shown below, using the example graph the Gnutella graph, both of which are in the `data` folder. Additional context can be found starting from page 5 in the attached assignment, the eigenvector paper, and of course [Wikipedia (direct link)](https://en.wikipedia.org/wiki/PageRank).

## PageRank Formula

![x_{k+1} = (1 - m)Ax_k + (1 - m)Dx_k + mSx_k](https://render.githubusercontent.com/render/math?math=x_%7Bk%2B1%7D%20%3D%20(1%20-%20m)Ax_k%20%2B%20(1%20-%20m)Dx_k%20%2B%20mSx_k)

[comment]: # (https://gist.github.com/a-rodin/fef3f543412d6e1ec5b6cf55bf197d7b)
[comment]: # (https://alexanderrodin.com/github-latex-markdown)

```
x: eigenvector
k: iteration counter
m: damping factor
A: stochastic matrix
D: dangling node matrix
S: "lowest score" matrix
```

## Usage

```
python3 pagerank.py <file>
```

The filepath to the dataset must be provided as the one and only command line argument to the program. The data must be in the form of integer edge pairs, one pair per line. The file may contain comments, and the separator can be (relatively) arbitrary, so long as a consisent delimiter is used. Multiple edges between the same two nodes are allowed, but the additional edges are ignored. Reflexive edges are likewise allowed but removed. See sample datasets in the `data` directory.

## Example Input

```
# 4 nodes
0 1
0 2
1 2
2 0
2 3
3 1
```

## Example Output

```
##########

m = 0.15
MIN_SCORE: 10000

Most visited nodes according to random surfer:

Time: 0.470912
Iterations: 28455 (total score)
Normalized score: 1.000000

Node 2 (normalized: 0.351432; score: 10000)
Node 1 (normalized: 0.273730; score:  7789)
Node 0 (normalized: 0.187735; score:  5342)
Node 3 (normalized: 0.187102; score:  5324)

##########

m = 0.15
DELTA_NORMAL: 1e-06

Highest ranking nodes according to PageRank:

Time: 0.000919
Iterations: 41
Stable at: 3
Sum of scores: 1.000000

Node 2 (score: 0.351058)
Node 1 (score: 0.275543)
Node 0 (score: 0.186700)
Node 3 (score: 0.186700)

##########

Top 4 nodes for PageRank and random surfer respectively:

[2, 1, 0, 3]
[2, 1, 0, 3]

##########

Absolute differences between the top 4 nodes:
(Using top nodes of PageRank as point of comparison)

Node 2 (difference: 0.000374)
Node 1 (difference: 0.001812)
Node 0 (difference: 0.001035)
Node 3 (difference: 0.000403)

Greatest absolute difference: 0.001812
Sum of differences: 0.003624
```

## Sample Gnutella Output

```
##########

m = 0.15
MIN_SCORE: 10000

Most visited nodes according to random surfer:

Time: 91.287988
Iterations: 4166879 (total score)
Normalized score: 1.000000

Node  367 (normalized: 0.002400; score: 10000)
Node  249 (normalized: 0.002203; score:  9181)
Node  145 (normalized: 0.002030; score:  8460)
Node  264 (normalized: 0.001989; score:  8289)
Node  266 (normalized: 0.001969; score:  8203)
Node  127 (normalized: 0.001877; score:  7823)
Node  122 (normalized: 0.001860; score:  7752)
Node    5 (normalized: 0.001849; score:  7704)
Node  123 (normalized: 0.001813; score:  7553)
Node 1317 (normalized: 0.001808; score:  7534)

##########

m = 0.15
DELTA_NORMAL: 1e-06

Highest ranking nodes according to PageRank:

Time: 10.598179
Iterations: 8
Stable at: 5
Sum of scores: 1.000000

Node  367 (score: 0.002388)
Node  249 (score: 0.002184)
Node  145 (score: 0.002055)
Node  264 (score: 0.001999)
Node  266 (score: 0.001963)
Node  123 (score: 0.001863)
Node  127 (score: 0.001861)
Node  122 (score: 0.001853)
Node 1317 (score: 0.001844)
Node    5 (score: 0.001831)

##########

Top 10 nodes for PageRank and random surfer respectively:

[367, 249, 145, 264, 266, 123, 127, 122, 1317, 5]
[367, 249, 145, 264, 266, 127, 122, 5, 123, 1317]

##########

Absolute differences between the top 10 nodes:
(Using top nodes of PageRank as point of comparison)

Node  367 (difference: 0.000012)
Node  249 (difference: 0.000019)
Node  145 (difference: 0.000025)
Node  264 (difference: 0.000009)
Node  266 (difference: 0.000005)
Node  123 (difference: 0.000051) *
Node  127 (difference: 0.000017) *
Node  122 (difference: 0.000007) *
Node 1317 (difference: 0.000035) *
Node    5 (difference: 0.000018) *

Greatest absolute difference: 0.000051
Sum of differences: 0.000199
```