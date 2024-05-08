import openai
import pandas as pd
openai.api_key = '<OPEN_AI_KEY>'
import json
def get_article_analysis(article_content):
    prompt = f"""
    Analyze the following article and provide a JSON response that is directly parsable using json.loads in python with the specified fields:

    Article:
    {article_content}

    JSON Response:
    {{
        "relevance_to_infrastructure": (value between 0 and 1),
        "relevance_to_conservation": (value between 0 and 1),
        "Tags": Multiple of ["Wildlife", "Freshwater", "Climate and Energy", "Forests", "Governance", "Other"],
        "Location": One of the following - ["Terai Arc Landscape", "Sacred Himalayan Landscape", "Kailash Sacred Landscape", "Chitwan Annapurna Landscape", "Kanchenjunga Landscape", "Other(Nepal), "Other(World)"],
        "Flora and Fauna": Multiple from ["Asian Elephant (Elephas maximus)", "Bengal Tiger (Panthera tigris ssp. tigris)", "Greater One-horned Rhinoceros (Rhinoceros unicornis)", "Gharial (Gavialis gangeticus)", "Otter (Lutra lutra & Lutrogale perspicillata)", "Pangolin (Manis crassicaudata & Manis pentadactyla)", "Red Panda (Ailurus fulgens)", "South Asian River Dolphin (Platanista gangetica)", "Snow Leopard (Panthera uncia)", "Tree Fern (Cyathea spp.)", "Champ (Michelia champaca)", "Bijaysal (Pterocarpus marsupium)", "Rhododendron (Rhododendron spp.)", "Other"]
    }}
    """
    response = openai.ChatCompletion.create(
        model="gpt-4-1106-preview", 
        messages=[
        {"role": "system", "content": "You are a helpful assistant meant to give responses in verify specific format"},
        {"role": "user", "content": f"{prompt}"}],
        max_tokens=300  # Adjust as needed
    )
    return response.choices[0].message.content



file_path = 'test-last-year-nepal.csv'  # Replace with your actual file path
df = pd.read_csv(file_path)
def is_nepali(text):
    for char in text:
        if '\u0900' <= char <= '\u097F':  # Devanagari block for Nepali
            return True
    return False
filtered_df = pd.DataFrame()  # Create a new dataframe for filtered data

# Process each article in the DataFrame
for index, row in df.iterrows():
    try:
        # article_content = row['title'] + '\n' + row['content']  # Replace 'content' with your actual column name
        # json_response = get_article_analysis(article_content)
        
        # analysis = json.loads(json_response.replace('```', '').replace('json', ''))
        
        # Check if the article meets the relevance criteria
        if float(row.get('relevance_to_infra', 0)) < 0.2 and float(row.get('gpt-relevance_to_conservation', 0)) < 0.2:
            continue  # Skip this iteration if criteria are not met

        # # Add new data as columns
        # df.at[index, 'gpt-relevance_to_infra'] = analysis.get('relevance_to_infra', None)
        # df.at[index, 'gpt-relevance_to_conservation'] = analysis.get('relevance_to_conservation', None)
        # df.at[index, 'Category-Tags'] = ', '.join(analysis.get('Tags', []))
        # df.at[index, 'Landscape-Location'] = analysis.get('Location', None)
        # df.at[index, 'Flora_and_Fauna'] = ', '.join(analysis.get('Flora and Fauna', []))

        # Check language
        df.at[index, 'Language'] = 'Nepali' if is_nepali(row['title']) else 'English'

        # Append the filtered row to the new dataframe
        filtered_df = filtered_df.append(df.loc[index])

    except Exception as e:
        print(f"Error processing article at index {index}: {e}")

# Export the modified DataFrame to a new CSV file
output_file_path = 'test-last-year-nepal-cleaned.csv'  # Replace with your desired output path
filtered_df.to_csv(output_file_path, index=False)
