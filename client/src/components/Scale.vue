<template>
  <v-container
    v-if="healthy && connected"
    class="scale d-flex flex-column pa-0 ma-0 align-self-center justify-space-between"
  >
    <v-spacer></v-spacer>
    <v-row>
      <v-col>
        <h2 :class="weight>0?'text-white text-right':'text-orange text-right'">Poids :</h2>
      </v-col>
      <v-col>
        <h2 :class="weight>0?'text-white':'text-orange'">{{ Number((weight).toFixed(3)) }}</h2>
      </v-col>
    </v-row>
    <v-row>
      <v-col>
        <h3 :class="tare>0?'text-orange text-right':'text-white text-right'">Tare :</h3>
      </v-col>
      <v-col>
        <h3 :class="tare>0?'text-orange':'text-white'">{{ Number((tare).toFixed(3)) }}</h3>
      </v-col>
    </v-row>
    <v-divider color="white"></v-divider>
  </v-container>
  <v-container
    v-else
    class="scale d-flex flex-column pa-0 ma-0 align-self-center justify-space-between"
  >
    <v-spacer></v-spacer>
    <v-row>
      <h1 class="text-orange text-center">Balance non connectée</h1>
    </v-row>
    <v-divider color="white"></v-divider>
  </v-container>
</template>

<script>
export default {
  name: 'Scale',
  computed: {
    weight() {
      return this.$store.state.scale.weight;
    },
    tare() {
      return this.$store.state.scale.tare;
    },
    healthy() {
      return this.$store.state.scale.healthy;
    },
    connected() {
      return this.$store.state.scale.connected;
    },
  },
};
</script>

<style scoped>
 .scale {
    height: 100%;
 }
</style>
