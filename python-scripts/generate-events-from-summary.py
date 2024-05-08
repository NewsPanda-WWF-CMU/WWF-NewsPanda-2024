import pandas as pd
import re
import openai
import json
import numpy as np
from tqdm import tqdm

openai.api_key = '<OPEN_AI_KEY>'

# Read the CSV File that contains all news articles
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
infrastructure_df = sorted_df[sorted_df['gpt-relevance_to_infra'] > 0.5]
wildlife_trade_df = sorted_df[sorted_df['relevance_to_illegal_wildlife_trade'] > 0.5]
human_conflict_df = sorted_df[sorted_df['relevance_to_human_wildlife_conflict'] > 0.5]
df_parts = [infrastructure_df, wildlife_trade_df, human_conflict_df]


# Concatenate all the summaries into a single string


# Count the number of words

example_json =[{'event_name': 'Tiger kills 5 people in Nepal Zoo', 'urls': ['https://news.mongabay.com/2024/02/un-award-for-nepals-tiger-range-restoration-spurs-euphoria-amid-challenges/', 'https://thehimalayantimes.com/nepal/reforestation-initiative-that-helped-triple-nepals-tiger-population-recognized-as-one-of-seven-un-world-restoration-flagships'], 'summary': "Nepal's Terai Arc Landscape initiative, praised for significantly increasing tiger populations and restoring 66,800 hectares of forest, earns UN recognition as one of the seven UN World Restoration Flagships as part of the UN Decade on Ecosystem Restoration.", 'event_type': 'Human Wildlife Conflict'}]


def getSummariestoEvents(summaries):
    messages = [
        {"role": "system", "content": "You are a knowledgeable assistant with expertise in analyzing news articles on conservation that returns JSON Formattable responses."},
        {
            "role": "user",
            "content":f"""{summaries} \n \n 
                Given the summaries and Keywords with entities of various news articles, identify specific events where multiple articles
                are discussing the same conservation-related incident or news. Here is an example of the format - 
                {example_json}
                It should contain the event name, the URLs of articles that cover this event, and a brief summary that encapsulates the key points discussed across these articles. 
                The event Categories should only be 3 types - [Illegal Wildlife Trade, Human Wildlife Conflict or Infrastructure Events]. 
                Your analysis should help in creating a database of conservation events with precise information and format must be IN EXACT JSON as shown in the example and it should be clearly json parsable THIS IS NON NEGOTIABLE. Also make sure Each event extracted has a very specific title for an event. if there are no events - return an empty array It has to be a specific event not some general category. Also each event must have atleast 1 url to be classified as an event
                """
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
    
with open('titles_summaries_urls.txt', 'w', encoding='utf-8') as file:
    for title, summary, url in zip(combined_df['title'], combined_df['description'], combined_df['url']):
        file.write(f"Title: {title}\nSummary: {summary}\nURL: {url}\n\n")


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
        with keys for each source (e.g., "Setopati", "Online Khabar") and their corresponding details. 
        Here is the structure I expect and please msake sure EVERY RESPONSE IS IN THE SAME OR SIMILAR JSON FORMAT:
        
        {
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
        print(assistant_response)
        return assistant_response
    except:
        return """"""


final_events = []
for df_part in df_parts:
    summaries_and_urls = '\n'.join(f"Title: {title}\n \nURL: {url} \n Summary {summary} \n Keywords: {keywords}, {categories}" for title, url, summary, keywords, categories in zip(df_part['title'], df_part['url'], df_part['description'], df_part['Keywords'], df_part['Category-Tags']))
    word_count = len(re.findall(r'\w+', summaries_and_urls))
    print("Total number of words in all summaries:", word_count)

    testEvents = getSummariestoEvents(summaries_and_urls)
    print(testEvents)
    processed_data = json.loads(clean_json_string(testEvents))
    print(processed_data)
    final_events.extend(processed_data)
print(final_events)
final_events_df = pd.DataFrame(final_events)
# filtered_data = [event for event in processed_data if len(event.get('urls', [])) > 1]

final_events_df.to_csv('events-extractedapr9.csv')

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
    articles = json.loads(clean_json_string_url(event['urls']))
    
    # Load content for each article
    event_text = get_event_text(articles, combined_df)
    
    # Generate analysis for the event
    event_details = json.loads(clean_json_string(getEventDetails(event_text)))
    
    # Save processed information
    processed_events.append({
        'Event Urls': event['urls'],
        'Event Name': event['event_name'],
        'Event Type': event['event_type'],
        'Event Summary': event_details['summary'],
        'Event Details': event_details['details'],
        'Event Actions': event_details['actions']
    })

# # Convert processed events into a DataFrame (optional, for saving or further processing)
processed_events_df = pd.DataFrame(processed_events)

# # Save to CSV or another format as needed
processed_events_df.to_csv('../src/data/processed_event_summaries_from_summary.csv', index=False)