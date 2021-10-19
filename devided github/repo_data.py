import mysql.connector
import requests
import os
import datetime
from bs4 import BeautifulSoup
import time
connection = mysql.connector.connect(host='localhost',
                                     user='root',
                                     password='password',
                                     database='gitdata',)

cursor = connection.cursor(buffered=True)
# user name--------------------------------------------------------------------------
token = os.getenv('GITHUB_TOKEN', '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')
params = {}
headers = {'Authorization': f'token {token}'}


# total_commit of repos
def total_commit_fetch_web_scrap(repo_name, username):
    html = requests.get('https://github.com/'+username + '/'+repo_name).text
    soup = BeautifulSoup(html, 'html.parser')

    total_commit = soup.select_one(
        'svg.octicon.octicon-history + span strong').text
    total_commit = total_commit.replace(",", "")
    return total_commit



# total_commit commit_by_user ---------------------------------------------------
def total_commit_user_func(repo_name, username):
    commit_by_user = 0
    url = "https://api.github.com/repos/"+username+"/"+repo_name+"/commits"
    page_no = 1
    while (True):
        response = requests.get(url, headers=headers, params={
                                "author": username, "per_page": 100})
        response = response.json()
        commit_by_user = len(response)+commit_by_user
        commit_by_user_fetched = len(response)
        if (commit_by_user_fetched == 100):
            page_no = page_no + 1
            url = url + '?page=' + str(page_no)
        else:
            break
    return commit_by_user



# total_contributors--------------------------------------------------------------
def total_contributors_func(repo_name, username):
    total_contributors = 0
    url = "https://api.github.com/repos/"+username+"/"+repo_name+"/contributors"
    page_no = 1
    while (True):
        response = requests.get(url, headers=headers, params={"per_page": 100})
        response = response.json()
        total_contributors = len(response)+total_contributors
        contributors_fetched = len(response)
        if (contributors_fetched == 100):
            page_no = page_no + 1
            url = url + \
                '?page=' + str(page_no)
        else:
            break
    return total_contributors



#fetch language_dict ---------------------------------------------------------------------------------
def fetch_language(username, repo_name, language_dict):
    languae_array = [None, None, None, None, None, None, None]
    url = "https://api.github.com/repos/"+username+"/"+repo_name+"/languages"
    language_url = requests.get(
        url, headers=headers, params=params)
    count = 0
    for language in language_url.json():
        if (count <= 6):
            languae_array[count] = language
            count = count + 1
    language_dict['languages1'] = str(languae_array[0])
    language_dict['languages2'] = str(languae_array[1])
    language_dict['languages3'] = str(languae_array[2])
    language_dict['languages4'] = str(languae_array[3])
    language_dict['languages5'] = str(languae_array[4])
    language_dict['languages6'] = str(languae_array[5])
    language_dict['languages7'] = str(languae_array[6])



#main function-----------------------------------------------------------------------------------
def getRepos():
    total_commit_all_repos = 0
    cursor.execute("select repo_name,github_id from user_repo WHERE Processed = 'N'")
    for repo in cursor:
        cursor2 = connection.cursor()
        username = repo[1]
        repo_name = repo[0]
        
        total_commit = total_commit_fetch_web_scrap(repo_name, username)
        total_commit_user = total_commit_user_func(repo_name, username)
        total_contributors = total_contributors_func(repo_name, username)
        total_commit_all_repos = total_commit_all_repos + int(total_commit_user)

        language_dict = {}
        fetch_language(username, repo_name, language_dict)

        sql = "UPDATE user_repo SET contributors=%s, total_commits=%s, commit_by_user=%s, language_1=%s, language_2=%s, language_3=%s, language_4=%s, language_5=%s, language_6=%s, language_7=%s, Processed=%s  WHERE repo_name=%s AND github_id=%s"
        val = (total_contributors, total_commit, total_commit_user, language_dict['languages1'], language_dict['languages2'], language_dict['languages3'],
               language_dict['languages4'], language_dict['languages5'], language_dict['languages6'], language_dict['languages7'],"Y",repo_name, username)
        cursor2.execute(sql,val)
    sql = "UPDATE initialdetails SET total_commits=%s WHERE github_id=%s "
    cursor2.execute(sql,(total_commit_all_repos, username))

    connection.commit()


getRepos()
print("DONE ")
