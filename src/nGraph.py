from dataclasses import asdict
import json
import secrets
import networkx as nx
from src.node import Node, NodeType
from src.edge import Edge

# TODO:: Use an actual logger with levels
class nGraph(nx.DiGraph):
    def __init__(self) -> None:
        super().__init__(self)

    def add_mj_node(self, node: Node):

        if node is None:
            # print("???: GOT NONE FOR node")
            return
        suffix = str(node.id)[0:3] + ":"

        # print(suffix, "Adding", node.id)
        if node.id in self.nodes:
            node = self.nodes[node.id]["node"] + node

        super().add_node(node.id, **asdict(node), node=node)

        if node.reference_job_id is not None:
            # print(
            #     suffix,
            #     " Adding reference node and edges",
            #     node.id,
            #     "<=>",
            #     node.reference_job_id,
            # )
            self.add_mj_node(node.getReferenceNodeNoRequest())
            referenceEdge = node.getReferenceEdge()
            # print(suffix, "     ReferenceEdge:", referenceEdge)
            if referenceEdge is not None:
                self.add_edge(
                    referenceEdge.from_, referenceEdge.to, **referenceEdge.asGraphEdge()
                )
        elif (
            node.type != NodeType.prompt and node.image
        ):  # "no request" reference nodes have no image, so we check for one to avoid thinking they are "root" nodes by accident... perhaps we should scan the results of the "recent job" scans / anything tht passes through "jobToNode" that does not have an image and specifically set those as "root" so we can have a simpler check for them.
            promptNode = node.getPromptNode()
            promptEdge = node.getPromptEdge()
            # print(suffix, "  Node 'root' level...")
            if promptNode.id in self.nodes:
                # print(
                #     suffix,
                #     "     PromptNode already exists",
                #     promptNode.id,
                #     "adding edge: ",
                #     promptEdge.id,
                # )
                self.add_edge(
                    promptEdge.from_, promptEdge.to, **promptEdge.asGraphEdge()
                )
                return
            else:
                # print(
                #     suffix,
                #     "     ```PromptNode does``` not exist",
                #     promptNode.id,
                #     "adding node and edge: ",
                #     promptEdge.id,
                # )
                self.add_mj_node(promptNode)
                self.add_edge(
                    promptEdge.from_, promptEdge.to, **promptEdge.asGraphEdge()
                )
            # print(
            #     suffix,
            #     " Adding prompt node and edges",
            #     node.id,
            #     promptNode.id,
            #     promptEdge.id,
            # )

    def getVisDCCData(self):
        wow = {}
        wow = {
            "nodes": [n[1]["node"].asvisDCCData() for n in self.nodes(data=True)],
            "edges": [e[2] for e in self.edges(data=True)],
        }

        return wow
