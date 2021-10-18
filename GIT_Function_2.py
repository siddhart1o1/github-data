from mysql.connector import Error
import json
import mysql.connector
import requests
import numpy as np
import requests
import requests
from requests.auth import HTTPBasicAuth
import os
import datetime
from bs4 import BeautifulSoup
import time
start_time = time.time()

# Connect to the database
connection = mysql.connector.connect(host='localhost',
                                     user='root',
                                     password='password',
                                     database='gitdata',)

cursor = connection.cursor()


#user name--------------------------------------------------------------------------
username = 'waldekmastykarz'
#-----------------------------------------------------------------------------------
token = os.getenv('GITHUB_TOKEN', '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')
params = {}
headers = {'Authorization': f'token {token}'}
data = requests.get('https://api.github.com/users/' +
                    username, headers=headers, params=params)
data = data.json()


#initial details ----------------------------------------------------------------
initial_details = {}
initial_details['username'] = username
initial_details['name'] = data['name']
initial_details['email'] = data['email']
initial_details['id'] = data['id']
initial_details['location'] = data['location']
initial_details['followers'] = data['followers']
initial_details['following'] = data['following']
initial_details['Total_commits_of_user'] = 0
initial_details['total_repos'] = 0
initial_details['total_stars'] = 0


total_repos = 0
#total repos -------------------------------------------------------------------
def total_repo_fetch(data, total_repos, initial_details):
    url = data['repos_url']
    page_no = 1
    repos_data = []
    while (True):
        response = requests.get(url, headers=headers, params={"per_page": 100})
        response = response.json()
        repos_data = repos_data + response
        total_repos = len(response) + total_repos
        repos_fetched = len(response)
        if (repos_fetched == 100):
            page_no = page_no + 1
            url = data['repos_url'] + '?page=' + str(page_no)
        else:
            break
    initial_details['total_repos'] = total_repos
    return repos_data


#total_commit--------------------------------------------------------------------
def total_commit_fetch(all_repo_data):
    total_commit = 0
    for repo in all_repo_data:
        try:
            url = all_repo_data[(repo['name'])]['commits_url']
            print(url)

            page_no = 1
            while (True):
                response = requests.get(
                    url, headers=headers, params={"per_page": 100})
                response = response.json()
                total_commit = len(response)+total_commit
                commit_fetched = len(response)
                if (commit_fetched == 100):
                    page_no = page_no + 1
                    url = all_repo_data[(repo['name'])]['commits_url'] + \
                        '?page=' + str(page_no)
                else:
                    break
            all_repo_data[(repo['name'])]['total_commits'] = int(total_commit)
        except:
            all_repo_data[(repo['name'])]['total_commits'] = int(total_commit)



#total_commit_web_scraping--------------------------------------------------------------------
def total_commit_fetch_web_scrap(all_repo_data, username):
    for repo in all_repo_data:
        html = requests.get('https://github.com/'+username +'/'+all_repo_data[(repo)]['name']).text
        soup = BeautifulSoup(html, 'html.parser')
        
        total_commit = soup.select_one('svg.octicon.octicon-history + span strong').text
        total_commit = total_commit.replace(",", "")
        all_repo_data[(repo)]['total_commits'] = int(total_commit)


#total_commit commit_by_user ---------------------------------------------------
def total_commit_user(all_repo_data, initial_details):
    for repo in all_repo_data:
        commit_by_user = 0
        
        url = all_repo_data[(repo)]['commits_url']
        page_no = 1
        while (True):
            response = requests.get(url, headers=headers, params={
                                    "author": username, "per_page": 100})
            response = response.json()
            commit_by_user = len(response)+commit_by_user
            commit_by_user_fetched = len(response)
            if (commit_by_user_fetched == 100):
                page_no = page_no + 1
                url = all_repo_data[(repo)]['commits_url'] + \
                    '?page=' + str(page_no)
            else:
                break
        all_repo_data[(repo)]['commit_by_user'] = commit_by_user
    initial_details['Total_commits_of_user'] = commit_by_user + \
            initial_details['Total_commits_of_user']


#total_contributors--------------------------------------------------------------
def total_contributors(all_repo_data):
    for repo in all_repo_data:
        total_contributors = 0
        url = all_repo_data[(repo)]['contributors']
        page_no = 1
        while (True):
            response = requests.get(url, headers=headers, params={"per_page": 100})
            try:
                response = response.json()
            except:
                all_repo_data[(repo)]['contributors'] = total_contributors
                return
            total_contributors = len(response)+total_contributors
            contributors_fetched = len(response)
            if (contributors_fetched == 100):
                page_no = page_no + 1
                url = all_repo_data[(repo)]['contributors'] + \
                    '?page=' + str(page_no)
            else:
                break
        all_repo_data[(repo)]['contributors'] = total_contributors


#total-language------------------------------------------------------------------
def fetch_language(all_repo_data):
    for repo in all_repo_data:
        all_repo_data[(repo)]['languages1'] = None
        all_repo_data[(repo)]['languages2'] = None
        all_repo_data[(repo)]['languages3'] = None
        all_repo_data[(repo)]['languages4'] = None
        all_repo_data[(repo)]['languages5'] = None
        all_repo_data[(repo)]['languages6'] = None
        all_repo_data[(repo)]['languages7'] = None
        languae_array = [None, None, None, None, None, None, None]
        language_url = requests.get(
            all_repo_data[(repo)]['languages'], headers=headers, params=params)

        count = 0
        for language in language_url.json():
            if (count <= 6):
                languae_array[count] = language
                count = count + 1

        all_repo_data[(repo)]['languages1'] = languae_array[0]
        all_repo_data[(repo)]['languages2'] = languae_array[1]
        all_repo_data[(repo)]['languages3'] = languae_array[2]
        all_repo_data[(repo)]['languages4'] = languae_array[3]
        all_repo_data[(repo)]['languages5'] = languae_array[4]
        all_repo_data[(repo)]['languages6'] = languae_array[5]
        all_repo_data[(repo)]['languages7'] = languae_array[6]





#get all repos info ---------------------------------------------------------------
all_repo_data = {}
def fetch_repo_info(all_repo_data, repos_data, username, initial_details):
    for repo in (repos_data):
        all_repo_data[(repo['name'])] = {}
        all_repo_data[(repo['name'])]['name'] = (repo['name'])
        all_repo_data[(repo['name'])]['id'] = (repo['id'])
        all_repo_data[(repo['name'])]['description'] = repo['description']
        all_repo_data[(repo['name'])]['created_at'] = repo['created_at']
        all_repo_data[(repo['name'])]['updated_at'] = repo['updated_at']

        if(repo['fork'] == True):
            all_repo_data[(repo['name'])]['owner'] = "False"
        else:
            all_repo_data[(repo['name'])]['owner'] = "True"

        all_repo_data[(repo['name'])]['stars'] = repo['stargazers_count']
        all_repo_data[(repo['name'])]['url'] = repo['url']
        all_repo_data[(repo['name'])]['commits_url'] = repo['commits_url'].split("{")[0]
        all_repo_data[(repo['name'])]['languages'] = (repo['url'] + '/languages')
        all_repo_data[(repo['name'])]['contributors'] = repo['contributors_url']

        #total stars---------------------------------------------------------------------------------------
        initial_details['total_stars'] = all_repo_data[(
            repo['name'])]['stars']+initial_details['total_stars']

        #corect format for date time ----------------------------------------------------------------------
        d1 = datetime.datetime.strptime(all_repo_data[(repo['name'])]['updated_at'], "%Y-%m-%dT%H:%M:%SZ")
        d2 = datetime.datetime.strptime(all_repo_data[(repo['name'])]['created_at'], "%Y-%m-%dT%H:%M:%SZ")
        new_format = "%Y-%m-%d"
        d1.strftime(new_format)
        d2.strftime(new_format)
        d1.date()
        d2.date()
        all_repo_data[(repo['name'])]['created_at'] = d2
        all_repo_data[(repo['name'])]['updated_at'] = d1





def insert_repo_data(all_repo_data, username,initial_details):
    for repo in all_repo_data:
        sql = "INSERT INTO user_repo (user_id, github_id, repo_id, user_connection, repo_name, contributors, total_commits, commit_by_user, created_date, last_commit,language_1,	language_2,	language_3,	language_4,	language_5,	language_6,	language_7) VALUES (  %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(sql, (
        initial_details['id'],
        username,
        all_repo_data[(repo)]['id'],
        all_repo_data[(repo)]['owner'],
        all_repo_data[(repo)]['name'],
        all_repo_data[(repo)]['contributors'],
        all_repo_data[(repo)]['total_commits'],
        all_repo_data[(repo)]['commit_by_user'],
        all_repo_data[(repo)]['created_at'],
        all_repo_data[(repo)]['updated_at'],
        all_repo_data[(repo)]['languages1'],
        all_repo_data[(repo)]['languages2'],
        all_repo_data[(repo)]['languages3'],
        all_repo_data[(repo)]['languages4'],
        all_repo_data[(repo)]['languages5'],
        all_repo_data[(repo)]['languages6'],
        all_repo_data[(repo)]['languages7'],
        ))


#calling functions -------------------------------------------------------------------------------------------
repos_data = total_repo_fetch(data, total_repos, initial_details)
fetch_repo_info(all_repo_data, repos_data, username, initial_details)

#total commits----------------------------------------------------------------------------------------------
# total_commit_fetch(repo,all_repo_data)
total_commit_fetch_web_scrap(all_repo_data, username)

#commit_by_user --------------------------------------------------------------------------------------------
total_commit_user(all_repo_data, initial_details)

#contributors----------------------------------------------------------------------------------------------
total_contributors(all_repo_data)

#languages--------------------------------------------------------------------------------------------------
fetch_language(all_repo_data)


insert_repo_data(all_repo_data, username,initial_details)
connection.commit()


sql = "INSERT INTO initialdetails (github_id, name, email, user_id, location, followers, following,total_commits,total_stars,total_repos) VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
cursor.execute(sql, (initial_details['username'],
                     initial_details['name'],
                     initial_details['email'],
                     initial_details['id'],
                     initial_details['location'],
                     initial_details['followers'],
                     initial_details['following'],
                     initial_details['Total_commits_of_user'],
                     initial_details['total_stars'],
                     initial_details['total_repos'],
                     ))

connection.commit()
print("--------------DONE--------------------")
print("--- %s seconds ---" % (time.time() - start_time))
