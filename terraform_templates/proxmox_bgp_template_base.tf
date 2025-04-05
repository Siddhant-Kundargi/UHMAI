terraform {
  required_providers {
    proxmox = {
      source = "bpg/proxmox"
      version = "0.61.1"
    }
  }
}

provider "proxmox" {
  endpoint = "https://{{ host | default('localhost') }}:8006/"
  username = "{{ terraform_user | default('terraform-prov@pve') }}"
  password = "{{ terrapass | default('123123')}}"
  insecure = true
}