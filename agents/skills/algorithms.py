"""Algorithms skill — graph, pathfinding, optimization, entropy."""
from __future__ import annotations
import heapq
import math
import numpy as np
import networkx as nx
from scipy import optimize

SKILL = "algorithms"


def shortest_path(graph: nx.Graph, src, dst) -> list:
    return nx.shortest_path(graph, src, dst, weight="weight")


def mst(graph: nx.Graph) -> nx.Graph:
    return nx.minimum_spanning_tree(graph)


def centrality(graph: nx.Graph) -> dict:
    return {
        "betweenness": nx.betweenness_centrality(graph),
        "eigenvector": nx.eigenvector_centrality(graph, max_iter=1000),
    }


def astar(grid: np.ndarray, start: tuple, goal: tuple) -> list[tuple]:
    """A* on a 2D binary grid (0=open, 1=blocked)."""
    def h(a, b): return abs(a[0]-b[0]) + abs(a[1]-b[1])
    open_set = [(h(start, goal), 0, start, [start])]
    visited = set()
    while open_set:
        _, cost, node, path = heapq.heappop(open_set)
        if node == goal:
            return path
        if node in visited:
            continue
        visited.add(node)
        r, c = node
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = r+dr, c+dc
            if 0 <= nr < grid.shape[0] and 0 <= nc < grid.shape[1] \
               and grid[nr, nc] == 0 and (nr, nc) not in visited:
                heapq.heappush(open_set, (cost+1+h((nr,nc),goal), cost+1, (nr,nc), path+[(nr,nc)]))
    return []  # no path


def entropy(data: list) -> float:
    """Shannon entropy in bits."""
    from collections import Counter
    counts = Counter(data)
    total = sum(counts.values())
    return -sum((c/total) * math.log2(c/total) for c in counts.values() if c > 0)


def topological_sort(dag: nx.DiGraph) -> list:
    return list(nx.topological_sort(dag))


def genetic_optimize(fitness_fn, population: np.ndarray, generations: int = 50,
                     mutation_rate: float = 0.1) -> np.ndarray:
    """Simple genetic algorithm. Returns best individual."""
    pop = population.copy()
    for _ in range(generations):
        scores = np.array([fitness_fn(ind) for ind in pop])
        idx = np.argsort(scores)[::-1]
        pop = pop[idx]
        top_half = pop[:len(pop)//2]
        children = top_half + np.random.randn(*top_half.shape) * mutation_rate
        pop = np.vstack([top_half, children])
    return pop[0]


def verify() -> bool:
    G = nx.path_graph(5)
    assert shortest_path(G, 0, 4) == [0, 1, 2, 3, 4]
    assert entropy([0, 0, 1, 1]) == 1.0
    grid = np.zeros((5, 5), dtype=int)
    path = astar(grid, (0, 0), (4, 4))
    assert path[-1] == (4, 4)
    return True
