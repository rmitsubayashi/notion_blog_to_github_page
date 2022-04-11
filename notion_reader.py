from notion.settings import BASE_URL
from notion_repo import NotionRepo
from notion_entry_details import NotionEntryDetails
import notion_to_markdown as md

class NotionReader:
    def __init__(self, token):
        self._notion_repo = NotionRepo(token)

    def get_title(self, notion_link):
        return self._notion_repo.get_title(notion_link)


    def get_entries_to_update(self, notion_link):
        entry_blocks = self._get_entry_blocks_to_update(notion_link)
        entries = []
        for block in entry_blocks:
            content_blocks = self._notion_repo.get_link_content(block.id)
            content = md.convert_notion_to_markdown(content_blocks)
            entry = self._map_notion_block_to_entry_class(content_blocks, block, content, block.id)
            entries.append(entry)
        return entries

    def _get_entry_blocks_to_update(self, notion_link):
        table_items = self._notion_repo.get_table_items(notion_link)
        return self._keep_only_to_publish_entry_blocks(table_items)

    def _keep_only_to_publish_entry_blocks(self, all_entries):
        to_keep = []
        for entry in all_entries:
            if entry.properties.status.select.name == 'to publish':
                to_keep.append(entry)
        return to_keep

    def _map_notion_block_to_entry_class(self, content_blocks, notion_block, content, block_id):
        title = notion_block.properties.title.title[0].plain_text
        categories = map(lambda selection: selection.name, notion_block.properties.categories.multi_select)
        image_urls = self._get_image_urls_in_block(content_blocks)
        return NotionEntryDetails(block_id, title, categories, content, image_urls)

    

    def _get_image_urls_in_block(self, notion_block):
        urls = []
        for child in notion_block:
            if child.type == "image":
                url = child.image.file.url
                urls.append(url)
        return urls
