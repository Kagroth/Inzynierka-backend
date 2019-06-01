<template>
    <div>
        <span><router-link to="/tasks/newExercise">Utwórz ćwiczenie</router-link></span><br><br>
        Ćwiczenia:
        <ul>
            <li v-for="exercise in exercises" :key="exercise"> {{ exercise.title }}  - <span>Podgląd</span></li>
        </ul>
    </div>    
</template>

<script>
export default {
    created() {
        this.$store.dispatch('getAllExercises')
    },

    computed: {
        exercises() {
            return this.$store.state.exercises
        }
    }
}
</script>

<style scoped>

</style>
