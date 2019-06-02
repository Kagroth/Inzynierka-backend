<template>
  <div>
    <!--<router-link to="/">Strona glowna</router-link>-->
    <br>
    <br>
    <v-form>
      <v-container>
        <v-layout row wrap>
          <v-flex md4 offset-md4>
            <v-text-field :type="text" v-model="form.firstname" label="Imię" required></v-text-field>
          </v-flex>
          <v-flex md4 offset-md4>
            <v-text-field :type="text" v-model="form.lastname" label="Nazwisko" required></v-text-field>
          </v-flex>
          <v-flex md4 offset-md4>
            <v-text-field :type="text" v-model="form.username" label="Nazwa użytkownika" required></v-text-field>
          </v-flex>
          <v-flex md4 offset-md4>
            <v-text-field :type="email" v-model="form.email" label="Email" required></v-text-field>
          </v-flex>
          <v-flex md4 offset-md4>
            <v-text-field type="password" v-model="form.password" label="Hasło" required></v-text-field>
          </v-flex>
          <v-flex md4 offset-md4>
            <v-text-field type="password" v-model="form.passwordRepeat" label="Powtórz hasło" required></v-text-field>
          </v-flex>
          <v-flex md4 offset-md4>
            <v-select :items="userTypes" label="Rodzaj użytkownika"></v-select>
          </v-flex>
          <v-flex md4 offset-md4>
            <v-btn color="primary" @click="registerUser" class="ma-0">
              Utwórz konto
            </v-btn>
          </v-flex>
        </v-layout>
      </v-container>
    </v-form>
    <form>
      <input type="text" placeholder="Imie" v-model="form.firstname">
      <br>
      <input type="text" placeholder="Nazwisko" v-model="form.lastname">
      <br>
      <input type="text" placeholder="Nazwa uzytkownika" v-model="form.username">
      <br>
      <input type="email" placeholder="email" v-model="form.email">
      <br>
      <input type="password" placeholder="Haslo" v-model="form.password">
      <br>
      <input type="password" placeholder="Powtorz haslo" v-model="form.passwordRepeat">
      <br>
      <select v-model="form.userType">
        <option>Student</option>        
        <option>Nauczyciel</option>
      </select><br>
      <input type="submit" value="Zarejestruj" @click="registerUser">
    </form>
  </div>
</template>

<script>
export default {
  data() {
    return {
      userTypes: ['Student', 'Nauczyciel'],
      form: {
        firstname: "",
        lastname: "",
        username: "",
        email: "",
        password: "",
        passwordRepeat: "",
        userType: ""
      }
    };
  },

  methods: {
    registerUser(event) {
      event.preventDefault();

      for(let field in this.form) {
        if(this.form[field] === "") {
          alert("Nie podano wszystkich danych!")
          return
        }
      }

      if(this.form.password !== this.form.passwordRepeat) {
        alert("Hasla sie roznia!")
        return
      }

      console.log("Username in component: " + this.form.username)
      this.$store.dispatch("createUser", this.form)
    }
  }
};
</script>

<style scoped>
</style>
