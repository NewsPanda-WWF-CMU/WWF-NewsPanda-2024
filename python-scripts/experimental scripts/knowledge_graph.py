import spacy
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from itertools import combinations
from collections import Counter

# Load Spacy NLP Model
nlp = spacy.load("en_core_web_sm")

# Load your data
df = pd.read_csv('mongabay_articles.csv')

# Function to extract entities from a text
def extract_entities(text):
    doc = nlp(text)
    return [ent for ent in doc.ents if ent.label_ in {'ORG', 'GPE'}]  # Focus on ORG and GPE entities

# Count entity occurrences
entity_counter = Counter()

# Process each article title and summary
for _, row in df.iterrows():
    text = f"{row['title']} {row['summary']}"
    text_entities = extract_entities(text)
    entity_counter.update([ent.text for ent in text_entities])

# Filter out entities based on frequency
min_occurrence = 2  # Minimum number of occurrences for an entity to be included
selected_entities = {ent for ent, count in entity_counter.items() if count >= min_occurrence}

# Create a graph
G = nx.Graph()

# Process each article title and summary
for _, row in df.iterrows():
    text = f"{row['title']} {row['summary']}"
    text_entities = extract_entities(text)

    # Add and connect entities from title and summary to graph
    for entity in text_entities:
        if entity.text in selected_entities:
            G.add_node(entity.text)

            # Create edges between all entities in the title and summary
            for entity1, entity2 in combinations(text_entities, 2):
                if entity1.text in selected_entities and entity2.text in selected_entities:
                    G.add_edge(entity1.text, entity2.text)

# Visualize the graph
plt.figure(figsize=(12, 12))
nx.draw_networkx(G, with_labels=True)
plt.show()
