import mysql.connector
import requests
import os
import datetime
from bs4 import BeautifulSoup

# Connect to the database
connection = mysql.connector.connect(host='localhost',
                                     user='root',
                                     password='password',
                                     database='gitdata',)

cursor = connection.cursor(buffered=True)
#user name--------------------------------------------------------------------------
token = os.getenv('GITHUB_TOKEN', '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')
params = {}
headers = {'Authorization': f'token {token}'}


def commit_dates():
    cursor.execute("select user_id,github_id,repo_id,repo_name from user_repo WHERE commit_processed = 'N' ")
    for repo in cursor:
        cursor2 = connection.cursor()
        user_id = repo[0]
        github_id = repo[1]
        repo_id = repo[2]
        repo_name = repo[3]
        print("data for --- ",user_id, github_id, repo_name,repo_id)
        url = "https://api.github.com/repos/"+github_id+"/"+repo_name+"/commits"
        page_no = 1
        while (True):
            response = requests.get(url, headers=headers, params={"per_page": 100, "author": github_id})
            response = response.json()
            for commits in response:
                d1 = datetime.datetime.strptime(commits['commit']['author']['date'], "%Y-%m-%dT%H:%M:%SZ")
                new_format = "%Y-%m-%d"
                d1 = d1.strftime(new_format)
                sql = "INSERT INTO commits_details (user_id, github_id, repo_id, repo_name, commit_date) VALUES (  %s, %s, %s, %s, %s)"
                cursor2.execute(sql, ( user_id,github_id,repo_id,repo_name, d1,))
            connection.commit()
            commit_fetched = len(response)
            if (commit_fetched == 100):
                page_no = page_no + 1
                url = url + '?page=' + str(page_no)
            else:
                break
        sql = "UPDATE user_repo SET commit_processed=%s  WHERE repo_name=%s AND github_id=%s"
        val = ("Y", repo_name, github_id)
        cursor2.execute(sql, val)
    connection.commit()


commit_dates()
