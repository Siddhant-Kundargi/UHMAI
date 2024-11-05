terraform {
  required_providers {
    proxmox = {
      source = "bpg/proxmox"
      version = "0.61.1"
    }
  }
}

provider "proxmox" {
  endpoint = "https://{{ host }}:8006/"
  username = "terraform-prov@pve"
  password = "{{ terrapass }}"
  insecure = true
}