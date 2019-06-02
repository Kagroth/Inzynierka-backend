<template>
  <div>
    <v-container>
      <v-layout row wrap justify-space-around border>
        <v-flex md6 offset-md2>
          <h2>Moje ćwiczenia</h2>
        </v-flex>
        <v-flex md2>
          <v-btn to="/tasks/newExercise" color="success" small>Utwórz ćwiczenie</v-btn>
        </v-flex>
      </v-layout>
      <v-divider></v-divider>
      <v-layout row wrap justify-space-around v-for="exercise in exercises" :key="exercises" mt-4>
        <v-flex md6 offset-md2>
          <h3>{{ exercise.title }}</h3>
        </v-flex>
        <v-flex md2>
          <v-btn @click="showExerciseDetails(exercise)" color="primary" small>Szczegóły</v-btn>
        </v-flex>
      </v-layout>
    </v-container>
    <!--
        <span><router-link to="/tasks/newExercise">Utwórz ćwiczenie</router-link></span><br><br>
        Ćwiczenia:
        <ul>
            <li v-for="exercise in exercises" :key="exercise"> {{ exercise.title }}  - <span @click="showExerciseDetails(exercise)">Podgląd</span></li>
        </ul>
    -->
  </div>
</template>

<script>
export default {
  created() {
    this.$store.dispatch("getAllExercises");
  },

  methods: {
    showExerciseDetails(exercise) {
      this.$router.push({
        name: "ExerciseDetails",
        params: { pk: exercise.pk }
      });
    }
  },

  computed: {
    exercises() {
      return this.$store.state.exercises;
    }
  }
};
</script>

<style scoped>
</style>
