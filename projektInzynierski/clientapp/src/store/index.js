import Vue from 'vue'
import Vuex from 'vuex'
import axios from 'axios'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    token: "",
    isLogged: "",
    
    username: "",
    profile: {},

    groups: [],
    users: [],
    exercises: [],
    tasks: []

  },

  mutations: {
    init (state) {
      state.token = localStorage.getItem('token'),
      state.isLogged = (localStorage.getItem('token') !== "null"
                        && localStorage.getItem('token') !== undefined)
      state.username = localStorage.getItem('username') || ""
      
    },

    setToken (state, payload) {
      localStorage.setItem('token', payload.token)
      state.token = localStorage.getItem('token')
      state.isLogged = (localStorage.getItem('token') != null)
      state.username = payload.username
    },

    setProfile (state, payload) {
      state.profile = payload
    },

    setUsers (state, payload) {
      state.users = payload
    },

    setGroups (state, payload) {
      console.log(payload)
      state.groups = payload
    },

    logout (state) {
      localStorage.setItem('token', null)
      state.token = null
      state.isLogged = false
      state.username = null
    },

    setExercises(state, payload) {
      console.log(payload)
      state.exercises = payload
    },

    setTasks(state, payload) {
      console.log(payload)
      state.tasks = payload
    }
  },

  actions: {
    createUser ({commit}, payload) {
      console.log("Wysylam request rejestracji")

      axios.post("http://localhost:8000/users/", payload)
           .then(response => console.log(response.data))
           .catch(error => console.log(error.response))
    },

    loginUser ({commit, dispatch}, payload) {
      console.log("Wysylam request logowania");

      return new Promise((resolve, reject) => {
        axios.post("http://localhost:8000/token/", payload)
           .then(response => {
             console.log(response.data.access);
             commit('setToken', {
               token: response.data.access,
               username: payload.username
             });
             dispatch('setLoggedUserData')

             resolve()
           })
           .catch(error => {            
             console.log(error.response);
             reject()
           })
      }
      )      
    },

    setLoggedUserData({commit, state}) {
      console.log("Wysylam request logowania");

      return new Promise((resolve, reject) => {
        axios.get("http://localhost:8000/profile/" + state.username)
           .then(response => {
             console.log(response.data);
             commit('setProfile', response.data)
             resolve()
           })
           .catch(error => {            
             console.log(error.response);
             reject()
           })
      })
    },

    getAllUsers({commit}, payload) {
      console.log("Wysylam zadanie pobrania userow!");

      return new Promise((resolve, reject) => {
        axios.get('http://localhost:8000/users/')
             .then((response) => {
               commit('setUsers', response.data)
               resolve();
             })
             .catch(() => {
               console.log("Blad pobierania userow");
               reject();
             })
      })
    },

    getAllStudents({commit}, payload) {
      console.log("Wysylam zadanie pobrania studentow!");

      return new Promise((resolve, reject) => {
        axios.get('http://localhost:8000/students/')
             .then((response) => {
               commit('setUsers', response.data)
               resolve();
             })
             .catch(() => {
               console.log("Blad pobierania userow");
               reject();
             })
      })
    },

    getAllGroups ({commit}, payload) {
      console.log("Wysylam zadanie wyswietlenia grup!")

      return new Promise((resolve, reject) => {
        let authHeader = "Bearer " + this.state.token;
        axios.get("http://localhost:8000/groups/", {headers: {
          'Authorization': authHeader
        }})
           .then((response) => {
              commit('setGroups', response.data)
              resolve()
           })
           .catch(() => {
            alert("Blad pobierania grup")
            reject()
           })
      })      
    },

    createGroup ({commit}, payload) {
      return new Promise((resolve, reject) => {
        let authHeader = "Bearer " + this.state.token;

        axios.post("http://localhost:8000/groups/", {
          params: payload},
          {headers: {
          'Authorization': authHeader
        }})
          .then((response) => {
            resolve(response)
          })
          .catch((error) => {
            reject(error)
          })
      })
    },

    deleteGroup({commit}, pk) {
      return new Promise((resolve, reject) => {
        let authHeader = "Bearer " + this.state.token;

        axios.delete("http://localhost:8000/groups/" + pk,
          {headers: {
          'Authorization': authHeader
        }})
          .then((response) => {
            console.log(response)
            resolve(response)
          })
          .catch((error) => {
            reject(error)
          })
      })
    },

    getAllExercises({commit}) {
      console.log("Wysylam zadanie pobrania ćwiczeń!");

      return new Promise((resolve, reject) => {
        let authHeader = "Bearer " + this.state.token;
        axios.get('http://localhost:8000/exercises/', {headers: {
          'Authorization': authHeader
        }})
             .then((response) => {
               commit('setExercises', response.data)
               resolve();
             })
             .catch(() => {
               console.log("Blad pobierania cwiczen");
               reject();
             })
      })
    },

    getAllTasks({commit}) {
      console.log("Wysylam zadanie pobrania zadania!");

      return new Promise((resolve, reject) => {
        let authHeader = "Bearer " + this.state.token;
        axios.get('http://localhost:8000/tasks/', {headers: {
          'Authorization': authHeader
        }})
             .then((response) => {
               commit('setTasks', response.data)
               resolve();
             })
             .catch(() => {
               console.log("Blad pobierania zadan");
               reject();
             })
      })
    },

    createExercise({commit}, payload) {
      return new Promise((resolve, reject) => {
        let authHeader = "Bearer " + this.state.token;

        axios.post("http://localhost:8000/exercises/", {
          params: payload},
          {headers: {
          'Authorization': authHeader
        }})
          .then((response) => {
            console.log(response.data)
            resolve(response.data)
          })
          .catch((error) => {
            reject(error)
          })
      })
    },

    createTask({commit}, payload) {
      return new Promise((resolve, reject) => {
        let authHeader = "Bearer " + this.state.token;

        axios.post("http://localhost:8000/tasks/", {
          params: payload},
          {headers: {
          'Authorization': authHeader
        }})
          .then((response) => {
            console.log(response.data)
            resolve(response.data)
          })
          .catch((error) => {
            reject(error)
          })
      })
    }
  }
})
