<script setup>
import Navbar from '@/components/Navbar.vue'
import CreateMachine from './components/CreateMachine.vue';
import VirtualMachinesList from './components/VirtualMachinesList.vue';
import Stats from './components/Stats.vue';
import { ref, watch, nextTick } from 'vue'

const show = ref('stats-view')
const showContext = ref('default')

const createMachine = () => {
  show.value = 'create-machine-view'
}

const showMachine = (name='') => {
  showContext.value = name
  show.value = ''
  nextTick(() => {
    show.value = 'stats-view'
  })
}

const onCreateMachine = () => {
  show.value = 'stats-view'
  console.log('Machine created')
}
</script>

<template>
  <Navbar @create-machine='createMachine' @set-default="showMachine"/>
  <div class="grid grid-cols-4 flex flex-1">
    <div class="col-span-1 bg-[#eeeeee] my-3 rounded-lg h-[88vh] ml-2 mr-1 pl-2 pr-4 flex flex-col font-mono flex-wrap">
      <VirtualMachinesList @show-vm-context="showMachine" />
    </div>
    <div class="bg-[#eeeeee] col-span-3 m-3 rounded-lg h-[88vh]">
      <div v-if="show === 'create-machine-view'" class="grid col-span-3">
        <CreateMachine @on-create-machine="onCreateMachine" />
      </div>
      <div v-if="show === 'stats-view'" class="grid col-span-3 flex flex-col h-full flex-start">
        <Stats :context=showContext />
      </div>
    </div>
  </div>
</template>