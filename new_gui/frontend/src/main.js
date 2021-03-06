import Vue from 'vue'
import App from './App.vue'
import vuetify from './plugins/vuetify'
import router from './router'
import store from './store'

Vue.config.productionTip = false
require('./css/neo4jd3.css')
// require('./css/leaflet.css')
new Vue({
  vuetify,
  router, 
  store,
  render: h => h(App)
}).$mount('#app')
