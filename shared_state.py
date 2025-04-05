# Global state
physical_machines = {}
vms = {}
firefly = None
autoscaling_groups = {}  # Added shared autoscaling groups variable

def initialize_physical_machines(app_config):
    global physical_machines
    physical_machines = app_config['PHYSICAL_MACHINES']

def can_accommodate_vm(cpu, memory):
    global physical_machines
    if not physical_machines:
        return False
        
    total_available_cpu = sum(host["cpu"] for host in physical_machines.values())
    total_available_memory = sum(host["ram"] for host in physical_machines.values())
    total_used_cpu = sum(vm["cpu"] for vm in vms.values())
    total_used_memory = sum(vm["ram"] for vm in vms.values())

    print(f"Available: CPU={total_available_cpu}, RAM={total_available_memory}")
    print(f"Used: CPU={total_used_cpu}, RAM={total_used_memory}")
    print(f"Requested: CPU={cpu}, RAM={memory}")
    
    return (total_available_cpu - total_used_cpu >= cpu and 
            total_available_memory - total_used_memory >= memory)
