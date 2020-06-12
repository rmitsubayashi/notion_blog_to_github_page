import unittest
import os
from datetime import datetime
from github_post import GithubPost
from github_post import GithubPostFactory

class GithubPostTests(unittest.TestCase):
    def test_file_to_post(self):
        post = GithubPostFactory().from_file_path('test/github_post.md')
        self.assertEqual('this is the title', post.title)
        self.assertEqual(25, post.date.day)
        self.assertEqual('unique id', post.unique_id)
        self.assertEqual('blah', post.content)
        self.assertEqual(['jekyll','update'], post.categories)

    def test_post_to_file(self):
        file_path = 'test/2000-10-10-title.md'
        self.assertFalse(os.path.exists(file_path))

        post = GithubPost('title', datetime(2000,10,10,10,0,0), 'unique id', ['jekyll','update'],'content')
        post.write_to_file('test')

        self.assertTrue(os.path.exists(file_path))
        f = open(file_path, 'r')
        content = f.read()
        f.close()
        self.assertEqual('---\nlayout: post\ntitle: "title"\ndate: 2000-10-10 10:00:00 \ncategories: jekyll update\nid: "unique id"\n---\n' +
            '{% if post %}\n{% assign categories = post.categories %}\n{% else %}\n{% assign categories = page.categories %}\n{% endif %}\n' +
            '{% for category in categories %}\n<a href="{{site.baseurl}}/categories/#{{category|slugize}}" style="float: right; margin-left: 4px;">{{category}}</a>\n' +
            '{% endfor %}\n<br>\ncontent', content)

        #clean up
        os.remove(file_path)


if __name__ == '__main__':
    unittest.main()