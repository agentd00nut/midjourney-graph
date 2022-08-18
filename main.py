from time import sleep
from dash import Dash, html, dcc, Input, Output, State, dash
from dash.dependencies import Input, Output
from dash._callback_context import callback_context
from src.callbacks.randomJob import random_job
from src.callbacks.runJob import runJob
from src.callbacks.selection import selection as cb_selection

from src.discord import DiscordLink
from src.job import jobFromJson
from src.mj import getJobStatus, getRecentJobsForUser
from src.node import NodeType, nodeFromJob
from src.nGraph import nGraph
from src.layout import layout
app = Dash(__name__)




app.layout = layout
graph = nGraph()


@app.callback(Output("clear", "n_clicks"), [Input("clear", "n_clicks")])
def callSelection(selection):
    global graph
    graph.clear()
    print("clearing graph")
    # TODO:: call the graph to redraw itself...

    return 0


@app.callback(Output("nodes", "children"), [Input("net", "selection")])
def callSelection(selection):
    global graph
    return cb_selection(graph, selection)


@app.callback(
    Output("graphControls", "style"), Input("graph_controls_button", "n_clicks")
)
def callGraphControls(n_clicks):
    if n_clicks % 2 == 0:
        return {"width": "16vw", "overflow": "auto", "display": "none"}
    else:
        return {"width": "16vw", "overflow": "auto"}


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


run_random_job = 0


@app.callback(Output("toggle_random", "children"), [Input("toggle_random", "value")])
def toggleRandomRun(value):
    callback_context.triggered[0]["prop_id"]
    global run_random_job
    if run_random_job == 0:
        run_random_job = 1
        return "Run Random On"
    else:
        run_random_job = 0
        return "Run Random Off"


@app.callback(
    Output("random_job", "n_clicks"),
    [Input("interval-random-job", "n_intervals"), Input("random_job", "n_clicks")],
    
)
def callRandomJob(n_intervals, n_clicks):
    global graph
    print(random_job(graph, MIDJ_USER))
    return 1


lastFast = 0
lastRelax = 0
lastImagine = 0
lastMax = 0
mode = "fast"


@app.callback(
    Output("maxup", "n_clicks"),
    [
        Input("maxup", "n_clicks"),
    ],
    State("net", "selection"),
)
def runMax(max, selections):
    global graph, mode
    if len(selections["nodes"]) == 0:
        print("No nodes selected")
        return 0
    node = graph.nodes[selections["nodes"][0]]
    if max == 0:
        return 0
    DL = DiscordLink()
    if mode == "relax":
        print("Going fast first")
        DL.fast()
        sleep(0.2)
        results = DL.max(node["node"])
        sleep(0.2)
        DL.relax()
        print("Back to relaxed!")
    else:
        results = DL.max(node["node"])

    return 0


@app.callback(
    Output("fast", "n_clicks"),
    [
        Input("fast", "n_clicks"),
    ],
)
def runFast(fast):
    global lastFast, mode
    if fast == lastFast:
        return lastFast
    lastFast = fast + 1
    DL = DiscordLink()
    results = DL.fast()
    mode = "fast"
    print(mode)
    return lastFast


lastRelax = 0


@app.callback(
    Output("relax", "n_clicks"),
    [
        Input("relax", "n_clicks"),
    ],
)
def runRelax(relax):
    global lastRelax, mode
    if relax == lastRelax:
        return lastRelax
    lastRelax = relax + 1
    DL = DiscordLink()
    results = DL.relax()
    mode = "relax"
    print(mode)
    return lastRelax


@app.callback(
    Output("imagineStatus", "children"),
    [
        Input("imagine", "n_clicks"),
    ],
    State("prompt", "value"),
    State("modifiers", "value"),
)
def runImagine(imagine, prompt, value):
    global graph, lastImagine
    if imagine == lastImagine:
        return html.Div()

    DL = DiscordLink()
    results = DL.imagine(prompt + " " + value)

    if results:
        return html.Div("/imagine prompt:" + prompt + " " + value)

    return html.Div()


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
    app.run_server(debug=True, host="192.168.50.160", port=8050)
