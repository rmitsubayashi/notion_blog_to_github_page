from github_post import GithubPost
from github_post import GithubPostFactory
from notion_entry_details import NotionEntryDetails
from notion import settings
from typing import List
import os
import re
import urllib.request
from git import Repo

class NotionToGithubRepoConverter:
    def __init__(self, directory: str, remote_repo: str):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        local_directory = os.path.join(script_dir, 'blog' + '\\' + directory)
        self.directory = local_directory
        self._asset_dir = local_directory + '\\' + 'assets'
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
        if not os.path.exists(self._asset_dir):
            os.mkdir(self._asset_dir)

    def _init_git(self, directory: str, remote_repo: str):
        Repo.clone_from(remote_repo, directory)

    def update_local_repository(self, notion_entry_details: List[NotionEntryDetails]):
        self.staged_files.clear()
        self.unstaged_files.clear()
        # download before formatting (formatting first makes the images inaccessible by url)
        self._download_images(notion_entry_details)
        self._format_image_urls(notion_entry_details)
        self._stage_and_unstage_images(notion_entry_details)
        files_by_id = self._get_local_files_by_id()
        factory = GithubPostFactory()
        for detail in notion_entry_details:
            post = factory.from_notion_entry_details(detail)
            if detail.notion_id in files_by_id:
                self._unstage_old_and_stage_new_post(
                    files_by_id[detail.notion_id], post
                )
            else:
                self._stage_new_post(post)

    def _download_images(self, detail_list: List[NotionEntryDetails]):
        for detail in detail_list:
            self._make_asset_directory(detail.notion_id)
            for url in detail.image_urls:
                image_name = self._extract_image_name(url, detail.notion_id)
                to_save_path = self._format_local_image_path(image_name, detail.notion_id)
                urllib.request.urlretrieve(url, to_save_path)
    
    def _make_asset_directory(self, notion_id: str):
        if not os.path.exists(self._asset_dir + '\\' + notion_id):
            os.mkdir(self._asset_dir + '\\' + notion_id)
    
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

    def _set_jekyll_image_directory_path_in_markdown(self, content: str, notion_id: str, image_name: str) -> str:
        jekyll_asset_dir = self._asset_dir.replace(self.directory, '')
        content_image_url = '{{site.baseurl}}' + jekyll_asset_dir + '/' + notion_id + '/' + image_name
        return content.replace(image_name, content_image_url)


    def _format_local_image_path(self, image_name: str, notion_id: str) -> str:
        return self._asset_dir + '\\' + notion_id + '\\' + image_name

    def _stage_and_unstage_images(self, details: List[NotionEntryDetails]):
        image_url_map = {}
        for detail in details:
            for url in detail.image_urls:
                image_url_map[url] = True
            for file_name in os.listdir(self._asset_dir + '\\' + detail.notion_id):
                # TODO only upload different images (need to identify duplicate images)
                comparable_file_name = self._format_local_image_path(file_name, detail.notion_id)
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
        factory = GithubPostFactory()
        for file_name in os.listdir(self._posts_dir):
            path = self._posts_dir + '\\' + file_name
            post = factory.from_file_path(path)
            id_file_name_dict[post.unique_id] = path
        return id_file_name_dict

    def _unstage_old_and_stage_new_post(self, old_file_path: str, new_post: GithubPost):
        old_post = GithubPostFactory().from_file_path(old_file_path)
        self._set_new_post_date_to_old_post_date(old_post, new_post)
        
        os.remove(old_file_path)
        if old_post.title != new_post.title:
            self.unstaged_files.append(old_file_path.replace(self.directory+'\\', ''))
        self._stage_new_post(new_post)

    def _set_new_post_date_to_old_post_date(self, old_post: GithubPost, new_post: GithubPost):
        new_post.date = old_post.date

    def _stage_new_post(self, new_post: GithubPost):
        file_name = new_post.write_to_file(self._posts_dir)
        self.staged_files.append(file_name.replace(self.directory+'\\', ''))
