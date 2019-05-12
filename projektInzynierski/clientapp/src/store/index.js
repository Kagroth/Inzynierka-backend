import Vue from 'vue'
import Vuex from 'vuex'
import axios from 'axios'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    token: localStorage.getItem('token'),
    isLogged: (this.token != null)

  },

  mutations: {

  },

  actions: {
    createUser ({commit}, payload) {
      console.log("Wysylam request")

      axios.post("http://localhost:8000/users/", payload)
           .then(response => console.log("Sukces" + response))
           .catch(error => console.log(error.response))
    }
  }
})
