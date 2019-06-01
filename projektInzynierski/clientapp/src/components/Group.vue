<template>
  <div>
    <h3>{{ group.name }}</h3>
    <span>Usuń</span>
    <ol>
      <li :key="user" v-for="user in group.users">
        <p>Imie i nazwisko: {{user.first_name}} {{ user.last_name}}</p>
        <p>Email: {{user.email}}</p>
        <p>Nazwa użytkownika: {{user.username}}</p>
      </li>
    </ol>
  </div>
</template>

<script>
export default {
  methods: {},

  computed: {
    group() {
      let contextGroup = this.$store.state.groups.filter(group => group.name === this.$route.params.name)
      // filter zwraca tablicę, dlatego trzeba zwrócić pierwszy obiekt explicit
      return contextGroup[0]
    }
  }
};
</script>

<style scoped>
</style>
