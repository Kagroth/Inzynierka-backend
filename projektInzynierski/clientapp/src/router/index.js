import Vue from 'vue'
import Router from 'vue-router'
import MainNav from '@/components/MainNav'
import LoginForm from '@/components/LoginForm'
import RegisterForm from '@/components/RegisterForm'
import GroupListing from '@/components/GroupListing'

Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/',
      name: 'App',
      component: MainNav
    },
    {
      path: '/login',
      component: LoginForm
    },
    {
      path: '/register',
      component: RegisterForm
    },
    {
      path: '/groups',
      component: GroupListing
    },
  ],
  mode: 'history'
})
