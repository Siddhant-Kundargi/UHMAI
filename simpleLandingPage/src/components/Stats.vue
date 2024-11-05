<script setup>
import { ref, toRefs } from 'vue'
const props = defineProps(['context'])
const { context } = toRefs(props)


const dashboardId = ref('')
const dashboardTitle = ref('')


// const fetchDashboardId = async (filteringString) => {
//     try {
//         const response = await fetch('http://localhost:5000/dashboarding/', {
//             // method: 'POST',
//             // headers: {
//             //     'Content-Type': 'application/json'
//             // },
//             // body: JSON.stringify({ "dashboard_name": filteringString })
//         })
//         const data = await response.json()
//         dashboardId.value = data.id // Assuming the response contains an 'id' field
//         console.log(dashboardId.value)
//     } catch (error) {
//         console.error('Error fetching dashboard ID:', error)
//     }
// }

const prefix = "http://localhost:3000/d-solo/"
const suffix = ["?timezone=browser&orgId=1&theme=light&panelId=2&__feature.dashboardSceneSolo", "?timezone=browser&orgId=1&theme=light&panelId=3&__feature.dashboardSceneSolo"] 

const fetchDashboardId = async (filteringString) => {
    try {
        if (filteringString === "" || filteringString === "default") {
            filteringString = "dashboard1"
        }
        console.log(filteringString)
        var url = 'http://localhost:5000/dashboarding/' + filteringString
        console.log(url)
        const response = await fetch(url)
        const data = await response.json()
        console.log(data)
        dashboardId.value = data.id // Assuming the response contains an 'id' field
        dashboardTitle.value = data.title
        console.log(dashboardId.value)
    } catch (error) {
        console.error('Error fetching dashboard ID:', error)
    }
}

fetchDashboardId(context.value)
</script>

<template>  
    <iframe v-for="(suffixItem, index) in suffix" :key="index" :src="prefix + dashboardId + '/' + dashboardTitle + suffixItem" class="w-full h-full p-2 pb-1" frameborder="0"></iframe>
</template>
