import networkx as nx
from dash import Dash, html, dcc
from dash.dependencies import Input, Output, State
import visdcc

app = Dash(__name__)
app.layout = html.Div(
    [
        visdcc.Network(id="net", options=dict(height="600px", width="100%")),
        dcc.Input(id="label", placeholder="Enter a label ...", type="text", value=""),
        html.Br(),
        html.Br(),
        dcc.RadioItems(
            id="color",
            options=[
                {"label": "Red", "value": "#ff0000"},
                {"label": "Green", "value": "#00ff00"},
                {"label": "Blue", "value": "#0000ff"},
            ],
            value="Red",
        ),
    ]
)


@app.callback(Output("net", "data"), [Input("label", "value")])
def myfun(x):

    G = nx.Graph(prompt="prompt1")
    G.add_nodes_from([(1, {"id": 1, "label": "wowoza", "color": "#ff0000"})])
    print(G.nodes(data=True))

    # data ={'nodes':[{'id': 1, 'label':    x    , 'color':'#00ffff'},
    #                 {'id': 2, 'label': 'Node 2'},
    #                 {'id': 4, 'label': 'Node 4'},
    #                 {'id': 5, 'label': 'Node 5'},
    #                 {'id': 6, 'label': 'Node 6'}                    ],
    #        'edges':[{'id':'1-3', 'from': 1, 'to': 3},
    #                 {'id':'1-2', 'from': 1, 'to': 2} ]
    #        }
    # return data


@app.callback(Output("net", "options"), [Input("color", "value")])
def myfun(x):
    return {"nodes": {"color": x}}


if __name__ == "__main__":
    app.run_server()
