from src.nGraph import nGraph
 

### Obviously not finished...
### Overall idea is to hand one of these things the graph
### And it hands you back a node and what job to call for it.

# really what i'd like is an easy way to define
# A way traverse the graph (walkers)
# A way to apply work to a node (workers)
# A way to track the work applied to a node / its state
# A way to roll up a walker + worker + state into one thing
# A way to save a graph whatever walker,worker,state is called to resume later.



class Randomizer():
    graph:nGraph
    """
        Base class for running random jobs on the graph.
    """
    def run(self,graph:nGraph):
        self.graph = graph
        pass

    def randomFromGraph(self):
        node = self.graph.random_node(type)
        return node



class RandomTreeExpander(Randomizer):
    """
    Picks a random prompt node; 
    
    if that node has <N successors it issues an imagine query for the prompt nodes full command.

    if the prompt node had more than the threshold of successors then it will start "falling down" the tree, 
    """

    def run(graph:nGraph):
