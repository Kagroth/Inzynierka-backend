<template>
  <div id="app">
    <v-app>
      <v-content>
        <main-nav/>
        <router-view/>
      </v-content>
    </v-app>
  </div>
</template>

<script>
import MainNav from '@/components/MainNav'
export default {
  components: {
    'main-nav': MainNav
  },

  name: 'App'
}
</script>

<style>
</style>
