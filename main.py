from dataclasses import asdict
from time import sleep
from dash import Dash, html, dcc, Input, Output, callback
from dash.dependencies import Input, Output
import networkx as nx

from src.callbacks.randomJob import random_job
from src.callbacks.runJob import runJob
from src.callbacks.selection import selection as cb_selection

import visdcc
from src.job import jobFromJson
from src.mj import getJobStatus, getRecentJobsForUser
from src.node import NodeType, nodeFromJob
from src.graph import Graph
from src.nGraph import nGraph

app = Dash(__name__)

MIDJ_USER = ""
try:
    with open("conf\midj.user", "r") as f:
        MIDJ_USER = f.read().strip("\n")
except FileNotFoundError:
    pass

NETOPTS = dict(
    # height='400px',
    # width='60%',
    nodes={"size": 50},
    configure={"enabled": False, "filter": ["physics", "layout"]},
    # layout={'clusterThreshold':10},
    edges={
        "smooth": {"enabled": False},
        "arrows": {"to": {"enabled": True, "scaleFactor": 1}},
    },
    physics={
        "barnesHut": {
            "gravitationalConstant": -46688,
            "centralGravity": 0.95,
            "springLength": 120,
            "springConstant": 0.125,
            "damping": 0.4,
        },
        "minVelocity": 0.75,
        "timestep": 0.3,
    },
)

app.layout = html.Div(
    [
        html.Div(
            [
                html.Div(
                    id="graphControls"
                ),  # Style gets set by the graph_controls_button callback
                html.Div(
                    visdcc.Network(
                        id="net",
                        selection={"nodes": [], "edges": []},
                        data={"nodes": [], "edges": []},
                        style={"height": "100%"},
                        options=NETOPTS,
                    ),
                    style={"width": "80%", "height": "400px", "flex": "1"},
                ),
            ],
            id="graph",
            style={
                "width": "100%",
                "height": "400px",
                "display": "flex",
                "flexDirection": "row",
                "justifyContent": "space-between",
            },
        ),
        dcc.Interval(
            id="interval-update-graph", interval=30 * 1000, n_intervals=0, disabled=True
        ),
        # dcc.Interval(
        #     id="interval-random-job", interval=120 * 1000, n_intervals=0, disabled=True
        # ),
        html.Div(id="random_job_id"),
        html.Div(id="node_info"),
        html.Div(id="configure"),
        html.Div(
            [
                html.Button("Graph Controls", id="graph_controls_button", n_clicks=0),
                dcc.Input(
                    id="image_selection", min=1, max=4, step=1, value=1, type="range"
                ),
                html.Button(
                    "V<>", id="variance", name="variance_button", value="variation"
                ),
                html.Button(
                    "U<>", id="upsample", name="upscale_button", value="upsample"
                ),
                # for 2x2 images...
                html.Button(
                    "reroll", id="reroll", name="reroll_button", value="reroll"
                ),
                html.Button(
                    "Make Variations",
                    id="make_variations",
                    name="make_variations_button",
                    value="variation",
                ),  # TODO:: Only show if the node is an upsampled image
                # TODO:: Button for "upscale to max" if availabe... Also need to determine how we might know if that's possible or not...
                html.Div(id="jobStatus"),
            ],
            id="jobInputs",
        ),
        html.Div(
            id="midjourneyInputs",
            children=[
                html.P(
                    [
                        "userId",
                        dcc.Input(
                            id="userId",
                            placeholder="Enter a user Id ...",
                            type="text",
                            value=MIDJ_USER,
                        ),  # Add your midjourney userid here
                        "numberOfJobs:",
                        dcc.Input(
                            id="numJobs",
                            placeholder="Enter a max number of jobs",
                            type="number",
                            name="numJobs",
                            min=1,
                            debounce=True,
                            value=1,
                        ),
                        "jobsPerQuery:",
                        dcc.Input(
                            id="jobsPerQuery",
                            placeholder="Jobs per query",
                            type="number",
                            debounce=True,
                            min=1,
                            max=100,
                            value=10,
                        ),
                        "Start Page:",
                        dcc.Input(
                            id="page",
                            placeholder="Enter a page number to start on, 0 is first...",
                            type="number",
                            debounce=True,
                            min=1,
                            value=1,
                        ),
                        html.Button(
                            "Refresh_Graph",
                            id="refresh_graph",
                            name="refresh_graph_button",
                        ),
                        html.Button(
                            "Random_Job", id="random_job", name="randomb_job_button"
                        ),
                    ],
                    style={"padding-bottom": "30px"},
                ),
            ],
        ),
        html.Div(id="nodes"),
        html.Div(id="edges"),
    ]
)


graph = nGraph()


@app.callback(Output("nodes", "children"), [Input("net", "selection")])
def callSelection(selection):
    global graph
    return cb_selection(graph, selection)


@app.callback(
    Output("graphControls", "style"), Input("graph_controls_button", "n_clicks")
)
def callGraphControls(n_clicks):
    if n_clicks % 2 == 0:
        return {"width": "20%", "overflow": "auto", "display": "none"}
    else:
        return {"width": "20%", "overflow": "auto"}


@app.callback(Output("net", "run"), [Input("graphControls", "id")])
def initControls(controls):
    """
    Initialize the controls for the graph.

    We have to do it this way, apparently, since visjss expects a DOM element and not just an id.
    And we don't have a way (that i know of) to get the DOM element from python... lol there's probably like a one line way to do it.
    """

    return f"""
    let controls=document.getElementById('{controls}');
    
    let options = this.props.options;
    options.configure.enabled = true;
    options.configure.container=controls;

    console.log("adding opts to net");
    this.net.setOptions(options);
    """


# @app.callback(
#     Output('random_job_id', 'children'),
#     [ Input('interval-random-job', 'n_intervals'), Input('random_job','n_clicks') ])
# def callRandomJob(n_intervals, n_clicks):
#     global graph
#     return random_job(graph)


@app.callback(
    Output("jobStatus", "children"),
    [
        Input("net", "selection"),
        Input("image_selection", "value"),
        Input("variance", "n_clicks"),
        Input("upsample", "n_clicks"),
        Input("reroll", "n_clicks"),
        Input("make_variations", "n_clicks"),
        Input("jobStatus", "children"),
    ],
)
def runAJob(selections, value, variance, upsample, reroll, make_variations, jobStatus):
    global graph
    return runJob(
        graph, selections, value, variance, upsample, reroll, make_variations, jobStatus
    )


@app.callback(Output("edges", "children"), [Input("net", "selection")])
def selectedEdges(x):
    if x is None or len(x["edges"]) == 0:
        return html.Div("")

    s = "Selected edges:"
    if len(x["nodes"]) > 0:  # Selecting just an edge is possible!
        s = s + "for " + str(x["nodes"][0]) + " : "
    if len(x["edges"]) > 0:
        s = [s] + [html.Div(i) for i in x["edges"]]
    return s


@app.callback(
    Output("net", "data"),
    [
        Input("userId", "value"),
        Input("numJobs", "value"),
        Input("page", "value"),
        Input("jobsPerQuery", "value"),
        Input("refresh_graph", "n_clicks"),
        Input("interval-update-graph", "n_intervals"),
    ],
)
def mainFun(userId, numJobs, page, jobsPerQuery, refresh_graph, intervals):
    global graph
    # https://visjs.github.io/vis-network/docs/network/#methodLayout

    page = int(page)
    maxJobs = int(numJobs)

    # Get the recent jobs for the user; keep paginating until we've exceeded the max jobs.
    recent_jobs = getRecentJobsForUser(userId, page, jobsPerQuery, maxJobs)

    nodes = [n for n in [nodeFromJob(jobFromJson(j)) for j in recent_jobs]]
    print("Got", len(nodes), "new nodes from", len(recent_jobs), "recent jobs")

    if len(nodes) == 0:
        data = graph.getVisDCCData()
        print("DATA::::NO NODES::::", data)
        return data

    # Add all the nodes to the graph.
    for n in nodes:
        graph.add_mj_node(n)

    # Get all reference nodes from the graph, make a single batch request for all of them, and add the resulting nodes back to the graph
    ref_nodes = [0, 0]
    while len(ref_nodes) > 0:
        ref_nodes = [
            n
            for n in graph.nodes(data=True)
            if n[1]["type"] == NodeType.reference and not n[1]["image"]
        ]
        print(f"Fetching {len(ref_nodes)} reference nodes")
        if len(ref_nodes) <= 0:
            break

        ref_nodes_to_add = [
            nodeFromJob(jobFromJson(j))
            for j in getJobStatus([n[1]["id"] for n in ref_nodes]).json()
        ]
        for n in ref_nodes_to_add:
            graph.add_mj_node(n)

    data = graph.getVisDCCData()

    # print("DATA:::",data)
    return data


if __name__ == "__main__":
    app.run_server(
        debug=True,
    )
