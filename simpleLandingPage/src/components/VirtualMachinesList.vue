<script setup>
import { ref } from 'vue'

// Initial VM data
class VM {
  constructor(name, type) {
    specs = type.split('-')
    
    this.name = name
    this.cpu = specs[0]
    this.ram = specs[1]
    this.disk = specs[2]
  }
}

const vmList = ref([])
const emit = defineEmits(['show-vm-context'])

async function getVMList() {
  const response = await fetch("http://localhost:5000/getVMList", )
  const data = await response.json()
  console.log(data)
  vmList.value = data  //data.map(vm => new VM(vm.name, vm.type))
}

// Function to create a new VM item
function createVMItem(name) {
    vmList.value.push(name) // No need for an object here, since your vmList is just an array of strings
}

// Function to handle view change
function changeView(name) {
  emit('show-vm-context', name)
}

getVMList()
setInterval(getVMList, 10000)
</script>

<template>
  <h2 class="px-2 py-2 font-bold text-xl mb-2">Available Virtual Machines</h2>
  <ul id="vm-list" class="flex-1 space-y-2 overflow-y-auto">
    <li 
      @click="changeView(vm.vm_name)" 
      v-for="(vm, index) in vmList" 
      :key="index"
      :class='[vm.alive === "dead" ? "bg-[#B2FBA5]" : "", vm.alive === "alive" ? "bg-[#FF6961]" : "bg-yellow-100",  "hover:bg-yellow-200 cursor-pointer py-2 px-4 rounded-full flex justify-between items-center"]'
    >
      <span>{{ vm.vm_name }}</span>
    </li>
  </ul> 
</template>
