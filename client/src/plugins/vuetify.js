import 'vuetify/styles';
import { createVuetify } from 'vuetify';
import * as components from 'vuetify/components';
import * as directives from 'vuetify/directives';
import { fr } from 'vuetify/locale';
import '@mdi/font/css/materialdesignicons.css';

export default createVuetify({
  components,
  directives,
  locale: {
    locale: 'fr',
    messages: { fr },
  },
  theme: {
    themes: {
      light: {
        colors: {
          primary: '#445448',
        },
      },
    },
  },
});
