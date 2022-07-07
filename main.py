
from dash import Dash, html, dcc, callback_context
from dash.dependencies import Input, Output
import visdcc
import requests
from dataclasses import asdict
from src.discord import DiscordLink
from src.job import  jobFromJson
from src.mj import getRecentJobsForUser
from src.node import nodeFromJob
from src.graph import Graph
app = Dash(__name__)

app.layout = html.Div([
    visdcc.Network(id='net',
                   selection={"nodes": [], "edges": []},
                   options=dict(height='400px', width='100%', layout={'clusterThreshold': 3, 'hierarchial': {'enabled': True, 'direction': 'UD'}})),
    html.Div(id='node_info'),

    html.Div(
        [
            dcc.Input(id='image_selection', min=1,
                      max=4, step=1, value=1, type='range'),
            html.Button('V<>', id='variance',
                        name='variance_button', value='variation'),
            html.Button('U<>', id='upsample',
                        name='upscale_button', value='upsample'),
            # for 2x2 images...
            html.Button('reroll', id='reroll',
                        name='reroll_button', value='reroll'),
            html.Button('Make Variations', id='make_variations', name='make_variations_button',
                        value='variation'),  # TODO:: Only show if the node is an upsampled image
            # TODO:: Button for "upscale to max" if availabe... Also need to determine how we might know if that's possible or not...
            html.Div(id='jobStatus'),
        ], id='jobInputs'
    ),

    html.Div(id='midjourneyInputs', children=[
        html.P(['userId',
                dcc.Input(id='userId',
                          placeholder='Enter a user Id ...',
                          type='text',
                          value=''),
                'numberOfJobs:',
                dcc.Input(id='numJobs',
                          placeholder='Enter a max number of jobs',
                          type='number',
                          name='numJobs',
                          min=1,
                          max=100,
                          debounce=True,
                          value=1),
                'jobsPerQuery:',
                dcc.Input(id='jobsPerQuery',
                          placeholder='Jobs per query',
                          type='number',
                          debounce=True,
                          min=1,
                          max=100,
                          value=5),
                'Start Page:',
                dcc.Input(id='page',
                          placeholder='Enter a page number to start on, 0 is first...',
                          type='number',
                          debounce=True,
                          min=0,
                          value=0),
                html.Button('Refresh_Graph', id='refresh_graph',name='refresh_graph_button')
                ]),

    ]),

    html.Div(id='nodes'),
    html.Div(id='edges'),

])



graph = Graph()


@app.callback(
    Output('nodes', 'children'),
    [Input('net', 'selection')])
def selection(selections):
    global graph

    if len(selections['nodes']) == 0:
        return html.Div([html.H4('No node selected')])

    node = graph.getNode(selections['nodes'][0])
    if node is None:
        return html.Div([html.H4('No node selected')])

    discord_link = node.gotoDiscord()

    DL = DiscordLink()
    div = html.Div(
        [
            html.Img(src=node.image, height='100%', style={'padding-top': '20px'}),
            html.A(html.H4("Goto discord"), href=discord_link,),

        ],
        style={'display': 'flex', 'flex-direction': 'column',
               'justify-content': 'center', 'align-items': 'center', 'height': '350px'}
    )

    return div


variance_lc = -1
upsample_lc = -1
reroll_lc = -1
make_variations_lc = -1


@app.callback(
    Output('jobStatus', 'children'),
    [
        Input('net', 'selection'),
        Input('image_selection', 'value'),
        Input('variance', 'n_clicks'),
        Input('upsample', 'n_clicks'),
        Input('reroll', 'n_clicks'),
        Input('make_variations', 'n_clicks'),
        Input('jobStatus', 'children')
    ])
def runJob(selections, value, variance, upsample, reroll, make_variations, jobStatus):
    global graph
    global variance_lc, upsample_lc, reroll_lc, make_variations_lc

    if len(selections['nodes']) == 0:
        return jobStatus
    # https://dash.plotly.com/dash-html-components/button
    changed_id: str = [p['prop_id'] for p in callback_context.triggered][0]
    jobType = ''
    if changed_id.startswith('variance'):
        jobType = 'MJ::JOB::variation::'+str(value)
        if variance_lc == variance:
            return jobStatus
        variance_lc = variance
    elif changed_id.startswith('upsample'):
        jobType = 'MJ::JOB::upsample::'+str(value)
        if upsample_lc == upsample:
            return jobStatus
        upsample_lc = upsample
    elif changed_id.startswith('reroll'):
        jobType = 'MJ::JOB::reroll::0::SOLO'
        if reroll_lc == reroll:
            return jobStatus
        reroll_lc = reroll
    elif changed_id.startswith('make_variations'):
        jobType = 'MJ::JOB::variation::1::SOLO'
        if make_variations_lc == make_variations:
            return jobStatus
        make_variations_lc = make_variations
    else:
        return jobStatus

    node = graph.getNode(selections['nodes'][0])
    print("jobType", jobType, " For node id", node.id)

    DL = DiscordLink()

    result = DL.runJob(node, int(value), jobType)
    if not result:
        result.raise_for_status()
    return html.Div([html.H1(f"Started V{value} for {node.id}")])



@app.callback(
    Output('edges', 'children'),
    [Input('net', 'selection')])
def selectedEdges(x):
    s = 'Selected edges : '
    if len(x['edges']) > 0:
        s = [s] + [html.Div(i) for i in x['edges']]
    return s


@app.callback(
    Output('net', 'data'),
    [Input('userId', 'value'), Input('numJobs', 'value'), Input('page', 'value'), Input('jobsPerQuery', 'value'), Input('refresh_graph', 'n_clicks')])
def mainFun(userId, numJobs, page, jobsPerQuery, refresh_graph):

    global graph
    # If we don't have a user id we just return an empty graph.
    if userId is None:
        return {'nodes': [], 'edges': []}

    page = int(page)
    numJobs = int(numJobs)
    # Get the recent jobs for the user
    recent_jobs = []
    while len(recent_jobs) < int(numJobs):
        result = getRecentJobsForUser(userId, jobsPerQuery, page)
        if result is None or result.status_code != 200:
            print("we got bonked by midjourney api")
            print(result.reason)
            result.raise_for_status()
            continue
        recent_jobs.extend(result.json())
        print(len(recent_jobs), page)
        page += 1

    # Create a list of nodes from the recent jobs
    nodes = [nodeFromJob(jobFromJson(j)) for j in recent_jobs]
    print("Got", len(nodes), "nodes")

    # Add the nodes to the graph
    print("Adding the first round of nodes, not iterating down references")
    for n in nodes:
        graph.addNode(n)

    # Iterate on the nodes, trying to add references for each node
    #       We do this to avoid having to download the data for each node / having to check our held nodes for every reference
    print("")
    print("")
    print("")
    print("Now checking their references")
    for n in nodes:
        graph.addNodesReferences(n)

    print("done")

    # Return the graph as a json object compatible for the visdcc.Network
    data = {'nodes': [asdict(graph.nodes[n]) for n in graph.nodes], 'edges': [
        graph.edges[e].asGraphEdge() for e in graph.edges]}

    return data


if __name__ == '__main__':
    app.run_server(debug=True, dev_tools_hot_reload=False)