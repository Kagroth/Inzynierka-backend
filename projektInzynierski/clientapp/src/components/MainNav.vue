<template>
    <div>
        <v-toolbar>
            <v-toolbar-items>
                <v-btn flat to="/">
                    Strona główna
                </v-btn>
            </v-toolbar-items>
            <v-spacer></v-spacer>            
            <v-toolbar-items v-if="!isLogged">
                <v-btn flat to="/login">
                    Logowanie
                </v-btn>
                <v-btn flat to="/register">
                    Rejestracja
                </v-btn>
            </v-toolbar-items>
            <v-toolbar-items v-else>
                <v-btn flat to="/tasks">Zarządzanie zadaniami</v-btn>
                <v-btn flat to="/groups">Grupy</v-btn>
                <v-btn flat @click="logout">Wyloguj</v-btn>
            </v-toolbar-items>
        </v-toolbar>
        <!--
        <ul v-if="!isLogged">
            <li><router-link to="/login">Logowanie</router-link></li>
            <li><router-link to ="/register">Rejestracja</router-link></li>
        </ul>
        <ul v-else>
            <li><router-link to="/tasks">Zarządzanie zadaniami</router-link></li>
            <li><router-link to="/groups">Grupy</router-link></li>
            <li @click="logout">Wyloguj</li>
        </ul-->
    </div>
</template>

<script>

export default {
    computed: {
        isLogged() {
            return this.$store.state.isLogged;
        }
    },

    methods: {
        logout() {
            this.$store.commit('logout');
            this.$router.push('/');
        }
    }
}
</script>

<style scoped>

</style>
