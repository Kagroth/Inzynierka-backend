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
      console.log("username in store: ")
      console.log(payload.username)

      fetch('http://localhost:8000/users/').then(
        response => {
          return response.json()
        }).then(data => {
          for(let user of data) {
            console.log(user);
          }
        })
      .catch(response => {
        console.log(response)
      })
    }
  }
})
