from flask import Blueprint, request, jsonify, render_template, current_app
from FireFly import FireFly
from proxmox_management import ProxmoxManager
from shared_state import vms, firefly, can_accommodate_vm
import pickle
import os

vm_blueprint = Blueprint('vm', __name__)
PLACEMENT_FILE = 'vm_placement.pickle'
proxmox = ProxmoxManager()
VMID_COUNTER = 100  # Start VMIDs from 100
AUTOSCALING_GROUP_COUNTER = 1
autoscaling_groups = {}  # Store autoscaling group configurations

def load_placement():
    try:
        if os.path.exists(PLACEMENT_FILE):
            with open(PLACEMENT_FILE, 'rb') as f:
                return pickle.load(f)
        return {}
    except Exception as e:
        print(f"Error loading placement: {e}")
        return {}

def save_placement(placement):
    try:
        with open(PLACEMENT_FILE, 'wb') as f:
            pickle.dump(placement, f)
    except Exception as e:
        print(f"Error saving placement: {e}")

previous_placement = load_placement()

@vm_blueprint.route('/createMachine', methods=['POST'])
def create_machine():
    try:
        data = request.get_json() if request.is_json else {
            'cpu': int(request.form.get('cpu')),
            'mem': int(request.form.get('mem')),
            'disk': int(request.form.get('disk'))
        }

        if not all(field in data for field in ['cpu', 'mem', 'disk']):
            return jsonify({"status": "error", "message": "Missing required fields"}), 400

        if not current_app.config['PHYSICAL_MACHINES'] or not can_accommodate_vm(data['cpu'], data['mem']):
            print(current_app.config['PHYSICAL_MACHINES'])
            return jsonify({"status": "error", "message": "Insufficient resources"}), 400

        global VMID_COUNTER
        VMID_COUNTER += 1
        machine_id = f'vm{VMID_COUNTER}'
        vms[machine_id] = {"cpu": data['cpu'], "ram": data['mem'], "vmid": VMID_COUNTER}

        global firefly, previous_placement
        if len(current_app.config['PHYSICAL_MACHINES']) > 0 and len(vms) > 0:
            firefly = FireFly(current_app.config['PHYSICAL_MACHINES'], vms, previous_placement)
            if firefly.state:
                previous_placement = firefly.previous_placement
                save_placement(previous_placement)
                
                # Format VM data for Proxmox
                formatted_vms = []
                for vm_id, vm_spec in vms.items():
                    vmid = vm_spec.get("vmid", int(vm_id.replace('vm', '')))
                    vm_data = {
                        "new_vm_id": vmid,
                        "new_vm_name": f"vm{vmid}",
                        "node_name": "pve",
                        "cpu_cores": vm_spec["cpu"],
                        "memory_mb": vm_spec["ram"],
                        "disk_gb": data.get('disk', 8)
                    }
                    formatted_vms.append(vm_data)
                print(formatted_vms)
                proxmox.create_vm(
                    hypervisor_data={"node_name": "pve"},
                    vm_data=formatted_vms
                )
                result = proxmox.apply_changes()
                if result:
                    print(f"Proxmox changes applied: {result}")

        return jsonify({
            "status": "success",
            "machine_id": machine_id,
            "placement": firefly.state if firefly else None
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@vm_blueprint.route('/create', methods=['POST', 'GET'])
def create():
    return render_template('create_machine.html') if request.method == 'GET' else create_machine()

@vm_blueprint.route('/list', methods=['GET'])
def list_vms():
    # Group VMs by their autoscaling groups
    grouped_vms = {}
    standalone_vms = {}
    
    for vm_id, vm_data in vms.items():
        if 'autoscaling_group' in vm_data:
            gid = vm_data['autoscaling_group']
            if gid not in grouped_vms:
                grouped_vms[gid] = {
                    'vms': {},
                    'config': autoscaling_groups.get(gid, {})
                }
            grouped_vms[gid]['vms'][vm_id] = vm_data
        else:
            standalone_vms[vm_id] = vm_data

    placement_info = {
        'vms': standalone_vms,
        'scaling_groups': grouped_vms,
        'placement': firefly.state if firefly else None,
        'physical_machines': current_app.config['PHYSICAL_MACHINES'],
    }
    return jsonify(placement_info)

@vm_blueprint.route('/delete/<vm_id>', methods=['DELETE'])
def delete(vm_id):
    try:
        if vm_id not in vms:
            return jsonify({"error": "VM not found"}), 404
        
        del vms[vm_id]
        global firefly, previous_placement
        if vms and current_app.config['PHYSICAL_MACHINES']:
            if vm_id in previous_placement:
                del previous_placement[vm_id]
            firefly = FireFly(current_app.config['PHYSICAL_MACHINES'], vms, previous_placement)
            if firefly.state:
                previous_placement = firefly.previous_placement
                save_placement(previous_placement)
                
                formatted_vms = []
                for vid, vm_spec in vms.items():
                    vmid = vm_spec.get("vmid", int(vid.replace('vm', '')))
                    vm_data = {
                        "new_vm_id": vmid,
                        "new_vm_name": f"vm{vmid}",
                        "node_name": "pve",
                        "cpu_cores": vm_spec["cpu"],
                        "memory_mb": vm_spec["ram"],
                        "disk_gb": 8  # Default disk size
                    }
                    formatted_vms.append(vm_data)
                
                proxmox.create_vm(
                    hypervisor_data={"node_name": "pve"},
                    vm_data=formatted_vms
                )
                result = proxmox.apply_changes()
                if not result:
                    return jsonify({"error": "Failed to apply changes to Proxmox"}), 500
        
        return jsonify({"message": f"VM {vm_id} deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@vm_blueprint.route('/createAutoscalingGroup', methods=['POST'])
def create_autoscaling_group():
    try:
        data = request.get_json()
        required_fields = ['max_instance_count', 'min_instance_count', 'cpu', 'mem', 'disk']
        
        if not all(field in data for field in required_fields):
            return jsonify({"status": "error", "message": "Missing required fields"}), 400
        
        global AUTOSCALING_GROUP_COUNTER
        gid = AUTOSCALING_GROUP_COUNTER
        AUTOSCALING_GROUP_COUNTER += 1
        
        # Create initial instances based on min_instance_count
        instances = []
        
        for _ in range(data['min_instance_count']):
            global VMID_COUNTER
            VMID_COUNTER += 1
            machine_id = f'vm{VMID_COUNTER}'
            vms[machine_id] = {
                "cpu": data['cpu'],
                "ram": data['mem'],
                "vmid": VMID_COUNTER,
                "autoscaling_group": gid
            }
            instances.append(machine_id)
        
        # Update placement using FireFly
        global firefly, previous_placement
        if current_app.config['PHYSICAL_MACHINES'] and vms:
            firefly = FireFly(current_app.config['PHYSICAL_MACHINES'], vms, previous_placement)
            if firefly.state:
                previous_placement = firefly.previous_placement
                save_placement(previous_placement)
                
                # Format VM data for Proxmox creation
                formatted_vms = []
                for vm_id in instances:
                    vm_spec = vms[vm_id]
                    vm_data = {
                        "new_vm_id": vm_spec["vmid"],
                        "new_vm_name": f"vm{vm_spec['vmid']}",
                        "node_name": "pve",
                        "cpu_cores": vm_spec["cpu"],
                        "memory_mb": vm_spec["ram"],
                        "disk_gb": data['disk']
                    }
                    formatted_vms.append(vm_data)
                    
                proxmox.create_vm(
                    hypervisor_data={"node_name": "pve"},
                    vm_data=formatted_vms
                )
                result = proxmox.apply_changes()
                if not result:
                    return jsonify({"error": "Failed to create VMs in Proxmox"}), 500
        
        # Store autoscaling group configuration
        autoscaling_groups[gid] = {
            "max_instances": data['max_instance_count'],
            "min_instances": data['min_instance_count'],
            "current_instances": instances,
            "vm_template": {
                "cpu": data['cpu'],
                "mem": data['mem'],
                "disk": data['disk']
            }
        }
        
        return jsonify({
            "status": "success",
            "gid": gid,
            "instances": instances,
            "placement": firefly.state if firefly else None
        }), 200
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@vm_blueprint.route('/triggerAutoScaling/<int:gid>/<action>', methods=['GET'])
def update_instance_count(gid, action):
    try:
        if gid not in autoscaling_groups:
            return jsonify({"status": "error", "message": "Autoscaling group not found"}), 404

        group = autoscaling_groups[gid]
        current_count = len(group['current_instances'])
        scale_up = action.lower() == 'up'

        if scale_up and current_count >= group['max_instances']:
            return jsonify({"status": "error", "message": "Maximum instance limit reached"}), 400
        if not scale_up and current_count <= group['min_instances']:
            return jsonify({"status": "error", "message": "Minimum instance limit reached"}), 400

        if scale_up:
            # Create new instance
            global VMID_COUNTER
            VMID_COUNTER += 1
            machine_id = f'vm{VMID_COUNTER}'
            template = group['vm_template']
            
            vms[machine_id] = {
                "cpu": template['cpu'],
                "ram": template['mem'],
                "vmid": VMID_COUNTER,
                "autoscaling_group": gid
            }
            group['current_instances'].append(machine_id)
            
            # Update placement
            global firefly, previous_placement
            if current_app.config['PHYSICAL_MACHINES'] and vms:
                firefly = FireFly(current_app.config['PHYSICAL_MACHINES'], vms, previous_placement)
                if firefly.state:
                    previous_placement = firefly.previous_placement
                    save_placement(previous_placement)
                    
                    # Format VM data for all instances in autoscaling group
                    formatted_vms = []
                    for vm_id in group['current_instances']:
                        vm_spec = vms[vm_id]
                        formatted_vms.append({
                            "new_vm_id": vm_spec["vmid"],
                            "new_vm_name": f"vm{vm_spec['vmid']}",
                            "node_name": "pve",
                            "cpu_cores": vm_spec["cpu"],
                            "memory_mb": vm_spec["ram"],
                            "disk_gb": template['disk']
                        })
                    
                    proxmox.create_vm(
                        hypervisor_data={"node_name": "pve"},
                        vm_data=formatted_vms
                    )
                    result = proxmox.apply_changes()
                    if not result:
                        return jsonify({"error": "Failed to create VM in Proxmox"}), 500

        else:
            # Remove last instance
            if group['current_instances']:
                vm_to_remove = group['current_instances'].pop()
                if vm_to_remove in vms:
                    del vms[vm_to_remove]
                if vm_to_remove in previous_placement:
                    del previous_placement[vm_to_remove]

                # Update placement
                if vms and current_app.config['PHYSICAL_MACHINES']:
                    firefly = FireFly(current_app.config['PHYSICAL_MACHINES'], vms, previous_placement)
                    if firefly.state:
                        previous_placement = firefly.previous_placement
                        save_placement(previous_placement)

        return jsonify({
            "status": "success",
            "current_instances": group['current_instances'],
            "placement": firefly.state if firefly else None
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
