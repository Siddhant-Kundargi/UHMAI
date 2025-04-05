resource "proxmox_virtual_environment_vm" "{{ new_vm_name }}" {

  node_name = "{{ node_name | default('pve') }}"
  vm_id = "{{ new_vm_id }}"
  name = "{{ new_vm_name }}"  

  cpu {
    cores = "{{ cpu_cores | default(1) }}"
  }
  {% if clone_id %}
  clone {
    vm_id = "{{ clone_id }}" 
  }
  {% endif %}
  memory {
    dedicated = "{{ memory_mb | default(2048) }}"
  }

  started = false
}