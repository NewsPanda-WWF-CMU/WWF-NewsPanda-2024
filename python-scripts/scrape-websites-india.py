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
import urllib.parse
import pandas as pd


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


GPT4Prompt = """
Given the following article content, analyze and extract the required information in the specified format. Identify relevant tags from the list: [Fishing, Restoration, Marine Habitat, NGO, Species Loss, Freshwater Habitat, Pollution, Governance, Social Conflict, Shipping, Extractives - Oil and Gas, Habitat Loss, Atmosphere, Invasive Species, Social, Climate Change, Tourism, Illegal Wildlife Trade, Agriculture, Terrestrial Habitat, Extractives - Mining]. Determine the categories as one or more from: ["Wildlife", "Freshwater", "Climate and Energy", "Forests", "Governance", "Infrastructure"]. Also, identify the relevance to infrastructure and conservation on a scale of 0 to 1, the landscape from the options ["Terai Arc Landscape", "Sacred Himalayan Landscape", "Kailash Sacred Landscape", "Chitwan Annapurna Landscape", "Kanchenjunga Landscape", "Other(Nepal)", "Other(World)"], and possible flora and fauna impacted in a list with their scientific names. Lastly, provide a general location of the events in the article.
Flora Fauna List - one or more from ["Asian Elephant (Elephas maximus)", "Bengal Tiger (Panthera tigris ssp. tigris)", "Greater One-horned Rhinoceros (Rhinoceros unicornis)", "Gharial (Gavialis gangeticus)", "Otter (Lutra lutra & Lutrogale perspicillata)", "Pangolin (Manis crassicaudata & Manis pentadactyla)", "Red Panda (Ailurus fulgens)", "South Asian River Dolphin (Platanista gangetica)", "Snow Leopard (Panthera uncia)", "Tree Fern (Cyathea spp.)", "Champ (Michelia champaca)", "Bijaysal (Pterocarpus marsupium)", "Rhododendron (Rhododendron spp.)", "Other"]
Please provide the structured data as follows that can be JSON Decoded (THIS IS VERY IMPORTANT):
{
    "relevance_to_infrastructure": [Value between 0 and 1],
    "relevance_to_conservation": [Value between 0 and 1],
    "relevance_to_human_wildlife_conflict": [Value between 0 and 1],
    "relevance_to_illegal_wildlife_trade":[Value between 0 and 1],
    "location": "Preferably as specific a location where the events of the article are located specific to city or town. If not able to give this just list World",
    "indian_state": <The indian state that this article belongs to, if its not mentioned or not an article in India just mention Other>,
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

def get_traffic_article_content(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    response = requests.get(url, headers=headers)
    content = ""

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        article_body = soup.find('div', class_='col-lg-9 body')
        if article_body:
            paragraphs = article_body.find_all('p', style=False)  # Avoiding styled paragraphs like 'text-align:justify;'
            content = ' '.join(paragraph.get_text(strip=True) for paragraph in paragraphs)

    return content

hindi_month_mapping = {
        'जनवरी': 'January',
        'फ़रवरी': 'February',
        'मार्च': 'March',
        'अप्रैल': 'April',
        'फ़रवरी': 'February',
        'मई': 'May',
        'जून': 'June',
        'जुलाई': 'July',
        'अगस्त': 'August',
        'सितम्बर': 'September',
        'अक्टूबर': 'October',
        'नवम्बर': 'November',
        'दिसम्बर': 'December',
    }


def scrape_wti_articles(base_url='https://www.wti.org.in/resource-centre/news/page/1'):
    articles = []
    two_weeks_ago = datetime.now() - timedelta(days=7)
    next_page = 2
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    while True:
        response = requests.get(base_url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            for article in soup.find_all('article', class_='post'):

                title = article.find('h3', class_='greennature-blog-title').get_text(strip=True)
                url = article.find('a')['href']
                date_str = article.find('div', class_='blog-date').get_text(strip=True)
                summary = article.find('div', class_='greennature-blog-content').get_text(strip=True, separator=' ').split('...')[0]

                # Since the date is provided as a full URL, extracting the date portion
                date = datetime.strptime(date_str, '%B %d, %Y')
                if date < two_weeks_ago:
                    print('done collecting wti articles')
                    return articles
                content = get_wti_article_content(url)  # Get the full article content

                articles.append({'title': title, 'language': 'English', 'url': url, 'author': 'WTI', 'date': date, 'summary': summary, 'content': content, 'source_name': 'WTI'})

            base_url = f'https://www.wti.org.in/resource-centre/news/page/{next_page}'
            next_page +=1
        else:
            print(f"Failed to retrieve the page: Status code {response.status_code}")

def get_wti_article_content(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    response = requests.get(url, headers=headers)
    content = ""

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        article_content = soup.find('article', class_='news')
        if article_content:
            content_paragraphs = article_content.find('div', class_='greennature-blog-content').find_all('p')
            content = ' '.join([paragraph.get_text(strip=True) for paragraph in content_paragraphs])

    else:
        print(f"Failed to retrieve the article: Status code {response.status_code}")

    return content

def scrape_mongabay_india_articles_hindi():
    articles = []
    headers = {'User-Agent': 'Mozilla/5.0'}
    two_weeks_ago = datetime.now() - timedelta(days=7)
    next_page = 2
    base_url = 'https://hindi.mongabay.com/list/india/page/1'
    while True:
        response = requests.get(base_url, headers=headers)
        if response.status_code != 200:
            break

        soup = BeautifulSoup(response.content, 'html.parser')
        for article in soup.find_all('article', class_='post-news'):
            title = article.find('h2', class_='post-title-news').get_text(strip=True)
            url = article.find('h2', class_='post-title-news').a['href']
            author_date = article.find('div', class_='entry-meta-news').get_text(strip=True)

            for hi, en in hindi_month_mapping.items():
                author_date = author_date.replace(hi, en)
            try:
                author, date_str = re.match(r"(by[A-Za-z ]+)(\d{1,2} \w+ \d{4})", author_date).groups()
                author = author.replace('by', '').strip()
                date = datetime.strptime(date_str, '%d %B %Y')
                if date < two_weeks_ago:
                    print('DONE COLLECTING Mongabay HINDI ARTICLES')
                    return articles
            except:
                author = 'Unknown'
                date = '01-01-1900'


            excerpt = article.find('div', class_='excerpt-news').get_text(strip=True)
            content = get_mongabay_article_content(url)  # Get the full article content
            print('\n\n\n\n')
            print(date)
            articles.append({'title': title, 'language': 'Hindi', 'url': url, 'author': author, 'date': date, 'summary': excerpt, 'content': content, 'source_name': 'Mongabay'})
        
        base_url = f'https://hindi.mongabay.com/list/india/page/{next_page}'
        next_page +=1

    return articles

def scrape_ndtv_hindi_news():
    articles = []
    # Assuming the starting URL is for a specific news list section
    two_weeks_ago = datetime.now() - timedelta(days=7)

    base_urls = ['https://ndtv.in/topic/wildlife/news/', 'https://ndtv.in/topic/construction/news/']
    next_page = 1
    for base_url in base_urls:
        while True:
            response = requests.get(base_url+str(next_page))
            if response.status_code != 200:
                break  # If error, exit loop
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all article entries on the page. Adjust the class as per actual website structure
            for article in soup.find_all('li', class_='src_lst-li'):
                title = article.find('div', class_='src_itm-ttl')
                if title:
                    title = title.get_text(strip=True)
                    url = article.find('a')['href']
                    summary = article.find('div', class_='src_itm-txt').get_text(strip=True)
                    date_text = article.find('span', class_='src_itm-stx').get_text(strip=True)
                    extracted_date = date_text.split("|")[-1].strip()  # 'मंगलवार अप्रैल 9, 2024 03:55 PM IST'

                    # Splitting based on spaces and picking out date parts
                    parts = extracted_date.split()
                    month = hindi_month_mapping[parts[1]]
                    day = parts[2].replace(',', '')  # Removing the comma
                    year = parts[3]
                    time = parts[4] + ' ' + parts[5]  # Adding AM/PM

        # Combining the date parts into a single string
                    date_string = f"{month} {day} {year} {time}"
                    print(date_string)

                    # Parsing the date string into a datetime object
                    date_object = datetime.strptime(date_string, '%B %d %Y %I:%M %p')

                    if date_object < two_weeks_ago:
                            print('DONE COLLECTING ALL NDTV HINDI ARTICLES')
                            return articles
                    content = get_ndtv_article_content(url)
                    
                    articles.append({'title': title, 'url': url, 'summary': summary, 'date': date_object,  'content': content, 'source': 'NDTV Hindi', 'language': 'Hindi', 'author': 'NDTV' })
            
            # Check for a "Load More" button or next page link and update base_url accordingly
            # This example assumes there's a button or link to load more news. Adjust based on actual page structure
            next_page +=1

    return articles


def get_ndtv_article_content(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    response = requests.get(url, headers=headers)
    article_info = {
        "headline": "",
        "description": "",
        "content": []
    }

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract headline
        headline_tag = soup.find('h1', itemprop="headline")
        if headline_tag:
            article_info["headline"] = headline_tag.get_text(strip=True)

        # Extract description
        description_tag = soup.find('h2', class_="sp-descp")
        if description_tag:
            article_info["description"] = description_tag.get_text(strip=True)

        # Extract content paragraphs
        content_div = soup.find('div', itemprop="articleBody")
        if content_div:
            paragraphs = content_div.find_all('p')
            for paragraph in paragraphs:
                text = paragraph.get_text(strip=True)
                if text:  # Ensure the paragraph is not empty
                    article_info["content"].append(text)
        article_info['final_content'] = article_info["headline"] + article_info["description"]  +str(article_info["content"])
    else:
        print(f"Failed to retrieve the article: Status code {response.status_code}")

    return article_info['final_content']


def scrape_traffic_org_articles():
    articles = []
    base_url = 'https://www.traffic.org/news/?nq=india'  # Assuming a base URL for demonstration
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}
    two_weeks_ago = datetime.now() - timedelta(days=7)


    response = requests.get(base_url, headers=headers)
    print(response)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        # Assuming each article is contained in a div with class attribute 'card border-0'
        for article_div in soup.find_all('div', class_='p-2'):
            try:
                 # Extracting URL
                relative_url = article_div.find('a')['href']
                url = f"{base_url}{relative_url}" if not relative_url.startswith('http') else relative_url

                # Extracting title
                title = article_div.find('h3').get_text(strip=True)
                # Extracting publication date
                date_str = article_div.find('p', class_='mt-4').get_text(strip=True)
                # Parsing the date assuming format 'dd Month yyyy'
                date = datetime.strptime(date_str, '%d %B %Y')
                print(date_str)
                if date < two_weeks_ago:
                    print('done collecting articles')
                    return articles

                # Extracting summary
                summary = article_div.find('p', class_='mb-0 text-sm lg:text-base').get_text(strip=True).replace(u'\xa0', u' ')
                content = get_traffic_article_content(url)  # Get the full article content
                articles.append({'title': title, 'language': 'Hindi', 'url': url, 'author': 'traffic-org', 'date': date, 'summary': summary, 'content': content, 'source_name': 'Traffic.Org'})

            except Exception as e:
                print(f"Error processing article: {e}")

    return articles




def scrape_mongabay_india_articles_en():
    articles = []
    headers = {'User-Agent': 'Mozilla/5.0'}
    two_weeks_ago = datetime.now() - timedelta(days=7)
    next_page = 2
    base_url = 'https://india.mongabay.com/page/1'
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
                print(author_date)
                author, date_str = re.match(r"(by[A-Za-z ]+)(\d{1,2} \w+ \d{4})", author_date).groups()
                author = author.replace('by', '').strip()
                print(date_str)
                date = datetime.strptime(date_str, '%d %B %Y')
                print(date)
                if date < two_weeks_ago:
                    print('DONE COLLECTING ALL ENGLISH ARTICLES')
                    return articles
            except:
                author = 'Unknown'
                date = '01-01-1900'


            excerpt = article.find('div', class_='excerpt-news').get_text(strip=True)
            content = get_mongabay_article_content(url)  # Get the full article content
            print('\n\n\n\n')
            print(date)
            articles.append({'title': title,'language': 'English', 'url': url, 'author': author, 'date': date, 'summary': excerpt, 'content': content, 'source_name': 'Mongabay'})
        
        base_url = f'https://india.mongabay.com/page/{next_page}'
        next_page +=1

    return articles


def scrape_downtoearth_articles(base_url='https://www.downtoearth.org.in/category/wildlife-and-biodiversity/news?page=1'):
    articles = []
    two_weeks_ago = datetime.now() - timedelta(days=7)
    next_page = 2
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

    while True:
        response = requests.get(base_url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            for link in soup.find_all('div', class_='pl-5'):

                article = {}
                final_a = None
                print(link)
                a_tags = link.find_all('a')
                for idx, a in enumerate(a_tags):
                    if idx == 1:
                        final_a = a
                        break


                if final_a:
                    article['url'] = final_a['href']
                    article['title'] = link.find("p", class_="content-head").text.strip()
                    article['summary'] = link.find("p", class_="content-main").text.strip()
                    date_str = link.find("div", class_="content-share").find("div", class_="pull-left content-date").text.strip()
                    article['date'] = datetime.strptime(date_str, '%B %d, %Y')
                    print(article['date'])

                    if article['date'] < two_weeks_ago:
                        print('DONE collecting down to earth articles')
                        return articles
                    
                    article['content'] = get_downtoearth_article_content(article['url'])
                    article['language'] = 'English'
                    article['source_name'] = 'Down to Earth'
                    print(article['content'])
                    articles.append(article)

            base_url = f'https://www.downtoearth.org.in/category/wildlife-and-biodiversity/news?page={next_page}'
            next_page += 1
        else:
            print(f"Failed to retrieve the page: Status code {response.status_code}")
            break

    return articles

def get_downtoearth_article_content(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    response = requests.get(url, headers=headers)
    content = ""
    print(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        article_content = soup.find('div', class_='news-detail-content')
        if article_content:
            paragraphs = article_content.find_all('p')
            content = ' '.join([paragraph.text for paragraph in paragraphs])
    else:
        print(f"Failed to retrieve the article: Status code {response.status_code}")

    return content

hindi_articles = scrape_mongabay_india_articles_hindi() + scrape_ndtv_hindi_news()

english_articles = scrape_downtoearth_articles() + scrape_mongabay_india_articles_en() + scrape_traffic_org_articles() + scrape_wti_articles()




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
    except:
        return 
    """{'tags': '',
            'relevance_to_infrastructure': '',
            'relevance_to_conservation': '',
            'flora_and_fauna': '',
            'categories': '',
            'location': '',
            'landscape': ''
                'relevance_to_human_wildlife_conflict':'',
    'relevance_to_illegal_wildlife_trade':''}
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
            'indian_state': '',
            'landscape': '',
            'relevance_to_human_wildlife_conflict':'',
            'relevance_to_illegal_wildlife_trade':'',
            'infrastructure-subtype': ''
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


save_articles_to_csv(english_articles + hindi_articles, 'un-processed-articles-india-apr16.csv')
filename = 'un-processed-articles-india-apr16.csv'

# Load articles from the CSV file
articles = load_articles_from_csv(filename)


for index, article in tqdm(enumerate(articles), total=len(articles)):

    if (article['content'] == ''):
        continue

    article['processed_info'] =  process_article_with_chat_api(article)
    flatten_processed_info(article)

save_articles_to_csv(articles, 'gpt-articles-indiaapr16.csv')
def safe_float(value, default=0.0):
    try:
        return float(value)
    except ValueError:
        return default
articles = load_articles_from_csv('gpt-articles-indiaapr16.csv')
processed_articles = []
for article in articles:
    if article['content'] == '' or (safe_float(article['relevance_to_human_wildlife_conflict']) < 0.5 and safe_float(article['relevance_to_illegal_wildlife_trade']) < 0.5 and safe_float(article['relevance_to_infrastructure']) < 0.5):
        continue
    processed_articles.append(article)

save_articles_to_csv(processed_articles, '../src/data/weekly-india-articles.csv')


