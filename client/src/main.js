import { createApp } from 'vue';
import { io } from 'socket.io-client';

import App from './App.vue';
import store from './store';
import vuetify from './plugins/vuetify';
import serverUrl from './mixin/url';

const socket = io(serverUrl());

// Pont entre les événements Socket.IO et les actions Vuex
socket.on('connect', () => store.dispatch('scale/WS_connect', socket));
socket.on('disconnect', () => store.dispatch('scale/WS_disconnect'));
socket.on('scale_status', (data) => store.dispatch('scale/WS_scale_status', data));
socket.on('error', (data) => store.dispatch('scale/WS_error', data));

const app = createApp(App);

// Rendre le socket accessible via this.$socket dans les composants (Options API)
app.config.globalProperties.$socket = socket;

app.use(store);
app.use(vuetify);
app.mount('#app');
