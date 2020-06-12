# Preparation
1. Follow any tutorial on setting up a Github page blog with Jekyll. Save the github repository url in an environment variable named 'GITHUB_BLOG_URL'
1. Set up a Notion page with a single table. You should have columns named 'title', 'categories', and 'status'. The 'categories' column should be a Multi-Select type. The 'status' column should be a Select type and contain the options 'published' and 'to publish'. Other possible options like 'revising' and 'unpublished' are optional. These posts will be ignored and will not be uploaded. Save the page url in an environment variable named 'NOTION_BLOG_URL'
1. Check your browser cookies for the Notion access token. Save it in an environment variable named 'NOTION_TOKEN'
1. Add a category page to your Github page. You should be able to link to (github page url)/categories/#(category name)

# Runnig the code
1. Write a blog post as a row in your Notion table
1. Mark the status as 'to publish' once you are ready to publish
1. run `python main.py`
1. You should have a new commit in your Github repository, and all of the 'to publish' posts should be marked as 'published'.