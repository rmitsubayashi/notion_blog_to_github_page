import notion.block as notion_block
from notion.settings import BASE_URL
from notion_entry_details import NotionEntryDetails

class NotionReader:
    def __init__(self, notion_repo):
        self._notion_repo = notion_repo

    def get_title(self, notion_link):
        return self._notion_repo.get_block(notion_link).title

    def get_entries_to_update(self, notion_link):
        all_entries = self._get_all_entry_blocks(notion_link)
        filtered_entry_blocks = self._keep_only_to_publish_entry_blocks(all_entries)
        entries = []
        for block in filtered_entry_blocks:
            entry = self._convert_notion_block_to_entry(block)
            entries.append(entry)
        return entries

    # assumes the entries are in a page with only that table.
    def _get_all_entry_blocks(self, notion_link):
        # bug where collection.get_rows() returns nothing
        # https://github.com/jamalex/notion-py/issues/52
        collection_block = self._notion_repo.get_block(notion_link).children[0]
        return collection_block.collection.get_rows()

    def _keep_only_to_publish_entry_blocks(self, all_entries):
        to_keep = []
        for entry in all_entries:
            if entry.status == 'to publish':
                to_keep.append(entry)
        return to_keep

    def _convert_notion_block_to_entry(self, notion_block):
        title = notion_block.title
        categories = notion_block.categories
        content = self._convert_notion_to_markdown(notion_block)
        image_urls = self._extract_images_from_notion_block(notion_block)
        url_with_notion_id = notion_block.get_browseable_url()
        notion_id = url_with_notion_id.replace(BASE_URL, "")
        return NotionEntryDetails(notion_id, title, categories, content, image_urls)

    def _convert_notion_to_markdown(self, notion_block):
        return self._convert_notion_to_markdown_recusively(notion_block)

    def _convert_notion_to_markdown_recusively(self, block):
        if len(block.children) == 0:
            return self._convert_notion_block_to_markdown(block)
        markdown = ""
        for child in block.children:
            markdown += self._convert_notion_to_markdown_recusively(child) + '\n\n'
        return markdown

    def _convert_notion_block_to_markdown(self, block):
        if isinstance(block, notion_block.ImageBlock): #not formatted for Jekyll yet
            return "![](" + block.display_source + ")"
        elif isinstance(block, notion_block.HeaderBlock):
            return "# " + block.title
        elif isinstance(block, notion_block.SubheaderBlock):
            return "## " + block.title
        elif isinstance(block, notion_block.SubsubheaderBlock):
            return "### " + block.title
        elif isinstance(block, notion_block.BulletedListBlock):
            return "- " + block.title
        elif isinstance(block, notion_block.NumberedListBlock):
            return "1. " + block.title
        elif isinstance(block, notion_block.CodeBlock):
            lang = block.language.lower()
            # Jekyll ready
            return '{% highlight ' + lang + ' %}\n' + block.title + '{% endhighlight %}'
        else:
            return block.title

    def _extract_images_from_notion_block(self, notion_entry):
        children = notion_entry.children
        urls = []
        for child in children:
            if isinstance(child, notion_block.ImageBlock):
                url = child.display_source
                urls.append(url)
                print(url)
        return urls

    def update_notion_entries_after_publishing(self, notion_link):
        all_entries = self._get_all_entry_blocks(notion_link)
        filtered_entry_blocks = self._keep_only_to_publish_entry_blocks(all_entries)
        for block in filtered_entry_blocks:
            block.status = 'published'
            print('Marked ' + block.title + ' as published')
