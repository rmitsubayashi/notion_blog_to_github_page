def convert_notion_to_markdown(blocks):
    markdown = ""
    for block in blocks:
        markdown += _convert_block_to_markdown(block) + "\n\n"
    return markdown

def _convert_block_to_markdown(block):
    if block.type == "heading_1":
        return "# " + _convert_rich_text_to_markdown(block.heading_1.rich_text)
    elif block.type == "heading_2":
        return "## " + _convert_rich_text_to_markdown(block.heading_2.rich_text)
    elif block.type == "heading_3":
        return "### " + _convert_rich_text_to_markdown(block.heading_3.rich_text)
    elif block.type == "bulleted_list_item":
        return "- " + _convert_rich_text_to_markdown(block.bulleted_list_item.rich_text)
    elif block.type == "numbered_list_item":
        return "1. " + _convert_rich_text_to_markdown(block.numbered_list_item.rich_text)
    elif block.type == "paragraph":
        return _convert_rich_text_to_markdown(block.paragraph.rich_text)
    elif block.type == "code":
        return "{% highlight " + block.code.language + "%}\n" + _convert_rich_text_to_markdown(block.code.rich_text) + "{% endhighlight %}"
    elif block.type == "image":
        # note that this is not formatted for Jekyll yet.
        # returns the url AWS uses (lots of hashes and extra info.. ).
        return "![](" + block.image.file.url + ")"

def _convert_rich_text_to_markdown(rich_text):
    markdown = ""
    for text_block in rich_text:
        if text_block.annotations.bold == True:
            markdown += "__" + text_block.plain_text + "__"
        elif text_block.href != None:
            markdown += "[" + text_block.plain_text + "](" + text_block.href + ")"
        else:
            markdown += text_block.plain_text
    return markdown