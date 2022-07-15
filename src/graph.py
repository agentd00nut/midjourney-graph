from dataclasses import asdict
import random
from src.job import jobFromJson
from src.mj import mj_POST
from src.node import Node, NodeType, nodeFromJob
from src.edge import Edge
import secrets


class Graph:
    nodes: dict[str, Node]
    edges: dict[str, Edge]

    def __init__(self):
        self.nodes = {}
        self.edges = {}

    def getRandomNode(self):
        n = len(self.nodes)
        if n == 0:
            return None

        return (list(self.nodes.values()))[secrets.randbelow(n)]

    def hasId(self, id: str):
        return id in self.nodes

    def hasNode(self, node: Node):
        if node.id in self.nodes:
            # if the node is a prompt node we do not need to check if it has an image.
            if node.isPromptNode:
                return True
            # if the node IS missing an image we'll need to fetch it, so we say the node not in the graph
            return self.nodes[node.id].image is not None
        return False

    def addEdge(self, edge: Edge):
        if edge is None:
            return
        if edge.id not in self.edges:
            print(" adding edge", edge.id)
            self.edges[edge.id] = edge

    def getNode(self, nodeId: str):
        if self.hasId(nodeId):
            return self.nodes[nodeId]
        return None

    def addNode(self, node: Node):
        print("addNode", node.id, node.reference_job_id)

        # Check if the node already exists and has an image and has a non 0 accumulated_duration ()
        if self.hasNode(node) and self.nodes[node.id].image is not None:
            print(" node already exists", node.id)
            return False

        # Check if top level node that was not a reference.
        if node.reference_job_id is None and node.type == NodeType.reference:
            promptNode = node.getPromptNode()
            if not self.hasNode(promptNode):
                print(" adding prompt node", promptNode.id, "...", promptNode.label)
                self.nodes[promptNode.id] = promptNode

            # Add an edge from the node to the prompt node.
            self.addEdge(node.getPromptEdge())

        # The node we got has no image; we need to fetch it from midjourney
        if node.image is None:
            r = mj_POST(
                "https://www.midjourney.com/api/app/job-status/",
                '{"jobIds":["' + node.id + '"]}',
            )
            print("     fetching node", node.id, "...")

            if r is None or r.status_code != 200:
                print("\n\nError fetching node", node.id, "\n\n")
                return False
            job = jobFromJson(r.json()[0])
            node = nodeFromJob(job)
            if self.addNode(node):
                if node.reference_job_id is not None:
                    print(
                        "Fetched node needs to add its reference", node.reference_job_id
                    )
                    return self.addNode(node.getReferenceNodeNoRequest())
                return True

            return False

        # Add the node to the graph.
        self.nodes[node.id] = node
        self.addEdge(node.getReferenceEdge())
        return True

    # def addNodesReferences(self, node: Node):
    #     if node is None:
    #         return

    #     while node.reference_job_id != None:
    #         if node is None:
    #             break

    #         # Get the cheap reference node
    #         referance_node = node.getReferenceNodeNoRequest()
    #         print(node.id, " <- ", referance_node.id)

    #         if self.hasNode(referance_node):
    #             # Check if the reference node stored in the graph is missing an image, if it is we need to fetch the job-status from midjourney and convert into a node
    #             if self.nodes[referance_node.id].image is None:

    #                 print(
    #                     "     stored node had no image, fetching reference node from job-status", referance_node.id)
    #                 r = makeMidJourneyRequest(
    #                     "https://www.midjourney.com/api/app/job-status/", "{\"jobIds\":[\""+referance_node.id+"\"]}")
    #                 if r is None or r.status_code != 200:
    #                     print("     Error fetching node", referance_node.id)
    #                     break

    #                 job = jobFromJson(r.json()[0])
    #                 referance_node = nodeFromJob(job)
    #                 referance_node.isReferenceNode = True
    #             else:
    #                 print(
    #                     "     Node that exists already has image, breaking out", referance_node.id)
    #                 break

    #         if not self.addNode(referance_node):
    #             #print("graph had node, breaking out of addReferencesForNode")
    #             break

    #         node = referance_node

    def getVisDCCData(self):
        import json

        return json.dumps(
            {
                "nodes": [asdict(self.nodes[n]) for n in self.nodes],
                "edges": [self.edges[e].asGraphEdge() for e in self.edges],
            }
        )
