from dash import Dash, html, dcc, Input, Output, State, dash
import visdcc

MIDJ_USER = ""
try:
    with open("conf\midj.user", "r") as f:
        MIDJ_USER = f.read().strip("\n")
except FileNotFoundError:
    pass

NETOPTS_2 = {
    "nodes": {
        "borderWidth": None,
        "borderWidthSelected": None,
        "color": {"highlight": {}, "hover": {}},
        "font": {"size": 23, "strokeWidth": None},
        "scaling": {"min": 106, "max": 200},
        "shapeProperties": {"borderRadius": None},
        "size": 17,
    },
    "edges": {
        "arrows": {"to": {"enabled": True}},
        "font": {"size": 61, "strokeWidth": 3},
        "scaling": {"min": 11},
        "selectionWidth": 8,
        "selfReferenceSize": 15,
        "smooth": False,
    },
    "manipulation": {"enabled": True, "initiallyActive": True},
    "physics": {
        "repulsion": {
            "centralGravity": 2.25,
            "springLength": 450,
            "nodeDistance": 2075,
            "damping": 0.21,
        },
        "minVelocity": 0.75,
        "solver": "repulsion",
    },
}

NETOPTS = dict(
    # height='400px',
    # width='60%',
    nodes={
        "scaling": {"min": 10, "max": 50},
        "value": 1,
        "size": 17,
        "font": {"size": 23},
        "scaling": {"min": 106, "max": 200},
    },
    configure={"enabled": False},
    layout={
        "hierarchical": {
            "enabled": False,
            "levelSeparation": 200,
            "nodeSpacing": 125,
            "treeSpacing": 300,
            "sortMethod": "directed",
        }
    },
    edges={
        "arrows": {"to": {"enabled": True, "scaleFactor": 1}},
        "font": {"size": 61, "strokeWidth": 3},
        "selectionWidth": 8,
        "scaling": {"min": 11},
        "selectionWidth": 8,
        "selfReferenceSize": 15,
        "value": 1,
        "smooth": False,
    },
    manipulation={
        "enabled": True,
        "initiallyActive": True  # "initiallyActive": True,
        # "addNode": False,
        # "addEdge": False,
        # "deleteNode": True,
        # "deleteEdge": True,
    },
    physics={
        "repulsion": {
            "springLength": 475,
            "springConstant": 0.01,
            "nodeDistance": 500,
            "damping": 0.07,
        },
        "hierarchicalRepulsion": {
            "centralGravity": 0,
            "springLength": 475,
            "nodeDistance": 500,
            "damping": 0.09,
        },
        "minVelocity": 0.75,
        "solver": "repulsion",
    },
)


NETOPTS = NETOPTS_2

layout = html.Div(
    id="app-container",
    style={"display": "flex", "flexDirection": "row"},
    children=[
        html.Div(
            id="interface-container",
            style={
                "display": "flex",
                "flexDirection": "column",
                "order": 1,
                "flex-grow": 2,
            },
            children=[
                html.Div(
                    id="graph-container",
                    children=[
                        html.Div(
                            style={"order": 1, "width": "16vw"}, id="graphControls"
                        ),  # Style gets set by the graph_controls_button callback
                        visdcc.Network(
                            id="net",
                            selection={"nodes": [], "edges": []},
                            data={"nodes": [], "edges": []},
                            style={"height": "100%", "width": "100%", "order": 2},
                            options=NETOPTS,
                        ),
                    ],
                    style={
                        "display": "flex",
                        "flexDirection": "row",
                        "width": "100wh",
                        "height": "70vh",
                        "order": 1,
                    },
                ),
                dcc.Interval(
                    id="interval-update-graph",
                    interval=30 * 1000,
                    n_intervals=0,
                    disabled=False,
                ),
                dcc.Interval(
                    id="interval-random-job",
                    interval=90 * 1000,
                    n_intervals=0,
                    disabled=False,
                ),
                html.Div(
                    id="input-container",
                    style={"order": 1},
                    children=[
                        html.Div(id="random_job_id"),
                        html.Div(id="node_info"),
                        html.Div(id="configure"),
                        html.Div(
                            [
                                html.Button(
                                    "Graph Controls",
                                    id="graph_controls_button",
                                    n_clicks=0,
                                ),
                                html.Button("fast", id="fast", n_clicks=0),
                                html.Button("relax", id="relax", n_clicks=0),
                                html.Br(),
                                dcc.Input(
                                    type="text", id="prompt", value="", debounce=True
                                ),
                                dcc.Input(
                                    type="text",
                                    id="modifiers",
                                    value="--uplight --q 2 --mp ",
                                    debounce=True,
                                ),
                                html.Button("imagine", id="imagine", n_clicks=0),
                                html.Br(),
                                dcc.Input(
                                    id="image_selection",
                                    min=1,
                                    max=4,
                                    step=1,
                                    value=1,
                                    type="range",
                                ),
                                html.Button(
                                    "V<>",
                                    id="variance",
                                    name="variance_button",
                                    value="variation",
                                ),
                                html.Button(
                                    "U<>",
                                    id="upsample",
                                    name="upscale_button",
                                    value="upsample",
                                ),
                                # for 2x2 images...
                                html.Button(
                                    "reroll",
                                    id="reroll",
                                    name="reroll_button",
                                    value="reroll",
                                ),
                                html.Button(
                                    "Make Variations",
                                    id="make_variations",
                                    name="make_variations_button",
                                    value="variation",
                                ),  # TODO:: Only show if the node is an upsampled image
                                html.Button(
                                    "Max Upscale",
                                    id="maxup",
                                    name="maxup",
                                    value="maxup",
                                ),
                                # TODO:: Button for "upscale to max" if availabe... Also need to determine how we might know if that's possible or not...
                                html.Div(id="jobStatus"),
                                html.Div(id="imagineStatus"),
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
                                            style={"width": "50px"},
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
                                            style={"width": "40px"},
                                        ),
                                        "jobsPerQuery:",
                                        dcc.Input(
                                            id="jobsPerQuery",
                                            placeholder="Jobs per query",
                                            type="number",
                                            debounce=True,
                                            min=1,
                                            max=100,
                                            value=4,
                                            style={"width": "40px"},
                                        ),
                                        "Start Page:",
                                        dcc.Input(
                                            id="page",
                                            placeholder="Enter a page number to start on, 0 is first...",
                                            type="number",
                                            debounce=True,
                                            min=1,
                                            value=1,
                                            style={"width": "40px"},
                                        ),
                                        html.Button(
                                            "Refresh_Graph",
                                            id="refresh_graph",
                                            name="refresh_graph_button",
                                        ),
                                        html.Button(
                                            "Random_Job",
                                            id="random_job",
                                            name="randomb_job_button",
                                        ),
                                        html.Button(
                                            "RunRandomOff",
                                            id="toggle_random",
                                            value="1",
                                        ),
                                        html.Br(),
                                        html.Button(
                                            "clear graph", id="clear", n_clicks=0
                                        ),
                                    ],
                                    style={"padding-bottom": "30px"},
                                ),
                            ],
                        ),
                        html.Div(id="edges"),
                    ],
                ),
            ],
        ),
        html.Div(
            id="nodes",
            style={"position": "absolute", "align-items": "center", "right": "0px"},
        ),
    ],
)
