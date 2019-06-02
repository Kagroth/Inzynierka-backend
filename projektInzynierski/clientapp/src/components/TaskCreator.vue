<template>   
    <div>
        <h3>Kreator zadania</h3>
        <form>
            
        </form>
    </div>
</template>

<script>
export default {
    data() {
        return {
            form: {
            }
        }
    },

    methods: {
        createTask(event) {
            event.preventDefault();
            
            for(let field in this.form) {
                if(this.form[field] === "") {
                    alert("Nie podano wszystkich danych!")
                    return
                }
            }

            console.log(this.form)

            this.$store.dispatch('createExercise', this.form).then((responseData) => {
                alert(responseData.message)
            })
        }
    }
}
</script>

<style scoped>
