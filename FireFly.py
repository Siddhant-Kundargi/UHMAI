import numpy as np

class FireFly:

    def __init__(self, machine_dict, vm_dict, previous_placement={}):
        if not machine_dict or not vm_dict:
            raise ValueError("Both machine_dict and vm_dict must not be empty")
        
        self.physical_machines = machine_dict
        self.vms = vm_dict
        self.previous_placement = previous_placement  # Add state storage
        self.state = self.firefly_vm_placement(self.physical_machines, self.vms)

    def calculate_vm_fitness(self, vm_placements, physical_hosts, vms, previous_placement):
        """Calculates the fitness of a VM placement solution."""
        total_movements = 0
        overloaded_hosts = 0

        if previous_placement:
          for host, vms_on_host in vm_placements.items():
              for vm in vms_on_host:
                  if previous_placement.get(vm) != host:
                      total_movements += 1

        for host_id, host_data in physical_hosts.items():
            cpu_used = 0
            ram_used = 0
            for vm_id in vm_placements[host_id]:
                if vm_id not in vms: continue
                cpu_used += vms[vm_id]['cpu']
                ram_used += vms[vm_id]['ram']

            if cpu_used > host_data['cpu'] or ram_used > host_data['ram']:
                overloaded_hosts += 1

        fitness = total_movements * 10 + overloaded_hosts * 10  # Higher fitness is worse. Adjust weights if needed.
        return fitness

    def firefly_algorithm(self, objective_function, num_fireflies, max_iterations, alpha, beta, gamma, epsilon, search_space):
        dimensions = len(search_space[0])
        fireflies = np.random.uniform(low=np.array(search_space[0]), high=np.array(search_space[1]), size=(num_fireflies, dimensions))
        brightness = np.array([objective_function(x) for x in fireflies])

        for t in range(max_iterations):
            for i in range(num_fireflies):
                for j in range(num_fireflies):
                    if brightness[j] > brightness[i]:
                        rij = np.linalg.norm(fireflies[i] - fireflies[j])
                        Aij = beta / (rij**2 + epsilon)
                        fireflies[i] = fireflies[i] + beta * np.exp(-gamma * rij**2) * (fireflies[j] - fireflies[i]) + alpha * (np.random.uniform(low=-1, high=1, size = dimensions))
                        for d in range(dimensions):
                            fireflies[i][d] = np.clip(fireflies[i][d], search_space[0][d], search_space[1][d])

                brightness[i] = objective_function(fireflies[i])

        best_index = np.argmax(brightness)
        best_solution = fireflies[best_index]
        best_fitness = brightness[best_index]
        return best_solution, best_fitness

    def firefly_vm_placement(self, physical_hosts, vms, num_fireflies=20, max_iterations=100, alpha=0.2, beta=1, gamma=1, epsilon=1e-6):
        if len(physical_hosts) == 0:
            return {}
            
        num_hosts = len(physical_hosts)
        num_vms = len(vms)
        
        if num_vms == 0:
            return {host_id: [] for host_id in physical_hosts}
            
        search_space = ([0] * num_vms, [num_hosts - 1] * num_vms)

        def decode_firefly(firefly):
            vm_placements = {host_id: [] for host_id in physical_hosts}
            # First, add existing placements that are still valid
            for vm_id, host_id in self.previous_placement.items():
                if vm_id in vms and host_id in physical_hosts:
                    vm_placements[host_id].append(vm_id)
            
            # Then place new VMs
            for vm_index, host_index in enumerate(firefly):
                vm_id = list(vms.keys())[vm_index]
                if vm_id not in self.previous_placement:  # Only place new VMs
                    host_id = list(physical_hosts.keys())[int(round(host_index))]
                    vm_placements[host_id].append(vm_id)
            return vm_placements

        best_solution, best_fitness = self.firefly_algorithm(
            lambda x: self.calculate_vm_fitness(decode_firefly(x), physical_hosts, vms, self.previous_placement),
            num_fireflies, max_iterations, alpha, beta, gamma, epsilon, search_space
        )
        best_placement = decode_firefly(best_solution)

        # Update the class's previous_placement state
        self.previous_placement = {vm: host for host, vms_on_host in best_placement.items() for vm in vms_on_host}

        return best_placement

    def delete_vm(self, vm_id):
        """
        Deletes a VM from the placement without recalculating placement.
        Returns True if VM was found and deleted, False otherwise.
        """
        # Remove from vms dictionary if it exists
        if vm_id in self.vms:
            del self.vms[vm_id]
        else:
            return False

        # Remove from placement state if it exists
        if vm_id in self.previous_placement:
            host_id = self.previous_placement[vm_id]
            del self.previous_placement[vm_id]
            
            # Also remove from current state if present
            if host_id in self.state and vm_id in self.state[host_id]:
                self.state[host_id].remove(vm_id)
            
            return True
            
        return False