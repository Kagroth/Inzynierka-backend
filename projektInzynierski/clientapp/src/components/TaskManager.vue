
<template>
    <div>Zarzadzanie taskami
        <ul>
            <li><router-link to="/tasks/exercises">Cwiczenia</router-link></li>
            
            <li><router-link to="/tasks/tests">Kolokwia</router-link></li>
        </ul>
        <router-view></router-view>    
    </div>    
</template>

<script>
export default {
    
}
</script>

<style scoped>

</style>

