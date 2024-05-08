import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from geopy.geocoders import Nominatim
from shapely.ops import nearest_points
# Load the datasets
df1 = pd.read_csv('../src/data/weekly-nepal-articles.csv')





# Concatenate the three dataframes into one
combined_df = pd.concat([df1])
combined_df.drop_duplicates(subset=['url'])


df_test = pd.read_csv('../src/data/current-nepal-articles.csv')

print(len(df_test))
# Renaming and mapping columns for mongabay_articles
combined_df.rename(columns={
    'flora_and_fauna': 'Flora_and_Fauna',
    'tags': 'Keywords',
    'location': 'Location',
    # 'landscape': 'Landscape-Location',
    'categories': 'Category-Tags',
    'relevance_to_infrastructure': 'gpt-relevance_to_infra',
    'relevance_to_conservation': 'gpt-relevance_to_conservation',
    'date': 'publishedAt',
    'summary': 'description',
    'content': 'content',
    'author': 'author'
}, inplace=True)

combined_df['query'] = 'Nepal Conservation'


combined_df.drop(columns=['processed_info'], inplace=True)

# Adding missing columns from test-last-year-nepal-cleaned to mongabay_articles
for col in df_test.columns:
    if col not in combined_df.columns:
        combined_df[col] = 'N/A'

# Adding missing columns from mongabay_articles to test-last-year-nepal-cleaned
for col in combined_df.columns:
    if col not in df_test.columns:
        df_test[col] = 'N/A'

# Combine the two dataframes
# combined_df.reset_index(inplace=True)
# df_test.reset_index(inplace=True)
print(len(combined_df.columns) == len(set(combined_df.columns)))
print(combined_df.columns)
df_test = df_test.loc[~df_test.index.duplicated(keep='first')]
combined_df = combined_df.loc[~combined_df.index.duplicated(keep='first')]


combined_df = pd.concat([combined_df, df_test], ignore_index=True)

def remove_brackets_from_column(df, column):
    df[column] = df[column].astype(str).str.replace(r"[\[\]'']", "", regex=True)
    return df

# Columns to process
columns_to_process = ['Keywords', 'Category-Tags', 'Flora_and_Fauna']

# Process each column
for column in columns_to_process:
    combined_df = remove_brackets_from_column(combined_df, column)

# Save the combined dataframe to a new CSV
combined_csv_path = '../src/data/current-nepal-articles.csv'
combined_df.to_csv(combined_csv_path, index=False)
print(len(combined_df))
combined_df = pd.concat([combined_df], ignore_index=True)
combined_df = combined_df.drop_duplicates(subset=['url'])
# Convert 'publishedAt' to datetime if it's not already in that format

combined_df['publishedAt'] = pd.to_datetime(combined_df['publishedAt'],format='mixed', utc=True)
print(combined_df['publishedAt'])
# Sort the DataFrame by 'publishedAt'
sorted_df = combined_df.sort_values(by='publishedAt', ascending=False)

shapefile_landscape_map = {
    'CHAL/chalb.shp': 'Chitwan Annapurna Landscape',
    'Kailesh/kailashb.shp': 'Kailash Sacred Landscape',
    'TAL/talb_dd.shp': 'Terai Arc Landscape',
    'KL/kclb.shp': 'Kanchenjunga Landscape',
    'SHL/shlb.shp': 'Sacred Himalayan Landscape'
}
def is_point_in_shapefile(point, shapefile_path):
    gdf = gpd.read_file('shapefile/'+shapefile_path)
    return any(point.within(shape) for shape in gdf['geometry'])

def get_nearest_distance_to_shapefile(point, shapefile_path):
    gdf = gpd.read_file('shapefile/'+shapefile_path)
    min_distance = float('inf')
    for shape in gdf['geometry']:
        nearest_pt = nearest_points(point, shape)[1]
        distance = point.distance(nearest_pt)
        min_distance = min(min_distance, distance)
    return min_distance

def find_closest_landscape(point, shapefile_map, max_distance=0.1):
    closest_landscape = 'Other'
    closest_distance = float('inf')
    for shapefile, landscape_name in shapefile_map.items():
        distance = get_nearest_distance_to_shapefile(point, shapefile)
        if distance < closest_distance:
            closest_distance = distance
            closest_landscape = landscape_name
    return closest_landscape if closest_distance <= max_distance else 'Other'


def process_dataframe(df, shapefile_landscape_map):
    # Sorting the map to prioritize 'Terai Arc Landscape'
    prioritized_items = [(k, v) for k, v in shapefile_landscape_map.items() if v == 'Terai Arc Landscape']
    other_items = [(k, v) for k, v in shapefile_landscape_map.items() if v != 'Terai Arc Landscape']
    sorted_items = prioritized_items + other_items    
    for index, row in df.iterrows():
        lat, lon = row['latitude'], row['longitude']
        if pd.notna(lat) and pd.notna(lon):
            point = Point(lon, lat)
            landscape_found = False

            for shapefile, landscape_name in sorted_items:
                if is_point_in_shapefile(point, shapefile):
                    df.loc[index, 'Landscape-Location'] = landscape_name
                    df.loc[index, 'closest_landscape'] = landscape_name
                    landscape_found = True
                    break

            if not landscape_found:
                df.loc[index, 'Landscape-Location'] = 'Other'
                try:
                    df.loc[index, 'closest_landscape'] = find_closest_landscape(point, shapefile_landscape_map)
                except Exception as e:
                    print(f"Error finding closest landscape: {e}")
                    df.loc[index, 'closest_landscape'] = 'Other'
        else:
            df.loc[index, 'Landscape-Location'] = 'Other'
            df.loc[index, 'closest_landscape'] = 'Other'

    return df

sorted_df = process_dataframe(sorted_df, shapefile_landscape_map)
sorted_df = sorted_df.drop_duplicates(subset=['url'])

# Save the sorted DataFrame back to the same file
sorted_df.to_csv('../src/data/current-nepal-articles.csv', index=False)

