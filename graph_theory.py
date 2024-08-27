import networkx as nx
import random
import pandas as pd


def simulate_failure(P, B):
    G = nx.complete_graph(P)
    edges = list(G.edges())
    random.shuffle(edges)
    
    for edge in edges:
        G.remove_edge(*edge)
        
        if nx.number_connected_components(G) > 1:
            return "Partitioned"
        
        isolated_nodes = sum(1 for node in G.nodes() if G.degree(node) == 0)
        if isolated_nodes > B:
            return "Too Many Disconnected Nodes"
    
    return "No Failure"


def simulate_failure_random_removal(P, B):
    G = nx.complete_graph(P)
    edges = list(G.edges())
    
    while edges:
        num_edges_to_remove = random.randint(1, len(edges))
        edges_to_remove = random.sample(edges, num_edges_to_remove)
        G.remove_edges_from(edges_to_remove)        
        edges = list(G.edges())
        
        if nx.number_connected_components(G) > 1:
            return "Partitioned"
        
        isolated_nodes = sum(1 for node in G.nodes() if G.degree(node) == 0)
        if isolated_nodes > B:
            return "Too Many Disconnected Nodes"
    
    return "No Failure"


P = 30
B_values = [1, 2, 5, 10, 15, 20 , 25, 29]
iterations = 50

results = {B: {"Partitioned": 0, "Too Many Disconnected Nodes": 0} for B in B_values}

for B in B_values:
    for _ in range(iterations):
        result = simulate_failure_random_removal(P, B)
        if result != "No Failure":
            results[B][result] += 1

results_df = pd.DataFrame(results).T
results_df["Total"] = results_df["Partitioned"] + results_df["Too Many Disconnected Nodes"]

print(results_df)
