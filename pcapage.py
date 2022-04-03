import streamlit as st
import json
import os
import pandas as pd
import plotly.express as px
from sklearn.decomposition import PCA

def pca_page():
    st.title("PCA")

    st.write("Data has already been preprocessed to speedup loading. If you are interested in the code, you can find it in my git repo.")

    fp = open(os.path.join(os.curdir, "data", "pca", "pca_data.json"), "r")

    data = json.load(fp)


    df = pd.DataFrame(data).T

    with st.expander("See the data"):
        st.table(df)

    st.subheader("Original dimensions, before PCA")

    features = ["ABAB","ABAC","ABCB","ABCA","ABCD"]

    fig = px.scatter_matrix(
        df,
        dimensions=features,
        color=df.index
    )
    fig.update_traces(diagonal_visible=True)
    st.plotly_chart(fig)

    st.subheader("Principal components")


    pca = PCA()
    components = pca.fit_transform(df)
    labels = {
        str(i): f"PC {i + 1} ({var:.1f}%)"
        for i, var in enumerate(pca.explained_variance_ratio_ * 100)
    }

    fig = px.scatter_matrix(
        components,
        labels=labels,
        dimensions=range(4),
        color=df.index
    )
    fig.update_traces()
    st.plotly_chart(fig)

    st.subheader("First 2 principal components")

    pca = PCA(n_components=2)
    components = pca.fit_transform(df)

    fig = px.scatter(components, x=0, y=1, color=df.index, text=df.index)
    fig.update_traces(textposition='bottom center', showlegend=False, textfont_size=9)
    fig.update_traces(marker=dict(size=12,
                                  line=dict(width=2,
                                            color='DarkSlateGrey')),
                      selector=dict(mode='markers'),
                      )
    st.plotly_chart(fig, use_container_width=True)

