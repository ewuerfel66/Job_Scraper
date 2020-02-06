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
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.keys import Keys

# Other imports
from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
import spacy


###########################################
############## Functions ##################
###########################################

def open_browser():
    # Disable auto-complete
    print("Launching browser...")
    profile = webdriver.FirefoxProfile()
    profile.set_preference("browser.formfill.enable", "false")
    
# Create new Instance of Chrome in incognito mode
browser = webdriver.Firefox(executable_path='../../Selenium/geckodriver')
        

def indeed_query(title, location, dirty_jobs):
    # Go to Indeed homepage
    browser.get("https://www.indeed.com/")
    print("Scraping:", {title} - {location})

    # Find input fields
    try:
        what = browser.find_element_by_name("q")
        what.send_keys(str(title))
        where = browser.find_element_by_name("l")
        clear_auto(where)
        where.send_keys(str(location))

        # Click Search
        button = browser.find_element_by_class_name("icl-Button")
        button.click()

        # Collect pages to scrape
        url = browser.current_url

        # Get soup for the results page
        html = urlopen(url)
        soup = BeautifulSoup(html, 'html.parser')

        # extract job results
        for link in soup.find_all('a', {'class':'jobtitle turnstileLink'}):
            dirty_jobs.append(link.attrs['href'])
    except StaleElementReferenceException as e:
        print("Failed to scrape:", title, '-', location)
        pass
        

def deep_indeed_query(title, location, dirty_jobs, browser):
    # Go to Indeed homepage
    browser.get("https://www.indeed.com/")
    print('Scraping:', title, '-', location)
    # Find input fields
    try:
        what = browser.find_element_by_name("q")
        what.send_keys(str(title))
        where = browser.find_element_by_name("l")
        clear_auto(where)
        where.send_keys(str(location))
    except StaleElementReferenceException as e:
        print("Failed to fill:", title, '-', location)
        print(e)
        # Try again
        deep_indeed_query(title, location, dirty_jobs, browser)
        pass

    # Click Search
    button = browser.find_element_by_class_name("icl-Button")
    button.click()

    for i in range(3):
        # Collect pages to scrape
        url = browser.current_url

        # Get soup for the results page
        html = urlopen(url)
        soup = BeautifulSoup(html, 'html.parser')

        # extract job results
        for link in soup.find_all('a', {'class':'jobtitle turnstileLink'}):
            dirty_jobs.append(link.attrs['href'])
            
        # exit popup if it comes up
        try:
            popup_x = browser.find_element_by_class_name("icl-Icon icl-Icon--sm  icl-Icon--black close")
            popup_x.click()
        except NoSuchElementException:
            break
        
        # click on next page
        try:
            next_page = browser.find_element_by_class_name("np")
            next_page.click()
        except NoSuchElementException:
            break


def clean_description(text):
    # Clean
    clean_text = BeautifulSoup(text, "lxml").text
    # clean_text = clean_text[2:]
    clean_text = re.sub(r'\\n', ' ', clean_text)
    clean_text = re.sub(r'/', ' ', clean_text)
    clean_text = re.sub(r'[^a-zA-Z ^0-9]', '', clean_text)
    
    return clean_text

        
def clean_jobs(jobs):
    # Find unique values
    jobs = list(set(jobs))
    
    # Clean clean clean
    for job in jobs:
        if job.startswith('/pagead'):
            jobs.remove(job)

    for job in jobs:
        if job.startswith('/pagead'):
            jobs.remove(job)

    for job in jobs:
        if job.startswith('/pagead'):
            jobs.remove(job)

    for job in jobs:
        if job.startswith('/pagead'):
            jobs.remove(job)

    for job in jobs:
        if job.startswith('/pagead'):
            jobs.remove(job)

    for job in jobs:
        if job.startswith('/pagead'):
            jobs.remove(job)
            
    # add prefix
    jobs = ['https://www.indeed.com' + job for job in jobs]
            
    return jobs


def indeed_crawl(titles, locations, dirty_jobs, browser):

    # Loop locations
    for location in locations:
        # Loop titles
        for title in titles:
            deep_indeed_query(title, location, dirty_jobs, browser)

    # Clean it up
    jobs = clean_jobs(dirty_jobs)
    return jobs
    

def transform_query_for_nn(string):
    # Create a vocab and get word counts per doc
    sparse = tfidf.transform([query])
    query_dtm = pd.DataFrame(sparse.todense(), columns = tfidf.get_feature_names())
    return query_dtm


def parse(jobs):
    # instantiate texts lists
    texts = []
    
    for job in jobs:
        html = urlopen(job)
        soup = BeautifulSoup(html, 'html.parser')
        # append clean descriptions
        texts.append(soup.find_all('div', {'class':'jobsearch-jobDescriptionText'}))
        
    return texts

def clear_auto(element):
    auto_input = str(element.get_attribute("value"))
    auto_length = len(auto_input)
    # Delete everything
    for i in range(auto_length):
        element.send_keys(Keys.BACKSPACE)

def open_jobs(jobs, browser):
    # # Create new Instance of Chrome in incognito mode
    # open_browser()
    # browser = webdriver.Firefox(executable_path='../../Selenium/geckodriver')

    # # First job
    # browser.get(jobs[0])

    # Loop over the rest
    for job in jobs:
        browser = webdriver.Firefox(executable_path='../../Selenium/geckodriver')
        browser.get(job)
