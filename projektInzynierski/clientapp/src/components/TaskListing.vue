<template>
    <div>
        <span><router-link to="/tasks/">Utwórz zadanie</router-link></span><br><br>
        Zadania:
        <ul>
            <li v-for="task in tasks" :key="task"> 
                {{ task.pk }} - {{ task.taskType.name  }}  - 
                <span @click="showTaskDetails(task)">Podgląd</span>
            </li>
        </ul>
    </div>    
</template>

<script>
export default {
    created() {
        this.$store.dispatch('getAllTasks')
    },

    methods: {
        showTaskDetails(task) {
            this.$router.push({name: 'TaskDetails', params: {pk: task.pk}})
        }    
    },

    computed: {
        tasks() {
            return this.$store.state.tasks
        }
    }
}
</script>

<style scoped>

</style>
