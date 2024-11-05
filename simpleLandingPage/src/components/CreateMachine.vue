<script setup>
import { ref } from 'vue';

const machineName = ref('');
const machineType = ref('');

const emits = defineEmits(['on-create-machine']);

async function createMachine() {
    const stats = machineType.value.split('-');
    let cpu = stats[0];
    let ram = stats[1];
    let disk = stats[2];

    const response = await fetch('http://localhost:5000/createMachine', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            vm_name: machineName.value,
            cpu_req: cpu,
            ram_req: ram,
            disk_req: disk
        })
    });

    const data = await response.json();
    console.log(data);
    console.log(machineName.value, machineType.value);

    const vm = {
        name: machineName.value,
        cpu: cpu,
        ram: ram,
        disk: disk
    };

    // reset the form
    machineName.value = '';
    machineType.value = '';

    emits('on-create-machine');
}
</script>

<template>
    <form @submit.prevent="createMachine" class="bg-[#d2e7ff] p-8 rounded-lg m-2">
        <div class="mb-4">
            <label for="machineName" class="block text-gray-700 font-bold mb-2 text-left font-mono">Machine Name</label>
            <input type="text" id="machineName" v-model="machineName" class="shadow appearance-none border rounded-full w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline font-mono" required>
        </div>
        <div class="mb-4">
            <label for="machineType" class="block text-gray-700 font-bold mb-2 text-left font-mono">Machine Type</label>
            <input type="text" id="machineType" v-model="machineType" class="shadow appearance-none border rounded-full w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline font-mono" required>
        </div>
        <div class="flex items-center justify-between">
            <button type="submit" class="hover:bg-red-400 hover:text-[#fff6e9] bg-[#fff6e9] rounded-full text-black font-bold py-2 px-4 focus:outline-none focus:shadow-outline font-mono">Create Machine</button>
        </div>
    </form>
</template>