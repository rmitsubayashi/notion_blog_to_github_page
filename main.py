from notion_reader import NotionReader
from notion_writer import NotionWriter
from notion_to_github_repo_converter import NotionToGithubRepoConverter
from github_publisher import GithubPublisher

import os

token = os.environ.get('NOTION_TOKEN')
notion_reader = NotionReader(token)
notion_blog_url = os.environ.get('NOTION_BLOG_URL')
entries = notion_reader.get_entries_to_update(notion_blog_url)
print(str(len(entries)) + ' entries to update')
blog_title = notion_reader.get_title(notion_blog_url)
github_blog_url = os.environ.get('GITHUB_BLOG_URL')
notion_to_github_repo_converter = NotionToGithubRepoConverter(blog_title, github_blog_url)
notion_to_github_repo_converter.update_local_repository(entries)
print("Staging:")
for f in notion_to_github_repo_converter.staged_files:
    print(f)
print("Unstaging:")
for f in notion_to_github_repo_converter.unstaged_files:
    print(f)
    
if len(notion_to_github_repo_converter.staged_files) + len(notion_to_github_repo_converter.unstaged_files) > 0: 
    github_publisher = GithubPublisher(github_blog_url)
    success = github_publisher.publish(
        notion_to_github_repo_converter.directory,
        notion_to_github_repo_converter.staged_files,
        notion_to_github_repo_converter.unstaged_files
    )

    if success:
        notion_writer = NotionWriter(token)
        notion_writer.update_notion_entries_after_publishing(notion_blog_url)
    else:
        print("could not push to github")