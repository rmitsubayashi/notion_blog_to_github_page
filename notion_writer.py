from notion_reader import NotionReader

# the writer depending on the reader doesn't sound right,
# but couldn't think of an alternative

class NotionWriter:
    def __init__(self, token: str):
        self.reader = NotionReader(token)

    def update_notion_entries_after_publishing(self, notion_link):
        all_entries = self.reader._get_entry_blocks_to_update(notion_link)
        for block in all_entries:
            block.status = 'published'
            print('Marked ' + block.title + ' as published')