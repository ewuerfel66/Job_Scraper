"""
Heroku app that scrapes job ads for permutations of locations & titles.

User Input: Location List, Title List, Job Description

Output: 20 Job Postings
"""

#######################
####### Imports #######
#######################

# Flask App Imports
from flask import Flask, jsonify, request, json
from flask_restful import Api, reqparse
from flask_cors import CORS

# The usuals
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# System Imports
import re
import os
import time

# Selenium Imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys

# Other imports
from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
import spacy

# Functions (Local Imports)
from functions import (
    clear_auto, deep_indeed_query, clean_jobs,
    indeed_crawl, clean_description, tokenize,
    fit_for_nn, transform_query_for_nn, parse
)

###############################################
############ Create Flask App #################
###############################################

def create_app():
    """
    Creates and configures an instance of our Flask API
    """
    app = Flask(__name__)

    # enable CORS on all app routes
    CORS(app)

    # initialize the api wrapper
    api = Api(app)

    ############################################################
    ################### ENDPOINTS / ROUTES #####################
    ############################################################

    @app.route("/indeed_crawl", methods=["POST"])
    def indeed_crawl_query():
        print("Getting request...")
        values = request.get_json()

# Expecting JSON like:
# {
#     locations: ['Washington, DC', 'Charlotte, NC', 'Roanoke, VA']
#     titles: ['Data Scientist', 'Data Analyst']
#     query: """I use python to collect and scrape data from the web. I can set up integrated data pipelines
#         pipeline to collect data from different sources. I train machine learning models using sklearn, 
#         and tensorflow with keras. BeautifulSoup and Selenium. BeautifulSoup and Selenium.
#         BeautifulSoup and Selenium. BeautifulSoup and Selenium. I can give results to developers using Flask apps
#         and Flask APIs API. I can access APIs API and RSS feeds. I can also use SQL, particularly ElephantSQL
#         and Postgres. I like venture capital, finance and business consulting. I love to work with
#         natural language processing. Looking for a junior or entry level entry-level or mid level mid-level
#         venture capital, finance and business consulting venture capital, finance and business consulting
#         venture capital, finance and business consulting venture capital, finance and business consulting"""
# }

        # Extract request data
        locations = values['locations']
        titles = values['titles']
        query = values['query']

        # Disable auto-complete
        print("Launching browser...")
        profile = webdriver.FirefoxProfile()
        profile.set_preference("browser.formfill.enable", "false")
            
        # Create new Instance of Chrome in incognito mode
        browser = webdriver.Firefox(executable_path='../../../Selenium/geckodriver')

        # Instantiate dirty_jobs
        dirty_jobs = []

        # Crawl over indeed.com
        jobs = indeed_crawl(titles, locations, dirty_jobs, browser)

        # Clean up the text from the lxml
        print('Parsing descriptions...')
        texts = parse(jobs)
        texts = [str(text)[1:-1] for text in texts]

        # Send to df
        df = pd.DataFrame(texts, columns = ['description'])
        df['jobs'] = jobs

        # NLP Model
        print('Loading model...')
        nlp = spacy.load("en_core_web_md")
        print('Done loading model!')

        # Clean and tokenize the descriptions
        # df['tokens'] = [tokenize(entry, nlp) for entry in df['description'].apply(clean_description).tolist()]

        # send clean text to list
        text = df['description'].apply(clean_description).tolist()

        # Instantiate Vectorizer
        print('Fitting vectorizer...')
        tfidf_dtm = fit_for_nn(text)

        # Create a vocab and get word counts per doc
        sparse = tfidf.fit_transform(text)

        # send to df
        tfidf_dtm = pd.DataFrame(sparse.todense(), columns = tfidf.get_feature_names())

        # Instantiate model
        print('Teaching the computer...')
        nn = NearestNeighbors(n_neighbors=20, algorithm='ball_tree')
        nn.fit(tfidf_dtm)
        print('Damn, that computer is smart.')

        # Process query for the model
        print('Asking the computer for recommendations...')
        query_dtm = process_query_for_nn(query)

        # Query for closest neighbors
        results = nn.kneighbors(query_dtm)[1][0].tolist()

        # Send to list
        job_urls = df['jobs'][results].tolist()

        print('Done!')
        return jsonify({'jobs': job_urls})

    # Close out the app
    return app

create_app()