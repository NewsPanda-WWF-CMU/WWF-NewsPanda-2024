# Environment Setup:

Ensure Python 3.8+ is installed.

Install required packages: use `pip install -r requirements.txt` (ENSURE OPENAI IS VERSION 0.27.8)

For each script, set the open_ai_key in the script.

# News Article Processing and Analysis (scrape scripts)
## Overview
This Python script is designed to automate the collection, processing, and analysis of news articles from various sources for both  It focuses on extracting environmental and wildlife-related data, particularly looking at infrastructure impacts, human-wildlife conflict, and illegal wildlife trade.

## Usage

### Running the Script:

Execute the script using Python: python scrape_websites.py (for nepal) or python scrape-websites-india.py (for india).
The script will automatically scrape, process, and save the data into CSV files.

### Output:
Outputs include CSV files containing processed article data and a detailed analysis of each article based on environmental impact parameters and store the `weekly` files in the `src/data` directory.

### Configurations
Keywords for article scraping can be modified in the script under the lists infrastructure_impact_keywords, human_wildlife_conflict_keywords, and illegal_wildlife_trade_keywords.
The base URLs for different news sources are set at the top of the script and can be updated as needed.

### Note

This script requires internet access to fetch articles and use the OpenAI API for processing.
Ensure that the GeoPandas and Shapely libraries are properly configured, especially on Windows, due to their dependencies on C libraries.

# Combining scripts (combine-csvs-*.py)

## Overview
This script automates the aggregation, processing, and enhancement of news articles from multiple sources concerning environmental issues and conservation efforts in Nepal. It aims to structure unstructured data for better analysis and reporting.

## Functionalities
Data Aggregation: Collects articles from various news sources, focusing on topics like infrastructure impact, human-wildlife conflict, and illegal wildlife trade.
Renaming Columns: Standardizes column names across different data sources for consistency.
Geographic Analysis: Determines the geographical coordinates and assesses proximity to significant landscapes using shapefiles.
Date Handling: Converts publication dates to a uniform datetime format and sorts articles by date.
Text Cleaning: Removes unnecessary characters from text fields to clean data.
Duplicate Removal: Ensures the uniqueness of articles based on their URLs.

## Usage
Execute the script using Python: python combine-csvs-nepal.py (for nepal) or python combine-csvs-india.py (for india).
The script will automatically process and save the data into CSV files.

## Output 

This will update within the `src/data` folder of the main directory with the currently set articles

# Event Generation Scripts

## Overview

The two remaining python scripts `generate-events-at-scale.py` and `generate-events-from-summary.py` are designed to analyze and summarize groups of news articles that discuss the same significant events, particularly in the context of wildlife and environmental issues. It uses advanced natural language processing (NLP) techniques powered by OpenAI's GPT model to extract detailed insights and generate summaries from multiple sources.

## Usage

Before execution, ensure you set the csv of the articles of your choice from previous scripts to the top of the file in this line `df1 = pd.read_csv('')`

Execute the script using Python: python generate-events-at-scale.py (technique 1) or python generate-events-from-summary.py (technique 2).

The script will automatically process and save the data into CSV files.

Ensure 

## Functionalities

Data Aggregation: The script starts by reading and concatenating articles from CSV files into a single DataFrame, ensuring a unified structure for analysis.
Data Cleaning: It eliminates duplicate entries based on article URLs and converts publication dates into a consistent datetime format.
Data Sorting: Articles are sorted by their publication dates to assist in chronological analysis.
Term Analysis: A set of combined terms (keywords and category tags) is created for each article to facilitate detailed comparison and grouping based on content similarity.
Event Grouping: Articles are grouped into "events" based on the overlap of their combined terms, aiming to identify articles that discuss the same incident or topic.
Event Summarization: Utilizes OpenAI's GPT model to generate comprehensive summaries and detailed event descriptions in a structured JSON format, highlighting unique and common information across articles.
Output Generation: Processes and saves the event data into CSV files, providing an accessible format for further use or reporting.

## Key Operations
Conversion and Formatting: Converts all relevant fields to suitable formats (e.g., datetime) and standardizes text fields to ensure clean data for processing.
Overlap Calculation: Calculates the overlap of terms between different articles to determine which articles are likely discussing the same events.
NLP Analysis: Uses a sophisticated AI model to analyze the content deeply and extract structured summaries and actionable insights.
Data Export: The final structured outputs are exported as CSV files which include details about each event, like URLs involved, summary, detailed analysis, and proposed actions.

# Outputs
The script output different files based on the script that is run in the `src/data` directory:

'processed_event_summaries_at_scale.csv': Contains detailed summaries and analyses of each event, formatted as actionable insights and structured JSON.

'processed_event_summaries_from_summary.csv': Contains detailed summaries and analyses of each event, formatted as actionable insights and structured JSON.

# NOTE: EXPERIMENTAL SCRIPTS CONTAIN ALL OTHER EXPERIMENTS

