<template>
  <div>
    <v-container>
      <v-layout row wrap justify-space-around border>
        <v-flex md6 offset-md2>
          <h2>Moje Grupy</h2>
        </v-flex>
        <v-flex md2 v-if="userType.name === 'Teacher'">
          <v-btn to="/newGroup" color="success" small>
            Utwórz grupę
          </v-btn>
        </v-flex>
      </v-layout>
      <v-divider></v-divider>
      <v-layout row wrap justify-space-around v-for="group in groups" :key="group" mt-4>
        <v-flex md6 offset-md2>
          <h3>{{ group.name }}</h3>
        </v-flex>
        <v-flex md2>
          <v-btn @click="showGroupDetails(group)" color="primary" small>
            Szczegóły
          </v-btn>
        </v-flex>        
      </v-layout>
    </v-container>
    <!--
    <p><router-link to="/newGroup">Utwórz grupe</router-link></p>
    <h2>Grupy:</h2>
    <ul>
      <li :key="group" v-for="group in groups"> 
        <span>{{ group.name }}</span> - <span @click="showGroupDetails(group)">Podgląd</span></li>
    </ul>
    -->
  </div>
</template>

<script>
import Group from '@/components/Group'


export default {
    components: {
      'group': Group
    },

    data() {
        return {
        }
    },

    methods: {
      showGroupDetails(group) {
        this.$router.push({name: 'GroupDetails', params: {name: group.name, group: group}})
      }
    },

    computed: {
      groups() {
        return this.$store.state.groups
      },

      userType() {
         return this.$store.state.profile.userType
      }
    },

    created() {
      this.$store.dispatch('getAllGroups').then(
        () => { 
          this.groups = this.$store.state.groups
        }
      )
      .catch(
        () => { 
          console.log("Nie udalo sie pobrac grup")
          alert("Nie udalo sie zwrocic grup!")
        }
      )
    }
    
}
</script>

<style scoped>

</style>
