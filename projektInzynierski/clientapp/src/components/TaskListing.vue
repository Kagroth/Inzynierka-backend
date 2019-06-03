<template>
  <div>
    <v-container>
      <v-layout row wrap justify-space-around border>
        <v-flex md6 offset-md2>
          <h2>Moje zadania</h2>
        </v-flex>
        <v-flex md2 v-if="userType.name === 'Teacher'">
          <v-btn to="/tasks/newTask" color="success" small>Utwórz zadanie</v-btn>
        </v-flex>
      </v-layout>
      <v-divider></v-divider>
      <v-layout row wrap justify-space-around v-for="task in tasks" :key="task" mt-4>
        <v-flex md6 offset-md2>
          <h3>{{ task.title }}</h3>
        </v-flex>
        <v-flex md2>
          <v-btn @click="showTaskDetails(task)" color="primary" small>Szczegóły</v-btn>
        </v-flex>
      </v-layout>
    </v-container>
    <!--
    <span>
      <router-link to="/tasks/newTask">Utwórz zadanie</router-link>
    </span>
    <br>
    <br>Zadania:
    <ul>
      <li v-for="task in tasks" :key="task">
        {{ task.pk }} - {{ task.title }} - {{ task.taskType.name }} -
        <span
          @click="showTaskDetails(task)"
        >Podgląd</span>
      </li>
    </ul>
    -->
  </div>
</template>

<script>
export default {
  created() {
    this.$store.dispatch("getAllTasks")
  },

  methods: {
    showTaskDetails(task) {
      this.$router.push({ name: "TaskDetails", params: { pk: task.pk } })
    }
  },

  computed: {
    tasks() {
      return this.$store.state.tasks
    },

    userType() {
      return this.$store.state.profile.userType
    }
  }
};
</script>

<style scoped>
</style>
