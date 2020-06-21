from notion_entry_details import NotionEntryDetails
from notion import settings
from typing import List
import os
import re
import urllib.request

# gets images from Notion and saves it in the Github local repository
class ImageGetter:
    def __init__(self, local_directory):
        self._local_directory = local_directory
        self.asset_dir = local_directory + '\\' + 'assets'

    def download_images_and_update_file_name(self, notion_entry_details: NotionEntryDetails):
        self._make_asset_directory(notion_entry_details.notion_id)
        # download before formatting (formatting first makes the images inaccessible by url)
        self._download_images(notion_entry_details)
        self._format_image_urls(notion_entry_details)

    # assumes the repository is cloned already
    def _make_asset_directory(self, notion_id: str):
        if not os.path.exists(self.asset_dir):
            os.mkdir(self.asset_dir)
        if not os.path.exists(self.asset_dir + '\\' + notion_id):
            os.mkdir(self.asset_dir + '\\' + notion_id)

    def _download_images(self, detail_list: List[NotionEntryDetails]):
        for detail in detail_list:
            self._make_asset_directory(detail.notion_id)
            for url in detail.image_urls:
                image_name = self._extract_image_name(url, detail.notion_id)
                to_save_path = self._format_local_image_path(image_name, detail.notion_id)
                urllib.request.urlretrieve(url, to_save_path)

    # formats the content and the urls. the urls will be what we save in the local repository, 
    # the content will be what Jekyll uses to identify the image
    def _format_image_urls(self, detail_list: List[NotionEntryDetails]):
        for detail in detail_list:
            new_urls = []
            for original_url in detail.image_urls:
                image_name = self._extract_image_name(original_url, detail.notion_id)
                content_with_removed_image_signature = self._remove_image_signature_from_markdown(detail.content, image_name)
                content_with_jekyll_image_directory_path = self._set_jekyll_image_directory_path_in_markdown(
                    content_with_removed_image_signature, detail.notion_id, image_name
                )
                detail.content = content_with_jekyll_image_directory_path
                new_urls.append(self._format_local_image_path(image_name, detail.notion_id))
            detail.image_urls = new_urls
    
    def _extract_image_name(self, url: str, notion_id: str) -> str:
        prefix = settings.S3_URL_PREFIX_ENCODED
        url_without_prefix = url.replace(prefix, "")
        image_name_search = re.search(r'\/(.*)\?', url_without_prefix)
        image_name = image_name_search.group(1)
        return image_name

    def _remove_image_signature_from_markdown(self, content: str, image_name: str) -> str:
        return re.sub(r'\[\]\((.*'+image_name+r'.*)\)', '[]('+image_name+')', content)

    #jekyll has a different file path as the local directory
    def _set_jekyll_image_directory_path_in_markdown(self, content: str, notion_id: str, image_name: str) -> str:
        jekyll_asset_dir = self.asset_dir.replace(self._local_directory, '')
        content_image_url = '{{site.baseurl}}' + jekyll_asset_dir + '/' + notion_id + '/' + image_name
        return content.replace(image_name, content_image_url)


    def _format_local_image_path(self, image_name: str, notion_id: str) -> str:
        return self.asset_dir + '\\' + notion_id + '\\' + image_name
