from flask import Flask, render_template, request, jsonify
from FireFly import FireFly

app = Flask(__name__)

# Global state
physical_machines = {}
vms = {}
firefly = None

def can_accommodate_vm(cpu, memory):
    total_available_cpu = sum(host["cpu"] for host in physical_machines.values())
    total_available_memory = sum(host["ram"] for host in physical_machines.values())
    total_used_cpu = sum(vm["cpu"] for vm in vms.values())
    total_used_memory = sum(vm["ram"] for vm in vms.values())
    
    return (total_available_cpu - total_used_cpu >= cpu and 
            total_available_memory - total_used_memory >= memory)

def add_machine(cpu, allocated_memory, disk):
    if not physical_machines:
        return {
            "status": "error",
            "message": "No physical machines available. Please add physical machines first.",
            "type": "warning"
        }
    
    if not can_accommodate_vm(cpu, allocated_memory):
        return {
            "status": "error",
            "message": "Insufficient resources available. Cannot add more VMs.",
            "type": "error"
        }
    
    vm_id = f'vm{len(vms) + 1}'
    vm_spec = {"cpu": cpu, "ram": allocated_memory}
    vms[vm_id] = vm_spec
    
    response = {
        "status": "success",
        "message": "VM added successfully",
        "type": "success",
        "vm_id": vm_id,
        "vm_details": vm_spec,
        "placement": None
    }
    
    global firefly
    if len(physical_machines) > 0:
        firefly = FireFly(physical_machines, vms)
        response["placement"] = firefly.state
    
    return response

def add_physical_machine(cpu, allocated_memory, disk):
    machine_id = f'host{len(physical_machines) + 1}'
    physical_machines[machine_id] = {"cpu": cpu, "ram": allocated_memory}
    
    response = {
        "status": "success",
        "host_id": machine_id,
        "host_details": physical_machines[machine_id],
        "placement": None
    }
    
    global firefly
    if len(vms) > 0:
        firefly = FireFly(physical_machines, vms)
        response["placement"] = firefly.state
    
    return response

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/newMachine', methods=['POST'])
def newMachine():
    machineData = request.get_json()
    cpu_core_count = int(machineData['cpu'])
    allocated_memory = int(machineData['mem'])
    disk = int(machineData['disk'])
    
    resp = add_machine(cpu_core_count, allocated_memory, disk)
    return jsonify(resp)

@app.route('/newPhysicalMachine', methods=['POST'])
def new_physical_machine():
    physical_machine_data = request.get_json()
    cpu_core_count = int(physical_machine_data['cpu'])
    allocated_memory = int(physical_machine_data['mem'])
    disk = int(physical_machine_data['disk'])
    
    resp = add_physical_machine(cpu_core_count, allocated_memory, disk)
    return jsonify(resp)

@app.route('/reset', methods=['POST'])
def reset():
    """
    Reset the entire system state.
    - Clears all physical machines
    - Clears all virtual machines
    - Resets the FireFly algorithm
    This is like starting the system from scratch.
    """
    global physical_machines, vms, firefly
    physical_machines = {}
    vms = {}
    firefly = None
    return jsonify({
        "status": "success",
        "message": "Complete system reset: Cleared all physical and virtual machines",
        "type": "warning",
        "physical_machines": physical_machines,
        "vms": vms,
        "placement": None
    })

@app.route('/getCurrentPlacement', methods=['GET'])
def get_current_placement():
    return jsonify({
        "status": "success",
        "placement": firefly.state if firefly else None,
        "physical_machines": physical_machines,
        "vms": vms
    })

@app.route('/recreatePlacement', methods=['POST'])
def recreate_placement():
    """
    Recreate VM placement using FireFly algorithm.
    - Keeps existing physical and virtual machines
    - Only recalculates the placement of VMs on physical machines
    This is useful for optimizing the current placement without changing the machines.
    """
    global firefly
    if len(physical_machines) > 0 and len(vms) > 0:
        firefly = FireFly(physical_machines, vms)
        return jsonify({
            "status": "success",
            "message": "Recalculated VM placement while keeping existing machines",
            "type": "info",
            "placement": firefly.state,
            "physical_machines": physical_machines,
            "vms": vms
        })
    return jsonify({
        "status": "error",
        "message": "Cannot recreate placement: Need at least one physical machine and one VM",
        "type": "warning"
    })

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)