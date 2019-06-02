<template>
  <div>
    <v-form>
      <v-container>
        <v-layout row wrap>
          <v-flex xs12 md5 offset-md4>
            <v-text-field :type="text" v-model="form.groupName" label="Nazwa grupy" required></v-text-field>
          </v-flex>
          <v-flex xs12 md4 offset-md4>
            <v-select :items="users" v-model="currentSelectedUser">
                <template slot="item" slot-scope="data"> <!-- ten slot odpowiada za to jak obiekty sa wyswietlane w liscie -->
                    {{ data.item.first_name }} {{ data.item.last_name }}
                </template>
                <template slot="selection" slot-scope="data"> <!-- ten slot odpowiada za to jak wybrany obiekt jest wyswietlany -->
                    {{ data.item.first_name }} {{ data.item.last_name }}
                </template>
            </v-select>
          </v-flex>
          <v-flex xs12 md3>
            <v-btn color="primary" @click="addUser">Dodaj</v-btn>
          </v-flex>
          <v-flex xs12 md4 offset-md4>
            <v-btn color="primary" @click="createGroup">Utwórz</v-btn>
          </v-flex>
        </v-layout>       
        
        <v-layout row wrap>
            <v-flex md4 offset-md4>
                <h3>Wybrani użytkownicy: </h3>
            </v-flex>
            <v-flex md4 offset-md4 :key="selectedUser" v-for="selectedUser in form.selectedUsers">
                {{ selectedUser.first_name }} {{ selectedUser.last_name }}
            </v-flex>
        </v-layout>
      </v-container>
    </v-form>
    <!--
        <form>
            <input type="text" placeholder="Nazwa grupy" v-model="form.groupName"/><br><br>
            <select v-model="currentSelectedUser">
                <option :key="user" v-for="user in users" :value="user.username">
                     {{ user.first_name }} {{ user.last_name }} - {{ user.username }}
                </option>
            </select>
            <input type="button" value="Dodaj" @click="addUser"/><br>            
            <input type="submit" value="Utwórz" @click="createGroup"/>
        </form>
        <div>
            <p>Wybrani użytkownicy: </p>
            <ul>
                <li :key="selectedUser" v-for="selectedUser in form.selectedUsers">
                    {{ selectedUser.first_name }} {{ selectedUser.last_name }} - {{ selectedUser.username }}
                </li>
            </ul>
        </div>
    -->
  </div>
</template>

<script>
export default {
  data() {
    return {
      currentSelectedUser: null,
      form: {
        groupName: "",
        selectedUsers: []
      }
    };
  },

  methods: {
    addUser() {
      if(this.currentSelectedUser === null) {
          return
      }

      if (this.form.selectedUsers.includes(this.currentSelectedUser)) {
          return
      }

      this.form.selectedUsers.push(this.currentSelectedUser);
    },

    createGroup(event) {
      event.preventDefault();

      if (this.form.groupName === "") {
        alert("Nie podano nazwy grupy!");
        return;
      }

      this.$store
        .dispatch("createGroup", this.form)
        .then(response => {
          let message = response.data.message;
          alert(message);

          if (message === "Grupa została utworzona")
            this.$router.push("/groups");
        })
        .catch(() => {
          console.log("Nie udalo sie utworzyc grupy");
          alert("Nie udalo sie utworzyc grupy");
        });
    }
  },

  created() {
    this.$store
      .dispatch("getAllStudents")
      .then(() => {
        console.log("Pobrano userow!");
        console.log(this.$store.state.users)
      })
      .catch(() => {
        console.log("Nie udalo sie pobrac userow");
      });
  },

  computed: {
    users() {
      return this.$store.state.users;
    }
  }
};
</script>

<style scoped>
</style>
