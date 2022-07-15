from dataclasses import asdict, astuple
import pytest

from src.nGraph import nGraph
from src.node import Node
from src.edge import Edge

class TestnGraph:
    def test_instantiation(self):
        n=Node()
        assert n is not None

    def test_ge(self):
        A = Node('A','')
        B = Node('A','some_image_string')
        C = Node('C','')
        assert A.id == B.id
        assert B > A
        assert C != A
        
        # Assert that comparison of GE or LE between A and C will throw Exceptions
        with pytest.raises(Exception):
            assert A > C

        A.image='some_image_string'

        assert A == B

    def test_node_addition(self):
        A = Node('A','')
        B = Node('A','some_image_string')

        assert A.id == B.id

        A=A+B

        assert A.id == B.id
        assert A.image == B.image

