<template>
    <div>
        <h3>{{ exercise.title }}</h3>
        <p> Technologia - {{ exercise.language }}</p>
        <p> Poziom zaawansowania - {{ exercise.level }}</p>
        <p> Treść: <br> {{ exercise.content}}</p>
    </div>
</template>
<script>
export default {
    props: ['pk'],

    computed: {
        exercise() {
            /*
                jeżeli prop 'pk' jest zbindowany, wtedy wyszukaj exercise o zbindowanym pk
                w przeciwnym przypadku wyszukaj exercise po parametrze pk z URL 
            */
            let filterParam;

            if(this.pk === null || this.pk === undefined) {
                filterParam = this.$route.params.pk
            }
            else {
                filterParam = this.pk
            }

            let contextExercise = this.$store.state.exercises.filter(exercise => exercise.pk === filterParam)
            // filter zwraca tablicę, dlatego trzeba zwrócić pierwszy obiekt explicit
            return contextExercise[0]    
        }
    }
}
</script>
<style scoped>

</style>
