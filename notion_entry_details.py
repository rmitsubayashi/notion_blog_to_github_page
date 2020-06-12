class NotionEntryDetails:
    def __init__(self, notion_id, title, categories, content, image_urls):
        self.notion_id = notion_id
        self.title = title
        self.categories = categories
        self.content = content
        self.image_urls = image_urls