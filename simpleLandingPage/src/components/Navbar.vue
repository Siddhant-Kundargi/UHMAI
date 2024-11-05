<script setup>
import { ref } from 'vue'
</script>

<script>
export default {
    name: 'Navbar',
    data() {
        return {
            message: ref('Hello Vue 3!')
        }
    },
    methods: {
        createMachine(){
            this.$emit('create-machine', true)
        }
    }
}
</script>

<template>
    <div>
        <div>
            <div class="flex px-2 py-1 gap-x-2 bg-[#d2e7ff] px-2 py-2 mx-1 mt-2 rounded-full">
                <button @click="this.$emit('set-default')" visible="" href="" class="hover:bg-red-400 hover:text-[#fff6e9] rounded-full px-1.5 py-1 block bg-[#fff6e9]">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M8.25 9V5.25A2.25 2.25 0 0 1 10.5 3h6a2.25 2.25 0 0 1 2.25 2.25v13.5A2.25 2.25 0 0 1 16.5 21h-6a2.25 2.25 0 0 1-2.25-2.25V15m-3 0-3-3m0 0 3-3m-3 3H15" />
                    </svg>

                </button>
                
                
                <button @click="createMachine" href="" class="hover:bg-blue-400 hover:text-[#fff6e9] font-bold py-1 px-2 rounded-full font-mono block bg-[#fff6e9] ml-3">
                    Create
                </button>

                <button href="" class="hover:bg-blue-400 hover:text-[#fff6e9] font-bold py-1 px-2 rounded-full font-mono block bg-[#fff6e9]">
                    Shell
                </button>

                <button href="" class="hover:bg-blue-400 hover:text-[#fff6e9] font-bold py-1 px-2 rounded-full font-mono block bg-[#fff6e9]">
                    Users
                </button>

                <div class="flex-grow"></div>

                <button href="" class="hover:bg-red-400 hover:text-[#fff6e9] rounded-full px-1 py-1 block bg-[#fff6e9]">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="size-6">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M5.636 5.636a9 9 0 1 0 12.728 0M12 3v9" />
                    </svg>

                </button>
                


            </div>
            <nav>
                
            </nav>
        </div>
    </div>
</template>