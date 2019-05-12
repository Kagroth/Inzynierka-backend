<template>
  <div>
    <h3>{{group.name}}</h3>
    <ol>
      <li :key="user" v-for="user in group.users">
        <p>Imie i nazwisko: {{user.first_name}} {{user.last_name}}</p>
        <p>Email: {{user.email}}</p>
        <p>Nazwa użytkownika: {{user.username}}</p>
      </li>
    </ol>
  </div>
</template>

<script>
export default {
  props: ['group'],
  
  data() {
    return {
    };
  },

  methods: {}
};
</script>

<style scoped>
</style>
