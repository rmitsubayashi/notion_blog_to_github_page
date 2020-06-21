from jekyll_post_formatter import JekyllEntryDetails
from jekyll_post_formatter import JekyllEntryFactory
from jekyll_post_formatter import write_to_file
from notion_entry_details import NotionEntryDetails
from image_getter import ImageGetter
from notion import settings
from typing import List
import os
import re
import urllib.request
from git import Repo

# puts the Notion data into the local Github repository, ready to publish
class LocalGithubRepoManager:
    def __init__(self, directory: str, remote_repo: str):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        local_directory = os.path.join(script_dir, 'blog' + '\\' + directory)
        self.directory = local_directory
        self._image_getter = ImageGetter(local_directory)
        self._posts_dir = local_directory + '\\' + '_posts'
        self._init_directory(remote_repo)
        self.staged_files = []
        self.unstaged_files = []

    def _init_directory(self, remote_repo: str):
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
            self._init_git(self.directory, remote_repo)
        if not os.path.exists(self._posts_dir):
            os.mkdir(self._posts_dir)

    def _init_git(self, directory: str, remote_repo: str):
        Repo.clone_from(remote_repo, directory)

    def update_local_repository(self, notion_entry_details: List[NotionEntryDetails]):
        self.staged_files.clear()
        self.unstaged_files.clear()
        for detail in notion_entry_details:
            self._image_getter.download_images_and_update_file_name(detail)
        self. _stage_and_unstage_images(notion_entry_details)
        files_by_id = self._get_local_files_by_id()
        factory = JekyllEntryFactory()
        for detail in notion_entry_details:
            post = factory.from_notion_entry_details(detail)
            if detail.notion_id in files_by_id:
                self._unstage_old_and_stage_new_post(
                    files_by_id[detail.notion_id], post
                )
            else:
                self._stage_new_post(post)

    def _stage_and_unstage_images(self, details: List[NotionEntryDetails]):
        image_url_map = {}
        for detail in details:
            for url in detail.image_urls:
                image_url_map[url] = True
            for file_name in os.listdir(self._image_getter.asset_dir + '\\' + detail.notion_id):
                # TODO only upload different images (need to identify duplicate images)
                comparable_file_name = self._image_getter._format_local_image_path(file_name, detail.notion_id)
                if comparable_file_name not in image_url_map:
                    image_url_map[comparable_file_name] = False

        for image_url, should_add in image_url_map.items():
            url = image_url.replace(self.directory+'\\', '')
            if should_add:
                self.staged_files.append(url)
            else:
                self.unstaged_files.append(url)
                os.remove(image_url)

    def _get_local_files_by_id(self):
        id_file_name_dict = {}
        factory = JekyllEntryFactory()
        for file_name in os.listdir(self._posts_dir):
            path = self._posts_dir + '\\' + file_name
            post = factory.from_file_path(path)
            id_file_name_dict[post.unique_id] = path
        return id_file_name_dict

    def _unstage_old_and_stage_new_post(self, old_file_path: str, new_post: JekyllEntryDetails):
        old_post = JekyllEntryFactory().from_file_path(old_file_path)
        self._set_new_post_date_to_old_post_date(old_post, new_post)
        
        os.remove(old_file_path)
        if old_post.title != new_post.title:
            self.unstaged_files.append(old_file_path.replace(self.directory+'\\', ''))
        self._stage_new_post(new_post)

    def _set_new_post_date_to_old_post_date(self, old_post: JekyllEntryDetails, new_post: JekyllEntryDetails):
        new_post.date = old_post.date

    def _stage_new_post(self, new_post: JekyllEntryDetails):
        file_name = write_to_file(new_post, self._posts_dir)
        self.staged_files.append(file_name.replace(self.directory+'\\', ''))
