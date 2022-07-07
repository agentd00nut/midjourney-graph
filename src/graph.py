from src.job import jobFromJson
from src.mj import makeMidJourneyRequest
from src.node import Node, nodeFromJob
from src.edge import Edge


class Graph:
    nodes: dict[str, Node]
    edges: dict[str, Edge]

    def __init__(self):
        self.nodes = {}
        self.edges = {}

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

        # Check if the node already exists and has an image.
        if self.hasNode(node) and self.nodes[node.id].image is not None:
            print(" node already exists", node.id)
            return False

        # Check if top level node that was not a reference.
        if node.reference_job_id is None and not node.isReferenceNode:
            promptNode = node.promptNode()
            if not self.hasNode(promptNode):
                print(" adding prompt node", promptNode.id,
                      "...", promptNode.label)
                self.nodes[promptNode.id] = promptNode

            # Add an edge from the node to the prompt node.
            self.addEdge(node.promptEdge())

        if node.image is None:
            r = makeMidJourneyRequest(
                "https://www.midjourney.com/api/app/job-status/", "{\"jobIds\":[\""+node.id+"\"]}")
            print("     fetching node", node.id, "...")

            if r is None or r.status_code != 200:
                print("\n\nError fetching node", node.id, "\n\n")
                return False
            job = jobFromJson(r.json()[0])
            node = nodeFromJob(job)
            if self.addNode(node):
                if node.reference_job_id is not None:
                    print("Fetched node needs to add its reference",
                          node.reference_job_id)
                    return self.addNode(node.getReferenceNodeNoRequest())
                return True

            return False

        # Add the node to the graph.
        self.nodes[node.id] = node
        self.addEdge(node.referenceEdge())
        return True

    def addNodesReferences(self, node: Node):
        if node is None:
            return

        while node.reference_job_id != None:
            if node is None:
                break

            # Get the cheap reference node
            referance_node = node.getReferenceNodeNoRequest()
            print(node.id, " <- ", referance_node.id)

            if self.hasNode(referance_node):
                # Check if the reference node stored in the graph is missing an image, if it is we need to fetch the job-status from midjourney and convert into a node
                if self.nodes[referance_node.id].image is None:
                    
                    print(
                        "     stored node had no image, fetching reference node from job-status", referance_node.id)
                    r = makeMidJourneyRequest(
                        "https://www.midjourney.com/api/app/job-status/", "{\"jobIds\":[\""+referance_node.id+"\"]}")
                    if r is None or r.status_code != 200:
                        print("     Error fetching node", referance_node.id)
                        break

                    job = jobFromJson(r.json()[0])
                    referance_node = nodeFromJob(job)
                    referance_node.isReferenceNode = True
                else:
                    print(
                        "     Node that exists already has image, breaking out", referance_node.id)
                    break

            if not self.addNode(referance_node):
                #print("graph had node, breaking out of addReferencesForNode")
                break

            node = referance_node
