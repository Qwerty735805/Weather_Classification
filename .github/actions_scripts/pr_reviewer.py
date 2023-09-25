from github import Github
import os
import difflib
import json
import openai


class ChatApp:
    def __init__(self):
        # Setting the API key to use the OpenAI API
        openai.api_key = os.getenv("OPENAI_TOKEN")
        self.messages = [
            {"role": "system", "content": """
        Given a 'diff' file produced by the difflib Python library, representing the differences between two codebases involved in a pull request (PR),  your task is to conduct a meticulous review, identify the changes made, and then articulate these transformations in a manner that would simplify the review process for others. Your objective is to illuminate the differences, particularly in the context of any complex changes, using code snippets to clarify what the code looked like before the modification and what it looks like post-change.
        
        Your response should specifically encompass:
            Interpreting Code Difference: Read and interpret the diff file, identifying the specific lines of code that have been added, altered or removed.
        
            Detailing Changes: Explain the changes made in each file or module clearly and thoroughly. This is particularly important when the changes are complex, and greater clarity is required.
        
            Before-and-After Comparison: Using the information in the diff file, create a 'before' and 'after' code snippet comparison for the major changes. This should illustrate how the codebase transformed due to the proposed changes.
        
            Summary of Changes: Provide a high-level summary of the changes identified, alongside detailing the implications of these transformations.
        
        The evaluation and explanation should be clear, comprehensive, and accessible, facilitating an easier understanding of the changes made in the PR.
"""},
        ]

    def chat(self, message):
        self.messages.append({"role": "user", "content": message})
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=self.messages
        )
        self.messages.append({"role": "assistant", "content": response["choices"][0]["message"].content})
        return response["choices"][0]["message"]
    

# Ensure to put your own GitHub token here.
g = Github(os.getenv("GITHUB_TOKEN"))

repo = g.get_repo(os.getenv("GITHUB_REPOSITORY"))

with open(os.getenv("GITHUB_EVENT_PATH")) as event_file:
    event = json.load(event_file)

pr_number = event["pull_request"]["number"]  # Get the PR number from the event payload
pr = repo.get_pull(pr_number)
# pr = repmao.get_pull(os.getenv("GITHUB_REF").split('/')[-1])

base = pr.base.ref
head = pr.head.ref


for file in pr.get_files():
    try:
        with open(file.filename, 'r') as changed_file:
            changed_content = changed_file.read().splitlines()

        base_content = repo.get_contents(file.filename, ref=base).decoded_content.decode().splitlines()

        diff = difflib.context_diff(base_content, changed_content, fromfile=base, tofile=head)
        diff = '\n'.join(diff)

        sample_message='''Using the below diff 
         ''' + diff

        chatgpt=ChatApp()
        output=chatgpt.chat(sample_message)
        print(output['content'])        
    
    except Exception as e:
        print(f"Could not compare file: {file.filename}. Reason: {str(e)}")
