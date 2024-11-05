resource "proxmox_virtual_environment_vm" "testbuntu" {

  node_name = "pve"
  vm_id = "{{ new_vm_id }}"
  name = "{{ new_vm_name }}"  

  clone {
    vm_id = "{{ template_vm_id }}"
  }

  started = true
}