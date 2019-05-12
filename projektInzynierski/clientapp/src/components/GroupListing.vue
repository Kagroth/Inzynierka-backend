<template>
  <div>
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
          alert("Wszystkie grupy zwrocone!")
          this.groups = this.$store.state.groups
          }
      )
      .catch(
        () => { alert("Nie udalo sie zwrocic grup!")}
      )
    }
    
}
</script>

<style scoped>

</style>
