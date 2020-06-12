from notion.client import NotionClient

class NotionRepo:
    def __init__(self, oauth_token):
        self._client = NotionClient(token_v2=oauth_token)

    def get_block(self, notion_link):
        return self._client.get_block(notion_link)
