import { createStore } from 'vuex';
import products from './products';
import scale from './scale';
import ticket from './ticket';

export default createStore({
  modules: {
    products,
    scale,
    ticket,
  },
  strict: process.env.NODE_ENV !== 'production',
});
