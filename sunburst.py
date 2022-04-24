import streamlit as st
import os
import json
import plotly.express as px
def sunburst():
    """
    Streamlit wrapper
    """

    st.title("Sunburst diagrams")

    st.success("Developed by Francesco Deaglio and Filippo Costa")
    st.write("""
    The idea of this diagram is to see how the various passage networks evolve. For example, an AB network can continue by becoming ABA, ABC or by changing possession (lost ball, shot, end of game...).

In order to represent this, we have used the sunburst diagram. To speed up the GUI we have pre-calculated the values for all teams, while if you are only interested in your match you can edit the notebook on github.

Two graphs are shown, which I think are fairly important. The first one matches patterns at any point in the action. The second one is a subset of the first one, where player A is the one who starts the action.
    
The graphs are interactive. For example, if you click on ABA, it shows you the graph with ABA as the starting pattern (thus removing its "brothers" ABC and AB-lost).
    """)

    fp = open(os.path.join(os.curdir, "data", "sunburst",  "sunburst_unconstrained.json"), "r")

    data = json.load(fp)
    fp = open(os.path.join(os.curdir, "data", "sunburst", "sunburst_beginning.json"), "r")

    databeg = json.load(fp)
    team = st.selectbox("Select the team", data.keys())

    st.subheader("Unconstrained")
    patterns = []
    prefixes = []
    values = []

    for res in data[team]:
        patterns.append(res)
        prefixes.append(res[:-1])
        values.append(data[team][res])

    prefixes[0] = ""

    fig = px.sunburst(
                      names=patterns,
                      parents=prefixes,
                      values=values,
                      color=prefixes
                      )
    st.plotly_chart(fig)
    st.subheader("Player 'A' first in the possession")
    patternsb = []
    prefixesb = []
    valuesb = []

    for res in databeg[team]:
        patternsb.append(res)
        prefixesb.append(res[:-1])
        valuesb.append(databeg[team][res])

    prefixesb[0] = ""

    figb = px.sunburst(
        names=patternsb,
        parents=prefixesb,
        values=valuesb,
        color=prefixesb
    )
    st.plotly_chart(figb, use_container_width=True)
