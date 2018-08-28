from __future__ import print_function
import requests, json
from datetime import datetime
from dateutil.parser import parse

def repos_list(git_api_url, org_name, api_user, token):
    
    """
    Lists all repositories of the given org
    Returns the list of repository names
    """

    url = git_api_url + "/user" + "/repos"

    #print("List URL: " + url)
    #print("User: " + api_user)
    #print("Token: " + token)

    #s = requests.Session()
    #s.headers.update({'access_token': token})

    tokenHeader = {'Authorization': 'token %s' % token}
    req = requests.get(url, headers=tokenHeader)  
    
    if req.status_code == 200:

        data = req.json()
        repoList = []
        for currentRepo in data:
            repoName = currentRepo["name"]
            repoList.append(repoName)

        return repoList
    else:
        print("Repo List Error Code: {} ".format(req.status_code))
        raise SystemExit


def pulls_list(git_api_url, org_name, repo_name, api_user, token):
    
    """
    Lists all open pull requests on a given repository
    Returns a list of tuples containing some information for each pull request
    """
    url = git_api_url + "/repos/" + org_name + "/" + repo_name + "/pulls?state=all"
    print("List URL: " + url)

    tokenHeader = {'Authorization': 'token %s' % token}
    req = requests.get(url, headers=tokenHeader)

    if req.status_code == 200:

        data = req.json()

        pullRequests=[]
        for currentPull in data:

            pull_id = currentPull["id"]
            title = currentPull["title"]
            login = currentPull["user"]["login"]
            #creation_date = datetime.strptime(currentPull["created_at"], '%Y-%m-%dT%H:%M:%SZ')
            creation_date = parse(currentPull["created_at"])
            html_url= currentPull["html_url"]
            state = currentPull["state"]

            pullRequests.append((repo_name, pull_id, title, login, creation_date, html_url, state));

        return pullRequests
    else:
        print("GIT Pulls List Error Code: {}".format(req.status_code))
        raise SystemExit


def post_to_slack(pull_requests, slack_webhook):
    
    """
    Posts the list of open pull requests provided to the slack thread
    """
    target_state='open'
    for current_request in pull_requests:
        if current_request[6] == target_state :
                slack_data = {'text': 'Lambda User: ' + current_request[3] + "\n" + current_request[2] + ": " + current_request[6] + "\n" + current_request[5] + "\n\n"}
                
                response = requests.post(slack_webhook, data=json.dumps(slack_data), headers={'Content-Type': 'application/json'})

                if response.status_code != 200:
                        raise ValueError('Request to slack returned an error %s, the response is:\n%s' % (response.status_code, response.text))

def post_to_chime(pull_requests, chime_webhook):

    """
    Posts the list of open pull requests provided to the chime room
    """
    target_state='open'
    for current_request in pull_requests:
        if current_request[6] == target_state :
                chime_data = {'Content': 'Lambda User: ' + current_request[3] + "\n" + current_request[2] + ": " + current_request[6] + "\n" + current_request[5] + "\n\n"}
                response = requests.post(chime_webhook, data=json.dumps(chime_data), headers={'Content-Type': 'application/json'})

                if response.status_code != 200:
                        raise ValueError('Request to chime returned an error %s, the response is:\n%s' % (response.status_code, response.text))


def lambda_handler(event, context):
    
    api_user='ajavanshir'
    api_token='a1db8ddc40801280f6702620610d730523fa2d6c'
    git_api_url='https://api.github.com'
    org_name=event['org']
    repo_name=event['repo']
    slack_webhook='https://hooks.slack.com/services/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'
    chime_webhook='https://hooks.chime.aws/incomingwebhooks/40f050db-fc26-49ae-aebd-c9cb6ab353f8?token=UzRPRm1Wdkd8MXxhUDZub2c2WFloQmFsNi1laS11X1hBNERfN2FwRTBicG14MHhSU0pQRTBJ'


    repoList = repos_list(git_api_url, org_name, api_user, api_token)
    #print(repoList)

    for repo in repoList:
        pullRequests = pulls_list(git_api_url, org_name, repo, api_user, api_token)
        if len(pullRequests) > 0:
            post_to_slack(pullRequests, slack_webhook)
            post_to_chime(pullRequests, chime_webhook)


if __name__ == '__main__':
    event = {'org': 'ajavanshir', 'repo': 'git-to-slack'}
    lambda_handler(event, 'context')