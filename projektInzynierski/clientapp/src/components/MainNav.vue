<template>
    <div>
        <ul v-if="!isLogged">
            <li><router-link to="/login">Logowanie</router-link></li>
            <li><router-link to ="/register">Rejestracja</router-link></li>
        </ul>
        <ul v-else>
            <li><router-link to="/tasks">Zarządzanie zadaniami</router-link></li>
            <li><router-link to="/groups">Grupy</router-link></li>
            <li @click="logout">Wyloguj</li>
        </ul>
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
