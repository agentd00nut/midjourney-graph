from dash import Dash, html, dcc
import visdcc

MIDJ_USER = ""
try:
    with open("conf\midj.user", "r") as f:
        MIDJ_USER = f.read().strip("\n")
except FileNotFoundError:
    pass

NETOPTS_2 = {
    "nodes": {
        "color": {"highlight": {}, "hover": {}},
        "font": {"size": 0, "strokeWidth": 8},
        "scaling": {"min": 900, "max": 1000},
        "size": 300,
    },
    "configure": {"enabled": True},
    "layout": {
        "hierarchical": {
            "enabled": False,
            "levelSeparation": 200,
            "nodeSpacing": 125,
            "treeSpacing": 300,
            "sortMethod": "directed",
        }
    },
    "edges": {
        "arrows": {"to": {"enabled": True}},
        "font": {"size": 61, "strokeWidth": 3},
        "scaling": {"min": 50, "max": 100},
        "selectionWidth": 26,
        "selfReferenceSize": 15,
        "smooth": {"type": "cubicBezier", "forceDirection": "none", "roundness": 1},
    },
    "manipulation": {"enabled": True, "initiallyActive": True},
    "physics": {
        "forceAtlas2Based": {
            "gravitationalConstant": -29523,
            "centralGravity": 0.005,
            "springLength": 4000,
            "springConstant": 0.05,
            "damping": 0.6,
            "avoidOverlap": 0.88,
        },
        "maxVelocity": 216,
        "minVelocity": 5,
        "solver": "forceAtlas2Based",
        "timestep": 1,
    },
}


NETOPTS = NETOPTS_2

layout = html.Div(
    id="app-container",
    style={
        "display": "flex",
        "flexDirection": "row",
        "background": "#121212",
        "color": "#FFFFFF",
    },
    children=[
        html.Div(
            id="interface-container",
            style={
                "display": "flex",
                "flexDirection": "column",
                "order": 1,
                "flexGrow": 2,
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
                html.Div(
                    id="input-container",
                    style={"order": 1},
                    children=[
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
                                            value=30,
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
                                        html.Br(),
                                        html.Button(
                                            "clear graph", id="clear", n_clicks=0
                                        ),
                                        html.Button(
                                            "dothing", id="dothing", n_clicks=0
                                        ),
                                    ],
                                    style={"paddingBottom": "30px"},
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
            style={"position": "absolute", "alignItems": "center", "right": "0px"},
        ),
    ],
)
