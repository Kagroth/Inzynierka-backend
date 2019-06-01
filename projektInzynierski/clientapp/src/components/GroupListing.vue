<template>
  <div>
    <p><router-link to="/newGroup">Utwórz grupe</router-link></p>
    <h2>Grupy:</h2>
    <ul>
      <li :key="group" v-for="group in groups"> 
        <span>{{ group.name }}</span> - <span @click="showGroupDetails(group)">Podgląd</span></li>
    </ul>
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
