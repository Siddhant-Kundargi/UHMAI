from os import path
import requests

class GrafanaDashboardingUtils:
    def __init__(self, api_token, base_url="http://localhost:3000"):
        self.__api_token = api_token
        while base_url.endswith('/'):
            base_url = base_url[:-1]
        self.__base_url = base_url

    def get_list_of_dashboards(self):
        grafana_url = self.__base_url + '/api/search'
        headers = {'Authorization': f'Bearer {self.__api_token}'}
        response = requests.get(grafana_url, headers=headers)
        response.raise_for_status()
        dashboards = response.json()

        dashboards_dict = dict((i['title'], i['uid']) for i in dashboards)
        return dashboards_dict
    
    def get_dashboard_id_by_title(self, search_string):
        full_dict = self.get_list_of_dashboards()
        for (i, j) in full_dict.items():
            if search_string in i:
                return (i, j)

# TF_DIR = "backend\\terraform_templates"

# base_template_path = path.join(TF_DIR, "proxmox_bgp_template.tf")
# base_template = open(base_template_path, "r").read()

# class TerraformTemplate:
#     def __init__(self, name, base_template_path=base_template, vm_resource_template_path=None):
#         self.name = name
#         with open(base_template_path, "r") as f:
#             self.template = f.read()
#         with open(vm_resource_template_path, "r") as f:
#             self.vm_resource_template = f.read()
#         self.resources = []

#     def __str__(self):
#         return self.template

#     def write(self, path):
#         with open(path, "w") as f:
#             f.write(self.template)

#     def add_resources(self, resources):
#         self.resources.append(resources)

#     def remove_resources(self, resources):
#         self.resources.remove(resources)