<template>
  <div>
    <p><router-link to="/groups/new">Utwórz grupe</router-link></p>
    <h2>Grupy:</h2>
    <group :key="group" v-for="group in groups" v-bind:group="group"/>
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
          alert("Nie udalo sie zwrocic grup!")}
      )
    }
    
}
</script>

<style scoped>

</style>
