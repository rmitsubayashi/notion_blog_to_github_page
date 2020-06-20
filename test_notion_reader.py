import unittest
from notion_entry_details import NotionEntryDetails
from notion_reader import NotionReader
import os

class NotionReaderTests(unittest.TestCase):
    def test_filter_status(self):
        token = os.environ.get('NOTION_TOKEN')
        notion_reader = NotionReader(token)
        entries = notion_reader.get_entries_to_update("https://www.notion.so/Filter-Status-45b97981608f4ce6a36091172b962439")
        self.assertEqual(1,len(entries))
    
    def test_download_image(self):
        self.assertEqual(1,1)

    def test_markdown(self):
        expected = NotionEntryDetails(
            "93812fac65a14d1eb9033ece651ef2b3",
            "title",
            ["fuga"],
            "# h1\n\n## h2\n\n### h3\n\n- bullet\n\n1. one\n\n**bold** text\n\n[facebook](https://www.facebook.com/) link\n\n",
            []
        )
        token = os.environ.get('NOTION_TOKEN')
        notion_reader = NotionReader(token)
        entries = notion_reader.get_entries_to_update("https://www.notion.so/Markdown-70e076df8367476b820f9c5d5b9d2c84")
        self.assertEqual(expected.__dict__, entries[0].__dict__)

if __name__ == '__main__':
    unittest.main()