from notion_repo import NotionRepo

# the writer depending on the reader doesn't sound right,
# but couldn't think of an alternative

class NotionWriter:
    def __init__(self, token: str):
        self._notion_repo = NotionRepo(token)

    def update_notion_entries_after_publishing(self, entries):
        for entry in entries:
            self._notion_repo.update_status_to_published(entry.notion_id)
            print('Marked ' + entry.title + ' as published')