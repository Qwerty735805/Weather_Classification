from github import Github
import os
import difflib
import json

# Ensure to put your own GitHub token here.
g = Github(os.getenv("GITHUB_TOKEN"))

repo = g.get_repo(os.getenv("GITHUB_REPOSITORY"))

with open(os.getenv("GITHUB_EVENT_PATH")) as event_file:
    event = json.load(event_file)

pr_number = event["pull_request"]["number"]  # Get the PR number from the event payload
pr = repo.get_pull(pr_number)
# pr = repo.get_pull(os.getenv("GITHUB_REF").split('/')[-1])

base = pr.base.ref
head = pr.head.ref

for file in pr.get_files():
    try:
        with open(file.filename, 'r') as changed_file:
            changed_content = changed_file.read().splitlines()

        base_content = repo.get_contents(file.filename, ref=base).decoded_content.decode().splitlines()

        diff = difflib.context_diff(base_content, changed_content, fromfile=base, tofile=head)
        print('V-----------------------------------V')
        print('V-----------------------------------V')
        print('V-----------------------------------V')
        print(diff)
        print('^-----------------------------------^')
        print('^-----------------------------------^')
        print('^-----------------------------------^')
        
    except Exception as e:
        print(f"Could not compare file: {file.filename}. Reason: {str(e)}")
