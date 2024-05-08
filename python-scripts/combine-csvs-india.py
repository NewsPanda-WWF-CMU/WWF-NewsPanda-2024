import pandas as pd

# Load the datasets
df1 = pd.read_csv('../src/data/weekly-india-articles.csv')


# Concatenate the three dataframes into one
combined_df = pd.concat([df1], ignore_index=True)
combined_df.drop_duplicates(subset=['url'])

# Renaming and mapping columns for mongabay_articles
combined_df.rename(columns={
    'flora_and_fauna': 'Flora_and_Fauna',
    'tags': 'Keywords',
    'location': 'Location',
    'landscape': 'Landscape-Location',
    'named_entities': 'Entities',
    'categories': 'Category-Tags',
    'relevance_to_infrastructure': 'gpt-relevance_to_infra',
    'relevance_to_conservation': 'gpt-relevance_to_conservation',
    'date': 'publishedAt',
    'summary': 'description',
    'content': 'content',
    'author': 'author'
}, inplace=True)

combined_df['query'] = 'India Conservation'


combined_df.drop(columns=['processed_info'], inplace=True)


# Combine the two dataframes
combined_df = pd.concat([combined_df], ignore_index=True)

def remove_brackets_from_column(df, column):
    df[column] = df[column].astype(str).str.replace(r"[\[\]'']", "", regex=True)
    return df

# Columns to process
columns_to_process = ['Keywords', 'Category-Tags', 'Flora_and_Fauna']

# Process each column
for column in columns_to_process:
    combined_df = remove_brackets_from_column(combined_df, column)

# Save the combined dataframe to a new CSV
combined_csv_path = '../src/data/current-india-articles.csv'
combined_df.to_csv(combined_csv_path, index=False)
print(len(combined_df))
combined_df = pd.concat([combined_df], ignore_index=True)
combined_df.drop_duplicates(subset=['url'])
# Convert 'publishedAt' to datetime if it's not already in that format

combined_df['publishedAt'] = pd.to_datetime(combined_df['publishedAt'], errors='coerce', utc=True, format='mixed')

# Sort the DataFrame by 'publishedAt'
sorted_df = combined_df.sort_values(by='publishedAt', ascending=False)

# Save the sorted DataFrame back to the same file
sorted_df.to_csv('../src/data/current-india-articles.csv', index=False)
