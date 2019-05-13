<template>
    <div>
        <form>
            <input type="text" placeholder="Nazwa grupy" v-model="form.groupName"/><br><br>
            <select v-model="currentSelectedUser">
                <option :key="user" v-for="user in users" :value="user.username">
                     {{ user.first_name }} {{ user.last_name }} - {{ user.username }}
                </option>
            </select>
            <input type="button" value="Dodaj" @click="addUser"/><br>            
            <input type="submit" value="Utwórz" @click="createGroup"/>
        </form>
        <div>
            <p>Wybrani użytkownicy: </p>
            <ul>
                <li :key="selectedUser" v-for="selectedUser in form.selectedUsers">
                    {{ selectedUser.first_name }} {{ selectedUser.last_name }} - {{ selectedUser.username }}
                </li>
            </ul>
        </div>
    </div>    
</template>

<script>
export default {
    data() {
        return {
            currentSelectedUser: null,
            form: {
                groupName: "",
                selectedUsers: []
            }
        }
    }, 

    methods: {
        addUser() {
            let filteredParam = this.currentSelectedUser;
            console.log(filteredParam);

            let userToAdd = this.users.filter(user => {
                console.log("Parametr to: ")
                console.log(user)
                console.log("Parametr filtrujacy: " + filteredParam)

                if(user.username === filteredParam) {
                    return user;
                }
                else {
                    console.log("Dupa")
                }
            })

            console.log(userToAdd[0])
            console.log(this.form.selectedUsers)

            if(this.form.selectedUsers.includes(userToAdd[0]))
                return;

            this.form.selectedUsers.push(userToAdd[0]);
        },

        createGroup(event) {
            event.preventDefault();
            
            this.$store.dispatch('createGroup', this.form).then(
                () => {
                    console.log("Grupa zostala utworzona!")
                    alert("Utworzono grupe")
                    this.$router.push('/groups')
                })
                .catch(() => {
                    console.log("Nie udalo sie utworzyc grupy")
                    alert("Nie udalo sie utworzyc grupy")
                })
        }
    },

    created() {
        this.$store.dispatch('getAllUsers').then(() => {
            console.log("Pobrano userow!")
        })
        .catch(() => {
            console.log("Nie udalo sie pobrac userow")
        })    
    },

    computed: {
        users() {
            return this.$store.state.users;
        }
    },

}
</script>

<style scoped>

</style>
