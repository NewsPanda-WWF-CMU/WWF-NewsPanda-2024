import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sentence_transformers import SentenceTransformer
import umap
import plotly.express as px
from hdbscan import HDBSCAN
import openai
import json

openai.api_key = '<OPEN_AI_KEY>'


def process_clusters_to_meaningful_titles(cluster_map):
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {
            "role": "user",
            "content": f"{cluster_map} Process these titles and return meaningful cluster names in less than 5-10 words for these clusters. Make sure you return exactly the same object as passed in the same format WHICH IS JSON LOADABLE IN PYTHON where the index is the key and the final cluster name is the value and ONLY that."
        }
    ]

    response = openai.ChatCompletion.create(
        model="gpt-4-0125-preview",
        messages=messages
    )

    assistant_response = response['choices'][0]['message']['content']
    return assistant_response

# Load data
df = pd.read_csv('mongabay_articles.csv')

# Fill missing content with empty string
df['content'] = df['summary'].fillna('')

# Compute sentence embeddings
model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = model.encode(df['content'].tolist(), show_progress_bar=True)

# UMAP for dimensionality reduction
umap_model = umap.UMAP(n_neighbors=30, min_dist=0.1, n_components=3, metric='cosine')
umap_embeddings = umap_model.fit_transform(embeddings)

# Clustering with HDBSCAN
clusterer = HDBSCAN(min_cluster_size=3, gen_min_span_tree=True)
clusters = clusterer.fit_predict(umap_embeddings)

# Create DataFrame for plotting
plot_df = pd.DataFrame(umap_embeddings, columns=['UMAP1', 'UMAP2', 'UMAP3'])
plot_df['Cluster'] = clusters
plot_df['Title'] = df['title']

# Create a dictionary to map cluster indices to article titles
cluster_to_titles = {}
for cluster_idx, title in zip(plot_df['Cluster'], plot_df['Title']):
    if cluster_idx not in cluster_to_titles:
        cluster_to_titles[cluster_idx] = []
    cluster_to_titles[cluster_idx].append(title)

def clean_json_string(json_string):
    # Remove Markdown code block markers
    json_string = json_string.replace("```json", "").replace("```", "")
    # Strip leading and trailing whitespace
    json_string = json_string.strip()
    return json_string

clustered_headings = json.loads(clean_json_string(process_clusters_to_meaningful_titles(cluster_to_titles)))

# Map cluster indices to GPT-4's cluster names
cluster_name_map = {int(k): v for k, v in clustered_headings.items()}
plot_df['Cluster Name'] = plot_df['Cluster'].map(cluster_name_map)

# Visualization with cluster names
fig = px.scatter_3d(plot_df, x='UMAP1', y='UMAP2', z='UMAP3', color='Cluster Name', hover_data=['Title'])
fig.update_layout(title='Article Clusters with UMAP and HDBSCAN', scene=dict(xaxis_title='UMAP Dimension 1', yaxis_title='UMAP Dimension 2', zaxis_title='UMAP Dimension 3'))
fig.show()

