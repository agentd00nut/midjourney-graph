import secrets
import time
from dash import Dash, html, dcc
import random
from src.discord import DISCORD_LIVEJOBS, DISCORD_LIVEJOBS_LAST_UPDATE, DiscordLink
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


PROMPT_IGNORE_LIST = []
with open("conf\discord.cookie", "r") as f:
    PROMPT_IGNORE_LIST = f.read().splitlines()
    print("Loaded ", len(PROMPT_IGNORE_LIST), " prompts to ignore")


# [node for node in ng.nodes if ng.out_degree(node) < 1]
import networkx as nx


# I know this is not how you need to use globals; i was trying to see if doing it this
#       way would let threads get "updated" globals... it did not, and now
#       it looks really dumb :)
def fetchLastUpdate():
    global DISCORD_LIVEJOBS_LAST_UPDATE
    return int(DISCORD_LIVEJOBS_LAST_UPDATE)


def setLastUpdate(x):
    global DISCORD_LIVEJOBS_LAST_UPDATE
    DISCORD_LIVEJOBS_LAST_UPDATE = x


def fetchLiveJobs():
    global DISCORD_LIVEJOBS
    return int(DISCORD_LIVEJOBS)


def setLiveJobs(x):
    global DISCORD_LIVEJOBS
    DISCORD_LIVEJOBS = x


def random_job(graph: nGraph, userId: str, type: NodeType = NodeType.prompt):
    global PROMPT_IGNORE_LIST
    DL = DiscordLink()
    maxChildren = 5
    last = int(fetchLastUpdate())

    if (int(time.time()) - last) > 20:

        lastInfoRequest = 0.0
        while last == fetchLastUpdate():
            if lastInfoRequest == 0.0 or time.time() - lastInfoRequest > 5:
                print("Sending info request...")
                print(DL.info())
                lastInfoRequest = time.time()
                setLastUpdate(lastInfoRequest)
            time.sleep(1.0)
            print(
                f"Waiting for updated job count... lastUpdate:{last}, live:{fetchLastUpdate()}, jobs:{fetchLiveJobs()}... lastInfoRequest:{lastInfoRequest}"
            )
    jobs = fetchLiveJobs()
    if jobs > 5:
        print("Too many jobs!")
        return html.Div([html.H4("too many running jobs")])

    jobs = jobs + 1
    setLiveJobs(jobs)

    print("There are now", jobs, "Running jobs")

    node = graph.random_node(type)
    if node is None:
        print("the randome Node was none!")
        return html.Div([html.H4("No nodes in graph")])

    # If a prompt node already has enough children, switch to run a job on one of its children.
    if node.type == type and type == NodeType.prompt:

        if graph.out_degree(node.id) < maxChildren:
            print(DL.imagine(node.id, node))
            return html.Div([html.H4("Running prompt as random job: " + node.prompt)])

        # Get a different random prompt node.
        promptNodes = [
            n
            for n in graph.nodes.data("type")
            if n[1] == NodeType.prompt
            and n[0] != node.id
            and n[0] not in PROMPT_IGNORE_LIST
            and len(list(graph.successors(n[0]))) < maxChildren
        ]
        if len(promptNodes) == 0:
            # print(
            #     "THERE ARE NO PROMPT NODES WITH FEWER THAN ", maxChildren, " CHILDREN"
            # )
            print("Picking a node with no descendents for a variation job.")
            node = secrets.choice(
                [
                    n
                    for n in graph.nodes(data=True)
                    if "--beta" not in n[0]
                    and "--upbeta" not in n[0]
                    and graph.out_degree(n[0]) == 0
                ]
            )[1]["node"]
            # print("Node id we picked as alternative:", nodeId)
            # node = graph.nodes[nodeId]["node"]
            # print("And the node itself we picked:", node)
        else:
            print("Chosen node had too many children... fetching another instead")
            node = graph.nodes[secrets.choice(promptNodes)[0]]["node"]
            print(DL.imagine(node.id, node))
            return html.Div([html.H4("Running prompt as random job: " + node.prompt)])
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
