from dataclasses import asdict, astuple
import secrets
import pytest

from src.nGraph import nGraph
from src.node import Node, NodeType
from src.edge import Edge


def findNodeWithLowSuccessors(graph: nGraph, node: str, maxSuccessors=3):
    """
    Finds a node in the graph "below" or at the given starting node that has less than maxSuccessors.

    Each node that has > maxSuccessors will recursively call this function on all its children.

    The current implementation will be very expensive on large graphs as there is no way (i know of) to "abort" the rest
    of the list comprehension thats being used... perhaps a loop would make more sense..

    For now it 100% does not matter :)

    A better implementation would be
    """

    successors = list(graph.successors(node))
    if len(successors) < maxSuccessors:
        return node

    matches = [
        c
        for c in [
            findNodeWithLowSuccessors(graph, n, maxSuccessors) for n in successors
        ]
        if c is not None
    ]
    # print(node, matches)
    if len(matches) > 0:
        return secrets.choice(matches)

    return None


class TestnGraph:
    def test_recursion(self):
        print("")
        ng = nGraph()

        ng.add_node("0")
        ng.add_edge("0", "A")
        ng.add_edge("0", "B")
        ng.add_edge("A", "1A")
        ng.add_edge("A", "2A")
        ng.add_edge("1A", "12A")
        ng.add_edge("1A", "22A")
        ng.add_edge("2A", "122A")
        ng.add_edge("B", "BB")
        ng.add_edge("B", "BBB")

        ng.add_edge("12A", "lolA")
        # print("A node that matched", findNodeWithLowSuccessors(ng, "0", 1))
        list_of_dangl = [node for node in ng.nodes if ng.out_degree(node) < 1]
        print(list_of_dangl)

    def test_instantiation(self):
        ng = nGraph()
        assert ng is not None


    def test_add_node(self):
        ng = nGraph()
        ng.add_node(Node("test"))
        assert ng.number_of_nodes() == 1

    def test_add_edge(self):
        ng = nGraph()
        A = Node("A")
        B = Node("B")
        ng.add_edge(A, B)
        assert ng.number_of_nodes() == 2
        assert ng.number_of_edges() == 1

    def test_add_same_node_id_more_data(self):
        ng = nGraph()
        A = Node("A", "")

        ng.add_node(A.id, n=A)
        assert ng.number_of_nodes() == 1

        B = Node("A", "some_image_string")
        ng.add_node(B.id, n=B)
        assert (
            ng.number_of_nodes() == 1
        ), "Expected to have only one node, containing the data from node B"

    def test_update_node_data(self):
        ng = nGraph()
        A = Node("A", "")
        ng.add_node(A.id, n=A)
        assert ng.number_of_nodes() == 1

        B = Node("A", "some_image_string")
        ng.add_node(B.id, n=B)
        assert (
            ng.number_of_nodes() == 1
        ), "Expected to have only one node, containing the data from node B"

        ng.nodes.get(B.id)["n"].image = "updated_string"
        assert ng.nodes.get(B.id)["n"].image == "updated_string"

    def test_expanding_dictionary_for_node_attributes(self):
        ng = nGraph()
        nodeData = {"test": 1}
        ng.add_node(0, n=nodeData)
        assert ng.nodes.get(0)["n"]["test"] == 1

        nodeData["test2"] = 2
        ng.add_node(1, **nodeData)
        assert ng.nodes.get(1)["test2"] == 2

    def test_add_mj_Node(self):
        ng = nGraph()
        A = Node("A", "img")
        ng.add_mj_node(A)
        assert ng.nodes.get(A.id)["image"] == "img"

    def test_node_in_graph(self):
        ng = nGraph()
        A = Node("A", "img")
        ng.add_mj_node(A)

        assert A.id in ng
        assert A.id in ng.nodes

    def test_add_duplicate_node_with_less_data(self):
        ng = nGraph()
        A = Node("A", "img")
        ng.add_mj_node(A)

        assert A.id in ng
        assert ng.nodes.get(A.id)["image"] == "img"
        B = Node("A", None)
        ng.add_mj_node(B)

        assert A.id in ng
        assert B.id in ng
        assert ng.number_of_nodes() == 1
        assert ng.nodes.get(A.id)["image"] == "img"

    def test_add_node_with_reference_node(self):
        ng = nGraph()
        A = Node("A", "img")
        ng.add_mj_node(A)
        B = Node("B", "img", reference_job_id=A.id)
        ng.add_mj_node(B)
        assert ng.number_of_nodes() == 2
        assert ng.number_of_edges() == 1
        assert ng.nodes.get(B.id)["reference_job_id"] == A.id

    def test_add_node_with_reference_node_then_fuller_reference_node(self):
        ng = nGraph()

        # "A" is the reference node that we don't yet have!
        A = Node("A", "img")

        # Adding B with only a reference_job_id
        B = Node("B", "img", reference_job_id=A.id)
        ng.add_mj_node(B)

        assert ng.number_of_nodes() == 2
        assert ng.number_of_edges() == 1
        assert ng.nodes.get(B.id)["reference_job_id"] == A.id
        assert (
            ng.nodes.get(A.id)["image"] == None
        )  # this is the case where the reference node has only been added from the id found in B

        # Now add A with the full data, and check that we didn't add a new node, and that the node at that reference id has been updated
        ng.add_mj_node(A)
        assert ng.number_of_nodes() == 2
        assert ng.number_of_edges() == 1
        assert ng.nodes.get(A.id)["image"] == "img"

    def test_multiple_nodes_with_shared_reference(self):
        ng = nGraph()
        A = Node("A", "img")
        B = Node("B", "img", reference_job_id=A.id)
        ng.add_mj_node(B)
        C = Node("C", "img", reference_job_id=A.id)
        ng.add_mj_node(C)
        assert ng.number_of_nodes() == 3
        assert ng.number_of_edges() == 2
        assert ng.nodes.get(A.id)["image"] == None
        assert ng.nodes.get(B.id)["image"] == "img"
        assert ng.nodes.get(C.id)["image"] == "img"

        ng.add_mj_node(A)
        assert ng.number_of_nodes() == 3
        assert ng.number_of_edges() == 2
        assert ng.nodes.get(A.id)["image"] == "img"
