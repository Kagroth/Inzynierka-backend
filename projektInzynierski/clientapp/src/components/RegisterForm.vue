<template>
  <div>
    <router-link to="/">Strona glowna</router-link>
    <br>
    <br>
    <form>
      <input type="text" placeholder="Imie">
      <br>
      <input type="text" placeholder="Nazwisko">
      <br>
      <input type="text" placeholder="Nazwa uzytkownika" v-model="form.username">
      <br>
      <input type="email" placeholder="email">
      <br>
      <input type="password" placeholder="Haslo">
      <br>
      <input type="password" placeholder="Powtorz haslo">
      <br>
      <input type="submit" value="Zarejestruj" @click="registerUser">
    </form>
  </div>
</template>

<script>
export default {
  data() {
    return {
      form: {
        username: ""
      }
    };
  },

  methods: {
    registerUser(event) {
      event.preventDefault();
      console.log("Username in component: " + this.form.username);
      this.$store.dispatch("createUser", {username: this.form.username});
    }
  }
};
</script>

<style scoped>
</style>
