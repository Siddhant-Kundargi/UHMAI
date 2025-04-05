import subprocess
from os import environ, path, linesep
from jinja2 import Environment, FileSystemLoader

def render_template(source_template_path: str, template_params: dict) -> str:
    """
    Render a Jinja2 template with given parameters
    
    Args:
        source_template_path: Full path to the template file
        template_params: Dictionary containing template parameters
    
    Returns:
        str: Rendered template output
    """
    template_dir = path.dirname(source_template_path)
    template_file = path.basename(source_template_path)
    
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template(template_file)
    return template.render(template_params)

class ProxmoxManager:
    def __init__(self, debug=True):
        self.TF_TEMPLATE_SOURCE = path.join(path.dirname(__file__), "terraform_templates")
        self.terraform_dir = path.join(path.dirname(__file__), "TemporaryTerraform")
        self._counter = 0
        self.debug = debug

    def apply_changes(self) -> str:
        """Execute terraform apply command and return the output."""
        result = subprocess.Popen(
            ['terraform.exe', f'-chdir={self.terraform_dir}', 'apply', '-auto-approve'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = result.stdout.read(), result.stderr.read()
        return stderr.decode() if stderr else stdout.decode()

    def  create_shell(self, vm_id):
        port_to_use = vm_id + 4000
        command = f"docker run --rm -p {port_to_use}:{4200} --name container-{vm_id} -e RTPW=pass -d shellinabox" 

        subprocess.Popen(command, shell=True)

    def create_vm(self, hypervisor_data: dict, vm_data: dict) -> None:
        """Create VM configuration from templates."""
        print("called vm data")
        print(vm_data)
        base_template_location = path.join(self.TF_TEMPLATE_SOURCE, "proxmox_bgp_template_base.tf")
        vm_resource_template = path.join(self.TF_TEMPLATE_SOURCE, "proxmox_bgp_vm_resource.tf")
        base_template = render_template(base_template_location, hypervisor_data)
        template = base_template

        for vm in vm_data:
            vm_template = render_template(vm_resource_template, vm)
            template += "\n\n" + vm_template

        for vm in vm_data:
            self.create_shell(vm['new_vm_id'])

        with open(path.join(self.terraform_dir, "main.tf"), 'w') as fd:
            fd.write(template)