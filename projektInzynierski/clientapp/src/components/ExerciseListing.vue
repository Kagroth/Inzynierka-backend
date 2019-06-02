<template>
    <div>
        <span><router-link to="/tasks/newExercise">Utwórz ćwiczenie</router-link></span><br><br>
        Ćwiczenia:
        <ul>
            <li v-for="exercise in exercises" :key="exercise"> {{ exercise.title }}  - <span @click="showExerciseDetails(exercise)">Podgląd</span></li>
        </ul>
    </div>    
</template>

<script>
export default {
    created() {
        this.$store.dispatch('getAllExercises')
    },

    methods: {
        showExerciseDetails(exercise) {
            this.$router.push({name: 'ExerciseDetails', params: {pk: exercise.pk}})
        }    
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
