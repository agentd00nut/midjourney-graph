from dash import Dash, html, callback_context

##
variance_lc = -1
upsample_lc = -1
reroll_lc = -1
make_variations_lc = -1

from src.discord import DiscordLink


def runJob(
    graph, selections, value, variance, upsample, reroll, make_variations, jobStatus
):

    global variance_lc, upsample_lc, reroll_lc, make_variations_lc

    if len(selections["nodes"]) == 0:
        return jobStatus
    # https://dash.plotly.com/dash-html-components/button
    print(callback_context.triggered)
    changed_id: str = [p["prop_id"] for p in callback_context.triggered][0]
    jobType = ""
    if changed_id.startswith("variance"):
        jobType = "MJ::JOB::variation::" + str(value)
        if variance_lc == variance:
            return jobStatus
        variance_lc = variance
    elif changed_id.startswith("upsample"):
        jobType = "MJ::JOB::upsample::" + str(value)
        if upsample_lc == upsample:
            return jobStatus
        upsample_lc = upsample
    elif changed_id.startswith("reroll"):
        jobType = "MJ::JOB::reroll::0::SOLO"
        if reroll_lc == reroll:
            return jobStatus
        reroll_lc = reroll
    elif changed_id.startswith("make_variations"):
        jobType = "MJ::JOB::variation::1::SOLO"
        if make_variations_lc == make_variations:
            return jobStatus
        make_variations_lc = make_variations
    else:
        return jobStatus

    node = graph.nodes[selections["nodes"][0]]
    print("jobType", jobType, " For node id", node["id"])

    DL = DiscordLink()

    result = DL.runJob(node["node"], jobType)
    if not result:
        # TODO:: The reason some (most) jobs fail is the new limited roles in the discord... We could try and detect this and present an option to just roll the full command of the job to "own" it... maybe also optionally using the image as an input.
        #       Technically i think we could /show the job into one of our available threads or the DM with the bot, but that starts moving into the spoofed web socket territory again....
        return html.Div(
            [
                html.P(
                    f"Failed to run {jobType} for {node['id']}... reason: {result.text}... repeated failures mean you should probably stop"
                )
            ]
        )

    # # TODO: Until the placeholders show up right away and get removed when the job comes in, they are just annoying.
    # # TODO: Reference image num will be wrong for upsample placeholder jobs
    # placeholder = Node(jobType+node.id, "im a placeholder", node.id, value, node.prompt, jobType, "", node.shape,  False, False, None )
    # graph.addNode(placeholder)
    # graph.addEdge(placeholder.referenceEdge())
    # netData = graph.getVisDCCData()

    return html.Div([html.P(f"Started {jobType} for {node['id']}")])
