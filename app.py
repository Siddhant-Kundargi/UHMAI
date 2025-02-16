from flask import Flask, render_template, request, jsonify
from FireFly import FireFly

app = Flask(__name__)

# Global state
physical_machines = {}
vms = {}
firefly = None

def add_machine(cpu, allocated_memory, disk):
    vm_id = f'vm{len(vms) + 1}'
    vm_spec = {"cpu": cpu, "ram": allocated_memory}
    vms[vm_id] = vm_spec
    
    global firefly
    if firefly and len(physical_machines) > 0:
        firefly = FireFly(physical_machines, vms)
        return {"status": "success", "placement": firefly.state}
    return {"status": "waiting for physical machines"}

def add_physical_machine(cpu, allocated_memory, disk):
    machine_id = f'host{len(physical_machines) + 1}'
    physical_machines[machine_id] = {"cpu": cpu, "ram": allocated_memory}
    
    global firefly
    if len(vms) > 0:
        firefly = FireFly(physical_machines, vms)
        return {"status": "success", "placement": firefly.state}
    return {"status": "success", "message": "waiting for VMs"}

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

@app.route('/getCurrentPlacement', methods=['GET'])
def get_current_placement():
    if firefly:
        return jsonify({
            "status": "success",
            "placement": firefly.state,
            "physical_machines": physical_machines,
            "vms": vms
        })
    return jsonify({"status": "no placement yet"})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)