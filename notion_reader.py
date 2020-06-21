import notion.block as notion_block
from notion.settings import BASE_URL
from notion_repo import NotionRepo
from notion_entry_details import NotionEntryDetails
import notion_to_markdown as md

class NotionReader:
    def __init__(self, token):
        self._notion_repo = NotionRepo(token)

    def get_title(self, notion_link):
        return self._notion_repo.get_block(notion_link).title

    def get_entries_to_update(self, notion_link):
        entry_blocks = self._get_entry_blocks_to_update(notion_link)
        entries = []
        for block in entry_blocks:
            entry = self._map_notion_block_to_entry_class(block)
            entries.append(entry)
        return entries

    def _get_entry_blocks_to_update(self, notion_link):
        # assumes the entries are in a page with only that table.
        collection_block = self._notion_repo.get_block(notion_link).children[0]
        all_blocks = collection_block.collection.get_rows()
        return self._keep_only_to_publish_entry_blocks(all_blocks)

    def _keep_only_to_publish_entry_blocks(self, all_entries):
        to_keep = []
        for entry in all_entries:
            if entry.status == 'to publish':
                to_keep.append(entry)
        return to_keep

    def _map_notion_block_to_entry_class(self, notion_block):
        title = notion_block.title
        categories = notion_block.categories
        content = md.convert_notion_to_markdown(notion_block)
        image_urls = self._get_image_urls_in_block(notion_block)
        url_with_notion_id = notion_block.get_browseable_url()
        notion_id = url_with_notion_id.replace(BASE_URL, "")
        return NotionEntryDetails(notion_id, title, categories, content, image_urls)

    

    def _get_image_urls_in_block(self, notion_entry):
        children = notion_entry.children
        urls = []
        for child in children:
            if isinstance(child, notion_block.ImageBlock):
                url = child.display_source
                urls.append(url)
        return urls
