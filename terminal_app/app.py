"""
Heroku app that scrapes job ads for permutations of locations & titles.

User Input: Location List, Title List, Job Description

Output: 20 Job Postings
"""

print("")
print("-------------------")
print("--- Job Scraper ---")
print("-------------------")
print("")
print("A browser will open in a second, let it do it's thing.")

#######################
####### Imports #######
#######################

# The usuals
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# System Imports
import re
import os
import time

# Functions (Local Imports)
from functions import *


###############################################
############ Get input values #################
###############################################

# Titles and locations
titles = [ "Data Analyst"]

locations = ["Raleigh-Durham, NC", "Charlotte, NC", "Roanoke, VA", "Charlottesville, VA",
             "Greensboro, NC"]

query = """I use python to collect and scrape data from the web. I can set up integrated data pipelines
        pipeline to collect data from different sources. I train machine learning models using sklearn, 
        and tensorflow with keras. BeautifulSoup and Selenium. BeautifulSoup and Selenium.
        BeautifulSoup and Selenium. BeautifulSoup and Selenium. I can give results to developers using Flask apps
        and Flask APIs API. I can access APIs API and RSS feeds. I can also use SQL, particularly ElephantSQL
        and Postgres. I like venture capital, finance and business consulting. I love to work with
        natural language processing. Looking for a junior or entry level entry-level or mid level mid-level
        venture capital, finance and business consulting venture capital, finance and business consulting
        venture capital, finance and business consulting venture capital, finance and business consulting"""


###############################################
########### Scrape Job Listings ###############
###############################################

# Instantiate dirty_jobs
dirty_jobs = []

# Crawl over indeed.com
print("Crawling Indeed:")
jobs = indeed_crawl(titles, locations, dirty_jobs, browser)

# Clean up the text from the lxml
print('Parsing descriptions...')
print("You can close that browser now")
texts = parse(jobs)
texts = [str(text)[1:-1] for text in texts]


# Send to df
df = pd.DataFrame(texts, columns = ['description'])
df['jobs'] = jobs

# NLP Model
print('Loading Natural Language model...')
nlp = spacy.load("en_core_web_md")
print('Done loading model!')

# DO NOT MOVE THESE FUNCTIONS TO functions.py!!!
def tokenize(text):
    # Tokenize
    global nlp
    doc = nlp(text)
    tokens = [token.lemma_ for token in doc if (token.is_stop != True) and (token.is_punct != True)]
    if ' ' in tokens:
        tokens.remove(' ')
    if '  ' in tokens:
        tokens.remove('  ')
    return tokens

print("Tokenizing the data...")

# send clean text to list
text = df['description'].apply(clean_description).apply(tokenize).tolist()
# join tokens for vectorizer
text = [" ".join(entry) for entry in text]

# Instantiate Vectorizer
tfidf = TfidfVectorizer(stop_words = 'english')

# Instantiate Vectorizer
print('Fitting vectorizer...')
# Create a vocab and get word counts per doc
sparse = tfidf.fit_transform(text)
# send to df
tfidf_dtm = pd.DataFrame(sparse.todense(), columns = tfidf.get_feature_names())

# Instantiate model
print('Teaching the computer...')
nn = NearestNeighbors(n_neighbors=20, algorithm='ball_tree')
nn.fit(tfidf_dtm)
print('Damn, that computer is smart.')

# DO NOT REMOVE THIS FUNCTION
def transform_query_for_nn(string):
    # Create a vocab and get word counts per doc
    global tfidf
    sparse = tfidf.transform([query])
    query_dtm = pd.DataFrame(sparse.todense(), columns = tfidf.get_feature_names())
    return query_dtm

# Process query for the model
print('Asking the computer for recommendations...')
query_dtm = transform_query_for_nn(query)

# Query for closest neighbors
results = nn.kneighbors(query_dtm)[1][0].tolist()

# Send to list
job_urls = df['jobs'][results].tolist()

print('Done!')
print("")

open_jobs(job_urls, browser)