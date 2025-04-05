terraform {
  required_providers {
    proxmox = {
      source = "bpg/proxmox"
      version = "0.61.1"
    }
  }
}

provider "proxmox" {
  endpoint = "https://localhost:8006/"
  username = "terraform-prov@pve"
  password = "123123"
  insecure = true
}

resource "proxmox_virtual_environment_vm" "vm101" {

  node_name = "pve"
  vm_id = "101"
  name = "vm101"  

  cpu {
    cores = "1"
  }
  
  memory {
    dedicated = "1024"
  }

  started = false
}

resource "proxmox_virtual_environment_vm" "vm102" {

  node_name = "pve"
  vm_id = "102"
  name = "vm102"  

  cpu {
    cores = "1"
  }
  
  memory {
    dedicated = "1024"
  }

  started = false
}

resource "proxmox_virtual_environment_vm" "vm103" {

  node_name = "pve"
  vm_id = "103"
  name = "vm103"  

  cpu {
    cores = "1"
  }
  
  memory {
    dedicated = "1024"
  }

  started = false
}