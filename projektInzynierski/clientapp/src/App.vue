<template>
  <div id="app">
    <main-nav/>
    <router-view/>
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
