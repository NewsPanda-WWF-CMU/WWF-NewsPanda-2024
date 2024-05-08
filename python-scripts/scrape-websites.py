import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
import openai
import json
import csv
import geopandas as gpd
from shapely.geometry import Point
from geopy.geocoders import Nominatim
from shapely.ops import nearest_points
from tqdm import tqdm  # Import tqdm
import nepali_datetime
import urllib.parse
import pandas as pd


english_base_url_format = "https://english.onlinekhabar.com/?s={query}"
nepali_base_url_format = "https://www.onlinekhabar.com/?search_keyword={query}"
def generate_search_urls(keywords, base_url_format):
    return [base_url_format.format(query=urllib.parse.quote(keyword)) for keyword in keywords]


openai.api_key = '<OPEN_AI_KEY>'

infrastructure_impact_keywords = [
    "road construction wildlife",
    "deforestation development",
    "urban expansion habitat",
    "mining ecosystems",
    "dam rivers",
    "oil gas conservation",
    "renewable energy biodiversity",
    "industrial pollution",
    "agricultural expansion species",
    "water projects ecology",
    "infrastructure protected areas",
    "transport corridors migration",
    "energy lines birds",
    "conservation infrastructure",
]

human_wildlife_conflict_keywords = [
    'wildlife'
    "human wildlife conflict",
    "animal attack",
    "wildlife encroachment",
    "wildlife conservation conflict"
    'conservation'
]

illegal_wildlife_trade_keywords = [
    "illegal wildlife trade",
    "poaching",
    "wildlife trafficking",
    "endangered species trade"
]

def find_closest_landscape(point, shapefile_map, max_distance=0.1):
    closest_landscape = 'Other'
    closest_distance = float('inf')
    for shapefile, landscape_name in shapefile_map.items():
        distance = get_nearest_distance_to_shapefile(point, shapefile)
        if distance < closest_distance:
            closest_distance = distance
            closest_landscape = landscape_name
    return closest_landscape if closest_distance <= max_distance else 'Other'


def get_nearest_distance_to_shapefile(point, shapefile_path):
    gdf = gpd.read_file('shapefile/'+shapefile_path)
    min_distance = float('inf')
    for shape in gdf['geometry']:
        nearest_pt = nearest_points(point, shape)[1]
        distance = point.distance(nearest_pt)
        min_distance = min(min_distance, distance)
    return min_distance

def get_coordinates(location):
    geolocator = Nominatim(user_agent="wwf-nepal")
    location = geolocator.geocode(location)
    return (location.latitude, location.longitude) if location else (None, None)

def is_point_in_shapefile(point, shapefile_path):
    gdf = gpd.read_file('shapefile/'+shapefile_path)
    return any(point.within(shape) for shape in gdf['geometry'])

GPT4Prompt = """
Given the following article content, analyze and extract the required information in the specified format. Identify relevant tags from the list: [Fishing, Restoration, Marine Habitat, NGO, Species Loss, Freshwater Habitat, Pollution, Governance, Social Conflict, Shipping, Extractives - Oil and Gas, Habitat Loss, Atmosphere, Invasive Species, Social, Climate Change, Tourism, Illegal Wildlife Trade, Agriculture, Terrestrial Habitat, Extractives - Mining]. Determine the categories as one or more from: ["Wildlife", "Freshwater", "Climate and Energy", "Forests", "Governance", "Infrastructure"]. Also, identify the relevance to infrastructure and conservation on a scale of 0 to 1, the landscape from the options ["Terai Arc Landscape", "Sacred Himalayan Landscape", "Kailash Sacred Landscape", "Chitwan Annapurna Landscape", "Kanchenjunga Landscape", "Other(Nepal)", "Other(World)"], and possible flora and fauna impacted in a list with their scientific names. Lastly, provide a general location of the events in the article.
Flora Fauna List - one or more from ["Asian Elephant (Elephas maximus)", "Bengal Tiger (Panthera tigris ssp. tigris)", "Greater One-horned Rhinoceros (Rhinoceros unicornis)", "Gharial (Gavialis gangeticus)", "Otter (Lutra lutra & Lutrogale perspicillata)", "Pangolin (Manis crassicaudata & Manis pentadactyla)", "Red Panda (Ailurus fulgens)", "South Asian River Dolphin (Platanista gangetica)", "Snow Leopard (Panthera uncia)", "Tree Fern (Cyathea spp.)", "Champ (Michelia champaca)", "Bijaysal (Pterocarpus marsupium)", "Rhododendron (Rhododendron spp.)", "Other"]
Please provide the structured data as follows that can be JSON Decoded (THIS IS VERY IMPORTANT):
{
    "relevance_to_infrastructure": [Value between 0 and 1],
    "relevance_to_conservation": [Value between 0 and 1],
    "location": "Preferably as specific a location where the events of the article are located specific to city. If not able to give this just list World",
    "flora_and_fauna": ["List of flora and fauna mentioned or impacted, from the given options"],
    "categories": ["List of categories relevant to the article from the given options of categories above"],
    "tags": ["List of tags relevant to the article from the given options of tags above"]
    "summary:" <A not more than 3 lines summary of the article>
    "named_entities" ["A list of any and all important named entities and organizations linked to this article"],
    "infrastructure-subtype": 'If relevance to infrastructure is high, this should be set to the type of subtype of events in infrastructure else None'
}
"""
def get_mongabay_article_content(url):
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        article_content = soup.find('article')
        if article_content:
            # Extracting text from multiple tag types
            text_elements = article_content.find_all(['p', 'h1', 'h2', 'h3', 'ul', 'ol', 'blockquote'])
            return ' '.join([element.get_text(strip=True) for element in text_elements])
    return ""

def get_setopati_article_content(url):
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Assuming the main content resides within a specific structure based on the given HTML
        content_area = soup.find('aside', class_='left-side')
        
        if content_area:
            # Extracting text from multiple tag types within the specified content area
            text_elements = content_area.find_all(['p', 'h1', 'h2', 'h3', 'ul', 'ol', 'blockquote'], style="text-align: justify;")
            # Concatenating all text elements found
            content = ' '.join(element.get_text(strip=True) for element in text_elements if element.get_text(strip=True))
            return content
    return ""

month_mapping = {
    "बैशाख": 1,
    "वैशाख": 1,
    "जेष्ठ": 2,
    "जेठ":2,
    "आषाढ़": 3,
    "असार": 3,
    "श्रावण": 4,
    "साउन":4,
    "भाद्र": 5,
    "भदौ": 5,
    "आश्विन": 6,
    "असोज": 7,
    "कार्तिक": 7,
    "कात्तिक": 7,
    "मंसिर": 8,
    "मिनेट": 4,
    "पुष": 9,
    "पुस": 9,
    "माघ": 10,
    "फाल्गुन": 11,
    "फागुन": 11,
    "चैत्र": 12,
    "चैत": 12,
}

def scrape_setopati_articles(url):
    articles = []
    headers = {'User-Agent': 'Mozilla/5.0'}
    current_date = datetime.now()
    two_months_ago = current_date - timedelta(days=14)  # 60 days for roughly two months

    article_count = 0
    while article_count < 30:
        article_count +=1
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            break  # Break the loop if the page fails to load or no more pages are available

        soup = BeautifulSoup(response.content, 'html.parser')

        # Loop through each article item
        for item in soup.select('.special-news .items'):
            article = {}
            article['title'] = item.select_one('.main-title').text.strip()
            article['url'] = item.select_one('a')['href']
            
            # Extract the publication date and author
            date_stamp = item.select_one('.date-stamp')
            if date_stamp:
                author_title = date_stamp.select_one('.author-title').text.strip()
                time_stamp = date_stamp.select_one('.time-stamp').text.strip()

                # Convert Nepali date to Gregorian date
                nepali_date_str = time_stamp.split(", ")
                nepali_year = int(nepali_date_str[-1].strip())
                nepali_date_parts = nepali_date_str[-2].split(" ")
                nepali_month = month_mapping[nepali_date_parts[0]]
                nepali_day = int(nepali_date_parts[1].replace(",", ""))
                nepali_date = nepali_datetime.date(nepali_year, nepali_month, nepali_day)
                gregorian_date = nepali_date.to_datetime_date()
                article['author'] = author_title
                article['date'] = gregorian_date.strftime('%Y-%m-%d')
                if gregorian_date < two_months_ago.date():
                    return articles
            else:
                article['author'] = 'Unknown'
                article['date'] = 'Unknown'
            
            # Placeholder for content and summary extraction
            article['content'] = get_setopati_article_content(article['url']) # Implement content extraction if needed
            article['summary'] = ''  # Implement summary extraction if needed
            
            articles.append(article)
        print('going to next page')
        # Check for the next page link and update the URL if available, else break
        next_page_link = soup.select_one('.pagination .nextpostslink')
        if next_page_link:
            url = next_page_link['href']
        else:
            break

    return articles

# Example usage
url = 'https://www.setopati.com/exclusive'
articles_setopati = scrape_setopati_articles(url)
for article in articles_setopati:
    # print(article)
    pass

print('done scraping setopati')


def get_onlinekhabar_article_content(url):
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    content = ""
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        # Extracting the main content of the article
        article_body = soup.select_one('.ok18-single-post-content-wrap')
        if article_body:
            paragraphs = article_body.find_all('p')
            content = ' '.join(paragraph.text for paragraph in paragraphs if paragraph.text)
        
        # Extracting the date from the new structure
        date_info_element = soup.select_one('.ok-news-post-hour span') or soup.select_one('.post__time span')
        if date_info_element:
            date_info = date_info_element.text
        # The date format is expected to be "YYYY भदौ २५ गते ८:१४ मा प्रकाशित"
        # Split and convert Nepali date to Gregorian date
            nepali_date_parts = date_info.split(' ')
            if nepali_date_parts[1] == 'मिनेट':
                gregorian_date = datetime.now()
            else:
                nepali_year = int(nepali_date_parts[0])
                nepali_month = month_mapping[nepali_date_parts[1]]
                nepali_day = int(nepali_date_parts[2].replace('गते', ''))
                nepali_date = nepali_datetime.date(nepali_year, nepali_month, nepali_day)
                gregorian_date = nepali_date.to_datetime_date()
            
            return {
                "content": content,
                "date": gregorian_date.strftime('%Y-%m-%d')
            }
        else: 
              return {
                "content": content,
                "date": "1990-01-01",
            }
    return {"content": content, "date": ""}



def scrape_onlinekhabar_articles(url):
    articles = []
    headers = {'User-Agent': 'Mozilla/5.0'}
    current_date = datetime.now()
    two_months_ago = current_date - timedelta(days=14)   # Approximation for two months

    while True:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            break

        soup = BeautifulSoup(response.content, 'html.parser')

        for item in soup.select('.search-results-append .ok-news-post'):
            article = {}
            article['title'] = item.select_one('.ok-news-title-txt').text.strip()
            article['url'] = item.select_one('a')['href']
            article['image'] = item.select_one('img')['src']
            article['source_name'] = 'Online Khabar Nepal'


            extracted_content = get_onlinekhabar_article_content(article['url'])
            if extracted_content['date'] != '':
                article['date'] = extracted_content['date']
                
                article_date_obj = datetime.strptime(article['date'], '%Y-%m-%d').date()  # Convert string to datetime.date object

                if article_date_obj < two_months_ago.date():
                    return articles  # Placeholder
            article['content'] = extracted_content['content']

            articles.append(article)


        # Check for the next page link and update the URL if available
        next_page_link = soup.select_one('.pagination .nextpostslink')
        if next_page_link:
            url = next_page_link['href']
        else:
            break

    return articles

# Generate URLs for both sets of keywords
human_wildlife_conflict_urls = generate_search_urls(human_wildlife_conflict_keywords, nepali_base_url_format)
illegal_wildlife_trade_urls = generate_search_urls(illegal_wildlife_trade_keywords, nepali_base_url_format)
infrastructure_urls = generate_search_urls(infrastructure_impact_keywords, nepali_base_url_format)

# Combine all URLs
all_search_urls = human_wildlife_conflict_urls + illegal_wildlife_trade_urls + infrastructure_urls
seen_urls = set()
unique_articles_nepali = []

for url in all_search_urls:
    print(url)
    articles = scrape_onlinekhabar_articles(url)  # Assuming this function is adapted to accept URLs directly
    for article in articles:
        if article['url'] not in seen_urls:
            unique_articles_nepali.append(article)
            seen_urls.add(article['url'])

print('done scraping online khabar nepali')


def get_onlinekhabar_article_content_en(url):
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    content = ""
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        article_body = soup.select('.post-content-wrap p')
        content = ' '.join(p.text for p in article_body)
        date_info = soup.select_one('.ok-post-date').text
        # Convert the date_info to datetime object
        article_date = datetime.strptime(date_info, '%A, %B %d, %Y').date()
        
        return {
            "content": content,
            "date": article_date.strftime('%Y-%m-%d')
        }
    return {"content": content, "date": ""}

def scrape_onlinekhabar_articles_en(url):
    articles = []
    headers = {'User-Agent': 'Mozilla/5.0'}
    current_date = datetime.now()
    two_months_ago = current_date - timedelta(days=14)  # Corrected approximation for two months

    while True:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            break

        soup = BeautifulSoup(response.content, 'html.parser')

        # Adjusted the selector to match the English site structure
        for item in soup.select('.ok-news-post.ltr-post'):
            article = {}
            # Updated selectors to match the English site's HTML structure
            article['title'] = item.select_one('.ok-post-contents h2 a').text.strip()
            article['url'] = item.select_one('.ok-post-contents h2 a')['href']
            article['image'] = item.select_one('.ok-post-image img')['src']
            article['source_name'] = 'Online Khabar EN'

            # Assuming `get_onlinekhabar_article_content_en` is a function you have that fetches the article content and date
            extracted_content = get_onlinekhabar_article_content_en(article['url'])
            if extracted_content['date'] != '':
                article['date'] = extracted_content['date']
                print(article['date'])

                
                article_date_obj = datetime.strptime(article['date'], '%Y-%m-%d').date()  # Assuming date format is the same

                if article_date_obj < two_months_ago.date():
                    return articles
            article['content'] = extracted_content['content']

            articles.append(article)

        # Updated the selector for the pagination link
        next_page_link = soup.select_one('.pagination-wrap .next.page-numbers')
        if next_page_link:
            url = next_page_link['href']
        else:
            break

    return articles

# Generate URLs for both sets of keywords
human_wildlife_conflict_urls = generate_search_urls(human_wildlife_conflict_keywords, english_base_url_format)
illegal_wildlife_trade_urls = generate_search_urls(illegal_wildlife_trade_keywords, english_base_url_format)
infrastructure_urls = generate_search_urls(infrastructure_impact_keywords, english_base_url_format)

# Combine all URLs
all_search_urls = human_wildlife_conflict_urls + illegal_wildlife_trade_urls + infrastructure_urls
seen_urls = set()
unique_articles = []

for url in all_search_urls:
    print(url)
    articles = scrape_onlinekhabar_articles_en(url)  # Assuming this function is adapted to accept URLs directly
    for article in articles:
        if article['url'] not in seen_urls:
            unique_articles.append(article)
            seen_urls.add(article['url'])

print('done scraping online khabar English')

def scrape_mongabay_articles(base_url):
    articles = []
    headers = {'User-Agent': 'Mozilla/5.0'}
    two_weeks_ago = datetime.now() - timedelta(days=14)
    next_page = 2
    while True:
        response = requests.get(base_url, headers=headers)
        if response.status_code != 200:
            break

        soup = BeautifulSoup(response.content, 'html.parser')
        for article in soup.find_all('article', class_='post-news'):
            title = article.find('h2', class_='post-title-news').get_text(strip=True)
            url = article.find('h2', class_='post-title-news').a['href']
            author_date = article.find('div', class_='entry-meta-news').get_text(strip=True)
            try:
                author, date_str = re.match(r"(by[A-Za-z ]+)(\d{1,2} \w+ \d{4})", author_date).groups()
                author = author.replace('by', '').strip()
                date = datetime.strptime(date_str, '%d %B %Y')
                if date < two_weeks_ago:
                    print('DONE COLLECTING ALL ARTICLES')
                    return articles
            except:
                author = 'Unknown'
                date = '01-01-1900'


            excerpt = article.find('div', class_='excerpt-news').get_text(strip=True)
            content = get_mongabay_article_content(url)  # Get the full article content
            print('\n\n\n\n')
            print(date)
            articles.append({'title': title, 'url': url, 'author': author, 'date': date, 'summary': excerpt, 'content': content, 'source_name': 'Mongabay'})
        
        base_url = f'https://news.mongabay.com/list/nepal/page/{next_page}'
        next_page +=1

    return articles

def parse_himalayan_date(date_text):
    # Handle relative dates
    if 'ago' in date_text:
        number, unit = date_text.split()[:2]
        if 'd' in number:
            return datetime.now() - timedelta(days=int(number.split('d')[0]))
        number = int(number)
        if 'h' in unit:  # Hours ago
            return datetime.now() - timedelta(hours=number)
        elif 'd' in unit:  # Days ago
            return datetime.now() - timedelta(days=number)
    else:
        # Handle absolute dates, adjust the format as per the website's date format
        try:
            return datetime.strptime(date_text, '%d %b, %Y')
        except ValueError:
            # Log error or handle as appropriate
            pass
    return None

def scrape_thehimalayantimes_articles(base_url, days_ago=14):
    articles = []
    headers = {'User-Agent': 'Mozilla/5.0'}
    threshold_date = datetime.now() - timedelta(days=days_ago)
    page = 1

    while True:
        url = f"{base_url}&pgno={page}"
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            break

        soup = BeautifulSoup(response.content, 'html.parser')
        article_list = soup.select('.post_list .row')
        if not article_list:
            break  # Break if no articles found on the page

        for article in article_list:
            title = article.select_one('.alith_post_title a').get_text(strip=True)
            url = article.select_one('.alith_post_title a')['href']
            summary = article.select_one('.alith_post_except a').get_text(strip=True)
            date_text = article.select_one('.meta_date').get_text(strip=True)
            
            # Parse the date
            article_date = parse_himalayan_date(date_text)
            if article_date and article_date < threshold_date:
                return articles  # Stop fetching more pages if an article is older than the threshold

            if article_date:  # Add only if the date could be parsed
                articles.append({
                    'title': title,
                    'url': url,
                    'summary': summary,
                    'date': article_date.strftime('%Y-%m-%d'),
                    'source_name': 'The Himalayan Times',
                })
        
        page += 1  # Increment page number to fetch next page

    return articles


def get_thehimalayantimes_article_content(article_url):
    content = ""
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(article_url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        article_body = soup.select_one('.ht-article-details .post-content')
        paragraphs = article_body.find_all('p') if article_body else []
        content = ' '.join(paragraph.get_text(strip=True) for paragraph in paragraphs)
    return content


himalayan_times_base = "https://thehimalayantimes.com/search?query={query}"

infra_urls = generate_search_urls(infrastructure_impact_keywords, himalayan_times_base)
wildlife_conf_urls = generate_search_urls(human_wildlife_conflict_keywords, himalayan_times_base)
illegal_urls = generate_search_urls(illegal_wildlife_trade_keywords, himalayan_times_base)

search_urls = infra_urls + wildlife_conf_urls + illegal_urls
print(search_urls)
seen_urls = set()
himalayan_articles = []
for url in search_urls:
    articles = scrape_thehimalayantimes_articles(url)
    print(url)
    for article in articles:
        if article['url'] not in seen_urls:
            seen_urls.add(article['url'])
            content = get_thehimalayantimes_article_content(article['url'])
            article['content'] = content
            himalayan_articles.append(article)


shapefile_landscape_map = {
    'CHAL/chalb.shp': 'Chitwan Annapurna Landscape',
    'Kailesh/kailashb.shp': 'Kailash Sacred Landscape',
    'TAL/talb_dd.shp': 'Terai Arc Landscape',
    'KL/kclb.shp': 'Kanchenjunga Landscape',
    'SHL/shlb.shp': 'Sacred Himalayan Landscape'
}


def process_article_with_chat_api(article):
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {
            "role": "user",
            "content": f"{GPT4Prompt}. Analyze this article and extract the required information. Article content: {article['content']}"
        }
    ]
    try:

        response = openai.ChatCompletion.create(
            model="gpt-4-0125-preview",
            messages=messages
        )
        

        assistant_response = response['choices'][0]['message']['content']
        return assistant_response
    except Exception as e:

        print(f"An error occurred: {e}")
        return 
    """{'tags': '',
            'relevance_to_infrastructure': '',
            'relevance_to_conservation': '',
            'flora_and_fauna': '',
            'categories': '',
            'location': '',
            'landscape': ''}
        """

def clean_json_string(json_string):
    # Remove Markdown code block markers
    json_string = json_string.replace("```json", "").replace("```", "")
    # Strip leading and trailing whitespace
    json_string = json_string.strip()
    return json_string


def flatten_processed_info(article):
    try:
        processed_data = json.loads(clean_json_string(article['processed_info']))
        for key, value in processed_data.items():
            article[key] = value
    except json.JSONDecodeError:
        print("Error decoding JSON from processed info")
        # Add keys with empty values if JSON decoding fails
        article.update({
            'tags': '',
            'relevance_to_infrastructure': '',
            'relevance_to_conservation': '',
            'flora_and_fauna': '',
            'categories': '',
            'location': '',
            'landscape': ''
        })

def save_articles_to_csv(articles, filename):
    # Collect all unique keys from all articles
    keys = set(key for article in articles for key in article.keys())

    with open(filename, 'w', newline='', encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(articles)

def load_articles_from_csv(filename):
    articles = []
    with open(filename, 'r', newline='', encoding='utf-8') as input_file:
        dict_reader = csv.DictReader(input_file)
        for row in dict_reader:
            articles.append(row)
    return articles

all_articles = himalayan_articles + unique_articles + scrape_mongabay_articles('https://news.mongabay.com/list/nepal/page/1') + unique_articles_nepali
save_articles_to_csv(all_articles, 'unprocessed-articles.csv')
filename = 'unprocessed-articles.csv'

# Load articles from the CSV file
articles = load_articles_from_csv(filename)


# for article in tqdm(df1., desc="Processing articles"):
for index, article in tqdm(enumerate(articles), total=len(articles)):

    if (article['content'] == ''):
        continue

    article['processed_info'] = process_article_with_chat_api(article)
    flatten_processed_info(article)

    location = article['location']
    lat, lon = get_coordinates(location)
    article['latitude'] = lat if lat else ''
    article['longitude'] = lon if lon else ''
    if lat and lon:
        point = Point(lon, lat)
        landscape_found = False

        for shapefile, landscape_name in reversed(sorted(shapefile_landscape_map.items())):
            if is_point_in_shapefile(point, shapefile):
                article['Landscape-Location'] = landscape_name
                article['closest_landscape'] = landscape_name
                landscape_found = True
                break
        if not landscape_found:
            article['Landscape-Location'] = 'Other'
            try:
                article['closest_landscape'] = find_closest_landscape(point, shapefile_landscape_map)
            except:
                article['closest_landscape'] = 'Other'
    else:
        article['Landscape-Location'] = 'Other'
        article['closest_landscape'] = 'Other'

processed_articles = []
for article in articles:
    print(article)
    if article['content'] == '' or(float(article['relevance_to_conservation']) < 0.5 and float(article['relevance_to_infrastructure']) < 0.5) :
        continue
    processed_articles.append(article)
save_articles_to_csv(processed_articles, '../src/data/weekly-nepal-articles.csv')


