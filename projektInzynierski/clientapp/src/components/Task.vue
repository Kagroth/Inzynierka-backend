<template>
    <div>
        Przykladowy task
        <!--
        <h3>{{ exercise.title }}</h3>
        <p> Technologia - {{ exercise.language }}</p>
        <p> Poziom zaawansowania - {{ exercise.level }}</p>
        <p> Treść: <br> {{ exercise.content}}</p>-->
    </div>
</template>
<script>
export default {
    computed: {
        /*
        exercise() {
            let contextExercise = this.$store.state.exercises.filter(exercise => exercise.pk === this.$route.params.pk)
            // filter zwraca tablicę, dlatego trzeba zwrócić pierwszy obiekt explicit
            return contextExercise[0]    
        }*/
    }
}
</script>
<style scoped>

</style>
