from flask import Flask, request, jsonify
from flask_cors import CORS
from algo import PMachine, VMachine, PACO_VMP
from utils import GrafanaDashboardingUtils
import json
from proxmoxer import ProxmoxAPI

proxmox = ProxmoxAPI(
    "192.168.15.153", user="root@pam", password="m0chiru@@#681", verify_ssl=False
)

gdu = GrafanaDashboardingUtils("")

app = Flask(__name__)
CORS(app, allow_headers=["Content-Type"], supports_credentials=True)

def get_paco_vmp_from_config():
    with open ('config.json', 'r') as f:
        config = json.load(f)

    pms = [PMachine(pm['cpu_capacity'], pm['ram_capacity'], pm['disk_capacity']) for pm in config['pms']]
    return PACO_VMP(pms=pms)

paco_vmp = get_paco_vmp_from_config()

@app.route('/dashboarding/<name>', methods=['GET'])
def dashboarding(name):
    # data = request.json()
    # if data['dashboard_name']:
    #     dashboard_id = gdu.get_dashboard_id_by_title(data['dashboard_name'])
    #     return jsonify({"id": dashboard_id})
    # return jsonify({'error': 'No dashboard name provided'})
    dashboard_data = gdu.get_dashboard_id_by_title(name)
    return jsonify({"title": dashboard_data[0], "id": dashboard_data[1]})


@app.route('/createMachine', methods=['POST'])
def createMachine():
    vm_name = request.json['vm_name']
    cpu_req, ram_req, disk_req = int(request.json['cpu_req']),int(request.json['ram_req']), int(request.json['disk_req'])
    vm = VMachine(vm_name=vm_name, cpu_req=cpu_req, ram_req=ram_req, disk_req=disk_req)

    try:
        paco_vmp.add_vm(vm)
    except Exception as e:
        return jsonify({'error': 'VM creation failed' + str(e)})
    
    paco_vmp.save_to_statefile()
    return getVMList()


@app.route('/deleteMachine')
def deleteMachine():
    return jsonify(dict())

@app.route('/getVMList')
def getVMList():
    return_list = []
    for pm in paco_vmp.pms:
        pm_idex = paco_vmp.pm_index(pm)
        pm_list = [vm.get_as_dict() for vm in pm.vms]
        [vm.update({'pm': pm_idex}) for vm in pm_list]
        return_list.extend(pm_list)

    print(return_list)
    return jsonify(return_list)

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response

app.run(debug=True, port=5000)