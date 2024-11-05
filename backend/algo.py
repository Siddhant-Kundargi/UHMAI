import numpy as np
import random
from pickle import dump as pickle_dump, load as pickle_load

# Define constants
ALPHA = 1     # Pheromone influence
BETA = 6      # Heuristic influence
TAU_0 = 0.1   # Initial pheromone value
RHO = 0.8     # Evaporation rate
KP = 365      # Constant for pheromone update

class PMachine:
    """ Physical machine class with support for disk space """
    def __init__(self, cpu_capacity, ram_capacity, disk_capacity):
        self.cpu_capacity = cpu_capacity
        self.ram_capacity = ram_capacity
        self.disk_capacity = disk_capacity 
        self.cpu_used = 0
        self.ram_used = 0
        self.disk_used = 0
        self.vms = [] 

    def has_capacity_for(self, vm):
        """ Check if the PM has enough capacity for a VM's CPU, RAM, and Disk """
        return (self.cpu_capacity - self.cpu_used >= vm.cpu_req and
                self.ram_capacity - self.ram_used >= vm.ram_req and
                self.disk_capacity - self.disk_used >= vm.disk_req)

    def add_vm(self, vm):
        """ Add VM to this PM and update used resources (CPU, RAM, Disk) """
        self.vms.append(vm)
        self.cpu_used += vm.cpu_req
        self.ram_used += vm.ram_req
        self.disk_used += vm.disk_req

    def remove_vm(self, vm):
        """ Remove VM from this PM and update used resources (CPU, RAM, Disk) """
        if vm in self.vms:
            self.vms.remove(vm)
            self.cpu_used -= vm.cpu_req
            self.ram_used -= vm.ram_req
            self.disk_used -= vm.disk_req 

class VMachine:
    """ Virtual machine class with disk space requirements """
    def __init__(self, vm_name, cpu_req, ram_req, disk_req):
        self.vm_name = vm_name
        self.cpu_req = cpu_req
        self.ram_req = ram_req
        self.disk_req = disk_req 

    def get_as_dict(self):
        """ Return VM attributes as a dictionary """
        return {"vm_name": self.vm_name,"cpu": self.cpu_req, "ram": self.ram_req, "disk": self.disk_req}

    def __str__(self):
        return str(self.get_as_dict())

class PACO_VMP:
    def __init__(self, num_pms=0, pms=None):
        """ Initialize PMs with different capacities including disk space """
        if pms:
            self.pms = pms
            self.num_pms = len(pms)
            num_pms = self.num_pms
        else:
            self.pms = [PMachine(4, 4, 20) for _ in range(num_pms)] 
        
        print(f"Initialized {num_pms} PMs with CPU, RAM, and Disk capacities of {self.pms[0].cpu_capacity}, {self.pms[0].ram_capacity}, {self.pms[0].disk_capacity}")
        self.pheromone = np.full((num_pms, num_pms), TAU_0)  # Initialize pheromone matrix

    def save_to_statefile(self, statefile='statefile.pkl'):
        """ Save the current state of the PACO_VMP object to a file """
        with open(statefile, 'wb') as f:
            pickle_dump(self, f)
        
    @staticmethod
    def load_from_statefile(statefile='statefile.pkl'):
        """ Load the PACO_VMP object from a saved statefile """
        with open(statefile, 'rb') as f:
            return pickle_load(f)

    def heuristic(self, pm, vm):
        """ Heuristic function considering CPU, RAM utilization """
        fC = (pm.cpu_used + vm.cpu_req) / pm.cpu_capacity
        fR = (pm.ram_used + vm.ram_req) / pm.ram_capacity
        return (1 - abs(fC - fR)) / (1 + fC + fR)

    def calculate_score(self, pm, vm):
        """ Calculate heuristic and pheromone score for the PM and VM placement """
        heuristic_value = self.heuristic(pm, vm)
        pheromone_value = np.mean(self.pheromone[self.pm_index(pm), :])  # Avg pheromone between VMs in the same PM
        return (pheromone_value ** ALPHA) * (heuristic_value ** BETA)

    def find_best_pm(self, vm):
        """ Find the best PM based on heuristic and pheromone scores """
        best_score = -float('inf')
        best_pm = None
        for pm in self.pms:
            if pm.has_capacity_for(vm):  # Check if the PM has enough resources (CPU, RAM, Disk)
                score = self.calculate_score(pm, vm)
                if score > best_score:
                    best_score = score
                    best_pm = pm
            
            else:
                raise("PM does not have enough capacity for the VM")
        return best_pm

    def add_vm(self, vm):
        """ Add a VM to the best PM """
        best_pm = self.find_best_pm(vm)
        if best_pm:
            best_pm.add_vm(vm)
            self.update_pheromone(best_pm, vm)

    def remove_vm(self, vm):
        """ Remove VM from its PM """
        for pm in self.pms:
            if vm in pm.vms:
                pm.remove_vm(vm)
                self.update_pheromone(pm, vm, removal=True)
                break

    def update_pheromone(self, pm, vm, removal=False):
        """ Update pheromone matrix after VM addition or removal """
        for other_vm in pm.vms:
            i = self.pm_index(pm)
            j = self.pm_index(pm)
            if removal:
                self.pheromone[i][j] = max(TAU_0, self.pheromone[i][j] * (1 - RHO))  # Evaporation
            else:
                self.pheromone[i][j] += KP / (pm.cpu_used + pm.ram_used)  # Pheromone deposition

    def pm_index(self, pm):
        """ Helper function to get the index of a PM in the pheromone matrix """
        return self.pms.index(pm)

if __name__ == "__main__":
    print("Running the PACO-VMP algorithm demo with disk space support")
    
    # Example usage
    paco_vmp = PACO_VMP(num_pms=5)

    # Create some VMs
    vms = []
    for _ in range(10):
        cpu_req = random.randint(10, 100)
        ram_req = random.randint(10, 100)
        disk_req = random.randint(50, 300)  # Adding disk requirements
        vm = VMachine(cpu_req=cpu_req, ram_req=ram_req, disk_req=disk_req)
        vms.append(vm)

    # Add VMs
    for vm in vms:
        paco_vmp.add_vm(vm)

    print("PM Status after adding VMs:")
    for pm in paco_vmp.pms:
        print(f"PM {paco_vmp.pm_index(pm)}: {pm.vms}")

    # Remove 4 VMs
    for _ in range(4):
        vm = random.choice(vms)
        paco_vmp.remove_vm(vm)
        vms.remove(vm)

    print("PM Status after removing VMs:")
    for pm in paco_vmp.pms:
        print(f"PM {paco_vmp.pm_index(pm)}: {pm.vms}")
