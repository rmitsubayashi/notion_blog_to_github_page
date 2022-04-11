import json
import requests
from types import SimpleNamespace

class NotionRepo:
    def __init__(self, oauth_token):
        self._request_header = {
            "Authorization": "Bearer " + oauth_token,
            "Notion-Version": "2022-02-22"
        }
        self._base_url = "https://api.notion.com/v1/"

    def get_table_items(self, table_id):
        response = requests.post(self._base_url + "databases/"+table_id+"/query", headers=self._request_header)
        return json.loads(response.text, object_hook=lambda d: SimpleNamespace(**d)).results
    
    def get_link_content(self, page_id):
        response = requests.get(self._base_url + "blocks/" + page_id + "/children", headers=self._request_header)
        return json.loads(response.text, object_hook=lambda d: SimpleNamespace(**d)).results

    def get_title(self, table_id):
        response = requests.get(self._base_url + "databases/"+table_id, headers=self._request_header)
        table_parent_id = json.loads(response.text, object_hook=lambda d: SimpleNamespace(**d)).parent.page_id
        parent_response = requests.get(self._base_url + "pages/"+table_parent_id, headers=self._request_header)
        return json.loads(parent_response.text, object_hook=lambda d: SimpleNamespace(**d)).properties.Name.title[0].plain_text

    def update_status_to_published(self, id):
        json_data = { "properties": {"status": { "select": { "name": "published", "color": "blue"} } } }
        requests.patch(self._base_url + "pages/"+id, headers=self._request_header, json = json_data)
    
