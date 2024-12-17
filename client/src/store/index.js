import Vue from 'vue';
import Vuex from 'vuex';
import antifreeze from './antifreeze';
import products from './products';
import scale from './scale';
import ticket from './ticket';

Vue.use(Vuex);

export default new Vuex.Store({
  modules: {
    antifreeze,
    products,
    scale,
    ticket,
  },
  strict: process.env.NODE_ENV !== 'production',
});
