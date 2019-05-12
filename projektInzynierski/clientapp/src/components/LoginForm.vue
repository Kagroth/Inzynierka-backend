<template>
    <div>
        <router-link to="/">Strona glowna</router-link><br><br>
        <form>
            <input type="text" placeholder="Nazwa uzytkownika" v-model="form.username"/><br>
            <input type="password" placeholder="haslo" v-model="form.password"/><br>
            <input type="submit" value="Zaloguj" @click="loginUser"/>
        </form>
    </div>
</template>

<script>

export default {
    data() {
        return {
            form: {
                username: "",
                password: ""

            }   
        }
    },

    methods: {
        loginUser(event) {
            event.preventDefault();
            
            this.$store.dispatch('loginUser', this.form)
                       .then(() => {
                           alert("Zalogowano!");
                           console.log("Przekierowuje do /groups!")
                           this.$router.push('/groups');
                           })
                       .catch(() => {alert("Niepowodzenie logowania")});           
            
        }
    }
}

</script>

<style scoped>

</style>
