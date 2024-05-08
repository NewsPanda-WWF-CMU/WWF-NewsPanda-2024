import pandas as pd
import openai
import json
import numpy as np
from tqdm import tqdm

openai.api_key = '<OPEN_AI_KEY>'

# Read add the file for all articles
df1 = pd.read_csv('')



# Concatenate the three dataframes into one
combined_df = pd.concat([df1], ignore_index=True)
combined_df.drop_duplicates(subset=['url'])
# Convert 'publishedAt' to datetime if it's not already in that format

combined_df['publishedAt'] = pd.to_datetime(combined_df['publishedAt'], errors='coerce', utc=True)

# Sort the DataFrame by 'publishedAt'
sorted_df = combined_df.sort_values(by='publishedAt', ascending=False)

# Save the sorted DataFrame back to the same file
sorted_df.to_csv('combined-indiaapr9.csv', index=False)

# Assuming 'combined_df' is your DataFrame after initial loading and preprocessing
combined_df = pd.read_csv('combined-indiaapr9.csv')

combined_df['combined_terms'] = combined_df.apply(lambda row: set((str(row['Keywords']) + ',' + str(row['Category-Tags'])).lower().split(',')), axis=1)

# Remove extra spaces and filter empty strings
combined_df['combined_terms'] = combined_df['combined_terms'].apply(lambda x: set(item.strip() for item in x if item.strip()))
def has_minimum_common_terms(set1, set2, min_common_terms=6):
    intersection = len(set1.intersection(set2))
    return intersection >= min_common_terms

def calculate_overlap_percentage(set1, set2):
    if not set1 or not set2:
        return 0
    intersection = len(set1.intersection(set2))
    smallest_set_length = min(len(set1), len(set2))
    return (intersection / smallest_set_length) * 100

# Function to group articles into events based on overlapping combined terms
def group_articles_into_events(df):
    events = []
    for i, row in tqdm(df.iterrows(), total=df.shape[0]):
        article_terms = row['combined_terms']
        matched_event = None

        for event in events:
            event_terms = event['combined_terms']
    
            overlap_percentage = calculate_overlap_percentage(article_terms, event_terms)
            # Check if there is very significant overlap
            if overlap_percentage > 95:                
                matched_event = event
                break
                

        if matched_event:
            matched_event['article_urls'].append(row['url'])
            matched_event['article_titles'].append(row['title'])
            matched_event['combined_terms'].update(article_terms)
        else:
            # Create a new event
            events.append({
                'article_urls': [row['url']],
                'article_titles': [row['title']],
                'combined_terms': article_terms,
            })

    return events

# Group articles into events
events = group_articles_into_events(combined_df)

# Filter events to include only those with more than one URL
filtered_events = [event for event in events if len(event['article_urls']) > 1 and len(event['article_urls']) < 5] 

# Convert filtered events to DataFrame for easier manipulation and saving
filtered_events_df = pd.DataFrame([{
    'article_urls': ",".join(event['article_urls']),
    'article_titles': ",".join(event['article_titles']),
    'combined_terms': ",".join(event['combined_terms']),
} for event in filtered_events])
# Save the DataFrame of filtered events
filtered_events_df.to_csv('filtered_grouped_articles_eventsapr9.csv', index=False)






def clean_json_string(json_string):
    # Remove Markdown code block markers
    json_string = json_string.replace("```json", "").replace("```", "")
    # Strip leading and trailing whitespace
    json_string = json_string.strip()
    return json_string

def clean_json_string_url(json_string):
    # Remove Markdown code block markers
    json_string = json_string.replace("```json", "").replace("```", "").replace("'", '"')
    # Strip leading and trailing whitespace
    json_string = json_string.strip()
    return json_string


def getEventSummary(articles):
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {
            "role": "user",
            "content": f"""Try to find different information in each article and list out the information that is different between
              the sets of articles, below the analysis. Analyze the content of these multiple articles that talk 
              about the same thing and give an objective summary of unique important information from the article in 
              terms of key value pairs of information. List each article source along with the unique information it provides about the incident.              
              Try to get as much combined information as possible and focus specifically on information available in one article but 
              not in others and list only ONE source URL as the source: \n {articles}"""
        }
    ]
    try:

        response = openai.ChatCompletion.create(
            model="gpt-4-0125-preview",
            messages=messages
        )

        assistant_response = response['choices'][0]['message']['content']
        return assistant_response
    except:
        return """"""

def generate_event_analysis_prompt(articles):
    prompt = """
        Based on the following articles, provide an event summary and detailed event details in JSON format. 
        The JSON should have two keys: "summary" for a general overview, and "details" containing a dictionary 
        with keys for each source and their corresponding details. 
        Here is the structure I expect and please make sure EVERY RESPONSE IS IN THE SAME OR SIMILAR JSON FORMAT:
        
        {
          "title": "a one line title of the event",
          "category": Only Should be Human Wildlife Conflict or Illegal Wildlife Trade,
          "summary": "A short summary of the event...",
          "actions": [<List of actions that can be taken by WWF Agents or concerned citizens (only 1 or 2 top actions)>]
          "details": {
            "Source Name": {
              "URL": "article URL",
              "<Detail Name>": "<detail 1 value>",
              "<Detail 2 Name>": "<detail 2 value>",
              ...
            },
            ...
          }
        }
        
        Below are the articles:
    """
    for article in articles:
        prompt += f"Source URL: {article['url']}\nContent: {article['content']}\n\n"
    return prompt.strip()

def getEventDetails(articles):
    messages = [
        {"role": "system", "content": "You are a helpful assistant that returns completely JSON Decodable responses and only that."},
        {
            "role": "user",
            "content": f"""{generate_event_analysis_prompt(articles)}. Ensure JSON FORMATTABILITY"""
        }
    ]
    try:

        response = openai.ChatCompletion.create(
            model="gpt-4-0125-preview",
            messages=messages
        )

        assistant_response = response['choices'][0]['message']['content']
        return assistant_response
    except:
        return """"""

# filtered_data = [event for event in processed_data if len(event.get('urls', [])) > 1]

filtered_events_df.to_csv('events-extractedapr9.csv')

events_extracted = pd.read_csv('events-extractedapr9.csv')





def get_event_text(urls, df):
    event_texts = []
    for url in urls:
        # Filter the dataframe for the specific URL
        event_data = df[df['url'] == url]
        # Extract the required information if available
        for _, row in event_data.iterrows():
            event_text = {
                "url": row['url'],
                "title": row['title'],
                "content": row['content']
            }
            event_texts.append(event_text)
    return event_texts


    

# Container for processed event summaries and details
processed_events = []
for index, event in tqdm(events_extracted.iterrows(), total=events_extracted.shape[0]):
    # Filter articles for the current event
    articles = event['article_urls'].split(',')
    
    # Load content for each article
    event_text = get_event_text(articles, combined_df)
    
    # Generate analysis for the event
    event_details = json.loads(clean_json_string(getEventDetails(event_text)))
    print(event_details)
    # Save processed information
    processed_events.append({
        'Event Urls': articles,
        'Event Summary': event_details['summary'],
        'Event Details': event_details['details'],
        'Event Actions': event_details['actions'],
        'Event Title': event_details['title'],
        'Event Category': event_details['category'],

    })

import csv

def save_articles_to_csv(articles, filename):
    # Collect all unique keys from all articles
    keys = set(key for article in articles for key in article.keys())

    with open(filename, 'w', newline='', encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(articles)


# # Save to CSV or another format as needed
save_articles_to_csv(processed_events, '../src/data/processed_event_summaries_at_scale.csv')