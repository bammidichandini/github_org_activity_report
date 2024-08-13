import requests
import csv

# Replace these variables with your own information
ACCESS_TOKEN = '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'
ORG_NAME = 'Aanyachandini'

def get_org_repos(org_name):
    url = f'https://api.github.com/orgs/{org_name}/repos'
    headers = {'Authorization': f'token {ACCESS_TOKEN}'}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f'Error fetching repositories for organization: {response.status_code} - {response.text}')
        return []

def get_org_members(org_name):
    url = f'https://api.github.com/orgs/{org_name}/members'
    headers = {'Authorization': f'token {ACCESS_TOKEN}'}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f'Error fetching members: {response.status_code} - {response.text}')
        return []

def get_commits(repo_full_name, username):
    url = f'https://api.github.com/repos/{repo_full_name}/commits?author={username}'
    headers = {'Authorization': f'token {ACCESS_TOKEN}'}
    response = requests.get(url, headers=headers)
    print(response.json())
    if response.status_code == 200:
        return response.json()
    else:
        print(f'Error fetching commits for {repo_full_name}: {response.status_code} - {response.text}')
        return []

def get_repo_pushes(repo_full_name):
    url = f'https://api.github.com/repos/{repo_full_name}/events'
    headers = {'Authorization': f'token {ACCESS_TOKEN}'}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f'Error fetching pushes for {repo_full_name}: {response.status_code} - {response.text}')
        return []

def get_repo_pull_requests(repo_full_name):
    url = f'https://api.github.com/repos/{repo_full_name}/pulls'
    headers = {'Authorization': f'token {ACCESS_TOKEN}'}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f'Error fetching pull requests for {repo_full_name}: {response.status_code} - {response.text}')
        return []

def main():
    org_repos = get_org_repos(ORG_NAME)
    org_repo_names = {repo['full_name'] for repo in org_repos}
    print(org_repo_names)
    members = get_org_members(ORG_NAME)
    output_file = 'github_org_activity_report.csv'
    
    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = ['Repo Name', 'Owner Name', 'UserName', 'Activity Date', 'Activity Name']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for member in members:
            username = member['login']
            print(f'Processing user: {username}')
            
            # Only fetch repositories for users
            user_repos_url = f'https://api.github.com/users/{username}/repos'
            headers = {'Authorization': f'token {ACCESS_TOKEN}'}
            response = requests.get(user_repos_url, headers=headers)
            
            if response.status_code != 200:
                print(f'Error fetching repositories for {username}: {response.status_code} - {response.text}')
                continue
            
            repos = response.json()
            
            for repo in org_repos:
                repo_name = repo['name']
                repo_full_name = repo['full_name']
                print(repo_name,repo_full_name)
                
                if repo_full_name in org_repo_names:
                    owner_name = repo['owner']['login']
                    
                    # Get commits
                    commits = get_commits(repo_full_name, username)
                    for commit in commits:
                        commit_date = commit['commit']['committer']['date']
                        commit_id = commit['sha']
                        writer.writerow({
                            'Repo Name': repo_name,
                            'Owner Name': owner_name,
                            'UserName': username,
                            'Activity Date': commit_date,
                            'Activity Name': f'Commit: {commit_id}'
                        })
                    
                    # Get pushes
                    pushes = get_repo_pushes(repo_full_name)
                    for push in pushes:
                        if push['type'] == 'PushEvent':
                            push_date = push['created_at']
                            writer.writerow({
                                'Repo Name': repo_name,
                                'Owner Name': owner_name,
                                'UserName': username,
                                'Activity Date': push_date,
                                'Activity Name': 'Push'
                            })
                    
                    # Get pull requests
                    pulls = get_repo_pull_requests(repo_full_name)
                    for pull in pulls:
                        pull_date = pull['created_at']
                        pull_id = pull['id']
                        writer.writerow({
                            'Repo Name': repo_name,
                            'Owner Name': owner_name,
                            'UserName': username,
                            'Activity Date': pull_date,
                            'Activity Name': f'Pull Request: {pull_id}'
                        })

    print(f'Report generated: {output_file}')

if __name__ == "__main__":
    main()
