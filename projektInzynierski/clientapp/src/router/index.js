import Vue from 'vue'
import Router from 'vue-router'
import StartSite from '@/components/StartSite'
import LoginForm from '@/components/LoginForm'
import RegisterForm from '@/components/RegisterForm'
import GroupListing from '@/components/GroupListing'
import GroupCreator from '@/components/GroupCreator'

Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/',
      name: 'App',
      component: StartSite
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
    {
      path: '/groups/new',
      component: GroupCreator
    }
  ],
  mode: 'history'
})
