import Vue from 'vue'
import Vuex from 'vuex'
import axios from 'axios'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    token: localStorage.getItem('token'),
    isLogged: (this.token != null),

    groups: []

  },

  mutations: {
    setToken (state, payload) {
      state.token = payload.token;
      state.isLogged = true
    },

    setGroups (state, payload) {
      console.log(payload)
      state.groups = payload;
    }
  },

  actions: {
    createUser ({commit}, payload) {
      console.log("Wysylam request rejestracji")

      axios.post("http://localhost:8000/users/", payload)
           .then(response => console.log("Sukces" + response))
           .catch(error => console.log(error.response))
    },

    loginUser ({commit}, payload) {
      console.log("Wysylam request logowania");

      return new Promise((resolve, reject) => {
        axios.post("http://localhost:8000/token/", payload)
           .then(response => {
             console.log(response.data.access);
             commit('setToken', {
               token: response.data.access
             });
             
             resolve()
           })
           .catch(error => {            
             console.log(error.response);
             reject()
           })
      }
      )      
    },

    getAllGroups ({commit}, payload) {
      console.log("Wysylam rzadanie wyswietlenia grup!")

      return new Promise((resolve, reject) => {
        axios.get("http://localhost:8000/groups/")
           .then((response) => {
              commit('setGroups', response.data)
              resolve()
           })
           .catch(() => {
            alert("Blad pobierania grup")
            reject()
           })
      })      
    }
  }
})
