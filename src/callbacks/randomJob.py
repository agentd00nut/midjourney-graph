import secrets
from dash import Dash, html, dcc
import random
from src.discord import DiscordLink
from src.nGraph import nGraph

from src.mj import getRunningJobsForUser
from src.node import NodeType
from src.node import Node


def getJobs(userId: str):

    jobs = getRunningJobsForUser(userId, 20)
    if not jobs:
        return None

    jobs = jobs.json()

    print("Got recent this many recent jobs: ", len(jobs))
    if len(jobs) >= 10:  # lazy way to deal with delays in the api
        print("Too many jobs running to add a random one")
        return None

    return jobs


# [node for node in ng.nodes if ng.out_degree(node) < 1]
import networkx as nx


def random_job(graph: nGraph, userId: str, type: NodeType = None):
    DL = DiscordLink()
    print("random_job")

    jobs = getJobs(userId)
    if jobs is None:
        print(" Jobs was none!")
        return html.Div([html.H4("Too many running jobs")])

    node = graph.random_node(type)
    if node is None:
        print("the randome Node was none!")
        return html.Div([html.H4("No nodes in graph")])

    # If a prompt node already has enough children, switch to run a job on one of its children.
    if node.type == type and type == NodeType.prompt:
        maxChildren = 2
        if graph.out_degree(node.id) < maxChildren:
            print(DL.imagine(node.id, node))
            return html.Div([html.H4("Running prompt as random job: " + node.prompt)])

        # Get a different random prompt node.
        promptNodes = [
            n
            for n in graph.nodes.data("type")
            if n[1] == NodeType.prompt
            and n[0] != node.id
            and len(list(graph.successors(n[0]))) < maxChildren
        ]
        if len(promptNodes) == 0:
            print(
                "THERE ARE NO PROMPT NODES WITH FEWER THAN ", maxChildren, " CHILDREN"
            )
            print("Picking a node with no descendents for a variation job.")
            nodeId = secrets.choice(
                [n for n in list(graph.nodes) if graph.out_degree(n) == 0]
            )
            node = graph.nodes[nodeId]["node"]
        # Get a random node from descendents of prompt node that was picked.
        # node = secrets.choice(
        #     [n for n in list(nx.descendants(graph, node.id)) if graph.out_degree(n) < 3]
        # )
        # node = graph.nodes[node]["node"]

    if len(node.job.image_paths) == 1:  #  upsample
        jobType = "MJ::JOB::variation::1::SOLO"
        jobNumber = 1
    elif len(node.job.image_paths) == 4:  # variation
        jobTypes = ["MJ::JOB::variation::"]  # , "MJ::JOB::upsample::"]
        # randomly select a job type from the jobTypes list
        jobType = secrets.choice(jobTypes)
        jobNumber = secrets.choice([1, 2, 3, 4])
        jobType = jobType + str(jobNumber)
    elif node.reference_job_id is not None:  # root node
        jobType = "MJ::JOB::reroll::0::SOLO"
        jobNumber = 0

    print(
        "Running the random job of type: "
        + str(jobType)
        + " with job number: "
        + str(jobNumber)
        + "on node "
        + str(node.id)
    )
    result = DL.runJob(node, jobType)
    if not result:
        return html.Div(
            [
                html.H3(
                    f"Failed to run {jobType} for {node.id}... reason: {result.text}... repeated failures mean you should probably stop"
                )
            ]
        )

    return html.Div([html.H4(f"Added {jobType} job for {node.id}")])
