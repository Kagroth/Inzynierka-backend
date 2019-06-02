<template>   
    <div>
        <h3>Kreator zadania</h3>
        <form>
            <input type="text" name="title" placeholder="Tytul" v-model="form.title"/><br>
            
            Rodzaj: 
            <select name="taskType" v-model="form.taskType">
                <option value="Exercise">Proste</option>
                <option value="Test">Kolokwium</option>
            </select><br>
            
            <select name="exercise" v-model="form.exercise">
                <option v-for="exercise in exercises" :key="exercise" :value="exercise.pk"> {{ exercise.title }} </option>
            </select><br>
            
            Przydziel do:
            <select name="groups" v-model="selectedGroup">
                <option v-for="group in groups" :key="group" :value="group"> {{ group.name }}</option>
            </select>
            <input type="button" value="Dodaj" @click="addGroup"/><br>
            <input type="submit" value="Utworz zadanie" @click="createTask"/>
        </form><br>
        Wybrane grupy:
        <ul>
            <li v-for="group in this.form.groups" :key="group"> {{ group.name }} </li>
        </ul>
    </div>
</template>

<script>
export default {
    data() {
        return {
            selectedGroup: "",
            form: {
                title: "",
                taskType: "",
                exercise: "",
                groups: []
            }
        }
    },

    methods: {
        addGroup() {
            if(this.form.groups.includes(this.selectedGroup)) {
                return
            }
 
            this.form.groups.push(this.selectedGroup)
        },

        createTask(event) {
            event.preventDefault();
            
            for(let field in this.form) {
                if(this.form[field] === "") {
                    alert("Nie podano wszystkich danych!")
                    return
                }
            }

            console.log(this.form)

            this.$store.dispatch('createTask', this.form).then((responseData) => {
                alert(responseData.message)
            })
        }
    },

    computed: {
        exercises() {
            if(this.form.taskType === "Exercise")
                return this.$store.state.exercises
            else
                return []
        },

        groups() {
            return this.$store.state.groups
        }
    },

    created() {
        this.$store.dispatch('getAllStudents').then(() => {
            console.log("Pobrano userow!")
        })
        .catch(() => {
            console.log("Nie udalo sie pobrac userow")
        }) 
        
        this.$store.dispatch('getAllGroups').then(() => {
            console.log("Pobrano grupy!")
        }).catch(() => {
            console.log("Nie udalo sie pobrac grup")
        }),
        
        this.$store.dispatch('getAllExercises').then(() => {
            console.log("Pobrano cwiczenia!")
        }).catch(() => {
            console.log("Nie udalo sie pobrac cwiczen")
        })
    },
}
</script>

<style scoped>
