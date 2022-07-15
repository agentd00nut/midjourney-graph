import networkx as nx
from dataclasses import dataclass
from src.node import Node, NodeType


n1 = Node()
nn = n1
A = nx.DiGraph(prompt="prompt1")

A.add_node(n1)

A.add_nodes_from([nn])
A.add_nodes_from([nn])
B = nx.DiGraph(prompt="prompt2")
B.add_nodes_from([nn, Node(id=2, label="jelly", color="#ff0000")])
print(B.nodes(data=True))

print(n1 in A)

A = nx.compose(A, B)

print(A.nodes)
