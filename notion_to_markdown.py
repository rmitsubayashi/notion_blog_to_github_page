import notion.block as notion_block
from notion_entry_details import NotionEntryDetails

def convert_notion_to_markdown(notion_block: NotionEntryDetails) -> str:
    return _convert_notion_to_markdown_recusively(notion_block)

def _convert_notion_to_markdown_recusively(block):
    # leaf node
    if len(block.children) == 0:
        return _convert_block_to_markdown(block)
    markdown = ""
    # parse leaf nodes first
    for child in block.children:
        markdown += _convert_notion_to_markdown_recusively(child) + '\n\n'
    return markdown

def _convert_block_to_markdown(block):
    if isinstance(block, notion_block.ImageBlock):
        # note that this is not formatted for Jekyll yet.
        # returns the url AWS uses (lots of hashes and extra info.. ).
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