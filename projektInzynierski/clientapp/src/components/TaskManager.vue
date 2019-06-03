
<template>
    <div>
        <v-container>
            <v-layout row wrap justify-center>
                <v-flex md2>
                    <v-btn to="/tasks/tasks">Zadania</v-btn>
                </v-flex>
                <v-flex md2 v-if="userType.name === 'Teacher'">
                    <v-btn to="/tasks/exercises">Ćwiczenia</v-btn>
                </v-flex>
                <v-flex md2 v-if="userType.name === 'Teacher'">
                    <v-btn to="/tasks/tests" disabled>Kolokwia</v-btn>
                </v-flex>
            </v-layout>
            <router-view></router-view>
        </v-container>
        <!--
        <ul>
            <li><router-link to="/tasks/tasks">Zadania</router-link></li>
            <li><router-link to="/tasks/exercises">Cwiczenia</router-link></li>            
            <li><router-link to="/tasks/tests">Kolokwia</router-link></li>
        </ul>
        <router-view></router-view>    
        -->
    </div>    
</template>

<script>
export default {
    computed: {
        userType() {            
            return this.$store.state.profile.userType
        }
    }
}
</script>

<style scoped>

</style>

