from notion_reader import NotionReader
from notion_writer import NotionWriter
from local_github_repo_manager import LocalGithubRepoManager
from github_publisher import GithubPublisher

import os

token = os.environ.get('NOTION_TOKEN')
notion_reader = NotionReader(token)
notion_blog_url = os.environ.get('NOTION_BLOG_URL')
entries = notion_reader.get_entries_to_update(notion_blog_url)
print(str(len(entries)) + ' entries to update')

blog_title = notion_reader.get_title(notion_blog_url)
github_blog_url = os.environ.get('GITHUB_BLOG_URL')
local_github_repo_manager = LocalGithubRepoManager(blog_title, github_blog_url)
local_github_repo_manager.update_local_repository(entries)
print("Staging:")
for f in local_github_repo_manager.staged_files:
    print(f)
print("Unstaging:")
for f in local_github_repo_manager.unstaged_files:
    print(f)
    
if len(local_github_repo_manager.staged_files) + len(local_github_repo_manager.unstaged_files) > 0: 
    github_publisher = GithubPublisher(github_blog_url)
    success = github_publisher.publish(
        local_github_repo_manager.directory,
        local_github_repo_manager.staged_files,
        local_github_repo_manager.unstaged_files
    )

    if success:
        notion_writer = NotionWriter(token)
        notion_writer.update_notion_entries_after_publishing(entries)
    else:
        print("could not push to github")