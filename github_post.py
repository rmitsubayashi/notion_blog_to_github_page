from datetime import datetime, timedelta, timezone
import re
from notion_entry_details import NotionEntryDetails

class GithubPost:
    def __init__(self, title, date, unique_id, categories, content):
        self.title = title
        self.date = date
        self.unique_id = unique_id
        self.categories = categories
        self.content = content

    def write_to_file(self, directory: str):
        file_content = '---\nlayout: post\n'
        file_content += 'title: "' + self.title + '"\n'
        # 2019-10-25 11:22:31 +0900
        date_str = self.date.strftime('%Y-%m-%d %H:%M:%S %z')
        file_content += 'date: ' + date_str + '\n'
        file_content += 'categories: ' + ' '.join(self.categories) + '\n'
        file_content += 'id: "' + self.unique_id + '"\n'
        file_content += '---\n'
        # links to category page
        file_content += '{% if post %}\n'
        file_content += '{% assign categories = post.categories %}\n'
        file_content += '{% else %}\n'
        file_content += '{% assign categories = page.categories %}\n'
        file_content += '{% endif %}\n'
        file_content += '{% for category in categories %}\n'
        file_content += '<a href="{{site.baseurl}}/categories/#{{category|slugize}}" style="float: right; margin-left: 4px;">{{category}}</a>\n'
        file_content += '{% endfor %}\n'
        file_content += '<br>\n'

        file_content += self.content

        file_name_date = self.date.strftime('%Y-%m-%d')
        title_for_file_name = self.title.replace(' ', '-')
        file_name = directory + '\\' + file_name_date + '-' + title_for_file_name + '.md'

        with open(file_name, 'w', encoding='utf-8') as f:
            f.write(file_content)

        return file_name


class GithubPostFactory:
    def from_file_path(self, file_path: str) -> GithubPost:
        f = open(file_path, 'r', encoding='utf-8')
        f.readline() # ---
        f.readline() # layout: post
        title_line = f.readline() # title: "title"
        search_title = re.search(r'title: "(.*)"', title_line)
        title = search_title.group(1)
        date_line = f.readline() #date: 2019-10-25 11:22:31 +0900
        search_date = re.search(r'date: (.*)', date_line)
        date_str = search_date.group(1)
        date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S %z')
        category_line = f.readline() # categories: jekyll update
        search_categories = re.search(r'categories: (.*)', category_line)
        categories = search_categories.group(1).split(' ')
        id_line = f.readline() # id: "id"
        search_id = re.search(r'id: "(.*)"', id_line)
        id = search_id.group(1)
        f.readline() # ---
        for _ in range(9):
            f.readline() # display category code
        content = f.read() # the rest of the file
        f.close()

        return GithubPost(title, date, id, categories, content)

    # TODO the date is set to when the script runs. 
    # this technically isn't too big of a deal, just messy code with possible bugs
    def from_notion_entry_details(self, notion_entry_details: NotionEntryDetails) -> GithubPost:
        jst = timezone(timedelta(hours=+9), 'JST')
        return GithubPost(notion_entry_details.title, datetime.now(jst), notion_entry_details.notion_id, notion_entry_details.categories, notion_entry_details.content)
