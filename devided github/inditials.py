import mysql.connector
import requests
import os
import datetime
from bs4 import BeautifulSoup
import time
start_time = time.time()
#2 files banegi   1st = initial detail and repo name 
#2nd = repo data
# Connect to the database
connection = mysql.connector.connect(host='localhost',
                                     user='root',
                                     password='password',
                                     database='gitdata',)

cursor = connection.cursor()
#user name--------------------------------------------------------------------------
username = 'plamber'
#-----------------------------------------------------------------------------------
token = os.getenv('GITHUB_TOKEN', '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')
params = {}
headers = {'Authorization': f'token {token}'}
data = requests.get('https://api.github.com/users/' + username, headers=headers, params=params)
data = data.json()



def total_stars(username):
    try:
        html = requests.get('https://github.com/'+username ).text
        soup = BeautifulSoup(html, 'html.parser')
        total_commit = soup.select_one('#js-pjax-container div.container-xl.px-3.px-md-4.px-lg-5 div div.flex-shrink-0.col-12.col-md-3.mb-4.mb-md-0 div div.js-profile-editable-replace div.d-flex.flex-column div.js-profile-editable-area.d-flex.flex-column.d-md-block div.flex-order-1.flex-md-order-none.mt-2.mt-md-0 div a:nth-child(3) span').text
        return (total_commit)
    except:
        return (0)

def getUser(username,data):
    initial_details = {}
    initial_details['username'] = username
    initial_details['name'] = data['name']
    initial_details['email'] = data['email']
    initial_details['id'] = data['id']
    initial_details['location'] = data['location']
    initial_details['followers'] = data['followers']
    initial_details['following'] = data['following']
    initial_details['total_stars'] = total_stars(username)
    initial_details['total_repos'] = data['public_repos']
    d1 = datetime.datetime.strptime(data['created_at'], "%Y-%m-%dT%H:%M:%SZ")
    new_format = "%Y-%m-%d"
    d1.strftime(new_format)
    d1.date()
    initial_details['created_at'] = d1


    url = data['repos_url']
    page_no = 1
    repos_data = []
    while (True):
        response = requests.get(url, headers=headers, params={"per_page": 100})
        response = response.json()
        repos_data = repos_data + response
        repos_fetched = len(response)
        if (repos_fetched == 100):
            page_no = page_no + 1
            url = data['repos_url'] + '?page=' + str(page_no)
        else:
            break


    all_repo_data = {}
    for repo in (repos_data):
        all_repo_data[(repo['name'])] = {}
        all_repo_data[(repo['name'])]['name'] = (repo['name'])
        all_repo_data[(repo['name'])]['id'] = (repo['id'])
        all_repo_data[(repo['name'])]['stars'] = repo['stargazers_count']
        all_repo_data[(repo['name'])]['created_at'] = repo['created_at']
        all_repo_data[(repo['name'])]['updated_at'] = repo['updated_at']
        all_repo_data[(repo['name'])]['description'] = repo['description']
        
        if(repo['fork'] == True):
            all_repo_data[(repo['name'])]['owner'] = "False"
        else:
            all_repo_data[(repo['name'])]['owner'] = "True"

        d1 = datetime.datetime.strptime(all_repo_data[(repo['name'])]['updated_at'], "%Y-%m-%dT%H:%M:%SZ")
        d2 = datetime.datetime.strptime(all_repo_data[(repo['name'])]['created_at'], "%Y-%m-%dT%H:%M:%SZ")
        new_format = "%Y-%m-%d"
        d1.strftime(new_format)
        d2.strftime(new_format)
        d1.date()
        d2.date()
        all_repo_data[(repo['name'])]['created_at'] = d2
        all_repo_data[(repo['name'])]['updated_at'] = d1




    #insert repo data ---------------------------------------------------------------------------------
    for repo in all_repo_data:
        sql = "INSERT INTO user_repo (user_id, github_id, repo_id, user_connection, repo_name,Processed,commit_processed,created_date,last_commit,description,stars) VALUES (  %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(sql, (
            initial_details['id'],
            username,
            all_repo_data[repo]['id'],
            all_repo_data[(repo)]['owner'],
            all_repo_data[(repo)]['name'],
            'N',
            'N',
            all_repo_data[(repo)]['created_at'],
            all_repo_data[(repo)]['updated_at'],
            all_repo_data[(repo)]['description'],
            all_repo_data[(repo)]['stars']
        ))


    # Insert newinitial  userdeta   ---------------------------------------------------------------------
    sql = "INSERT INTO initialdetails (github_id, name, email, user_id, location, followers, following,total_stars,total_repos,git_create_date) VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    cursor.execute(sql, (initial_details['username'],
                         initial_details['name'],
                         initial_details['email'],
                         initial_details['id'],
                         initial_details['location'],
                         initial_details['followers'],
                         initial_details['following'],
                         initial_details['total_stars'],
                         initial_details['total_repos'],
                         initial_details['created_at']
                         ))
    connection.commit()
    print("User details inserted")


getUser(username, data)

