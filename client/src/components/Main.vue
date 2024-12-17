<template>
  <v-container fluid>
    <v-row>
      <v-col
        cols="2"
        class="primary d-flex flex-column justify-space-around pa-0 ma-0"
        style="height: 100vh"
      >
        <v-row no-gutters class="scale-row d-flex">
          <Scale :freeze="freeze"/>
        </v-row>
        <v-row no-gutters>
          <v-btn-toggle
            v-model="productsCategory"
            color="deep-purple accent-3"
            class="filters"
            tile
            group>
            <v-container
              class="filters d-flex flex-column pa-0 ma-0 justify-space-around"
              width="100%"
            >
              <v-row v-for="category in categories"
                     :key="category"
                     style="width: 100%; justify-content: center"
                     align-content="center"
              >
                <v-btn :value="category" width="50%" height="80px">{{ category }}</v-btn>
              </v-row>
            </v-container>
          </v-btn-toggle>
        </v-row>
        <v-row class="refresh-row d-flex flex-row justify-space-around"
               no-gutters>
          <v-menu
            top
            :offset-x="true"
            :offset-y="true"
            class="white"
            v-bind:close-on-content-click="false"
          >
            <template v-slot:activator="{ on, attrs }">
              <v-btn
                v-bind="attrs"
                v-on="on"
                fab
                @click="clearFilter"
                :disabled="labels.length <= 0"
              >
                <v-icon>
                  mdi-format-list-numbered
                </v-icon>
              </v-btn>
            </template>

            <v-container
              style="height: 100%; background-color: white; width: 30vw;"
              class="pa-1 ma-0"
            >
              <v-row v-for="(label, index) in labels"
                     :key="index"
                     style="width: 100%; justify-content: center"
                     class="pa-0 ma-0"
                     align-content="center"
              >
                <v-card style="width: 100%;">
                  <v-card-title class="pa-1" style="width: 100%;">
                    <v-row class="pa-0 ma-0" style="width: 100%;">
                      <v-col
                        cols="1"
                        class="pa-0 ma-0 justify-start align-center"
                        style="height: 100%;"
                      >
                        <h5>{{ index + 1 }})</h5>
                      </v-col>
                      <v-col
                        cols="9"
                        class="pa-0 ma-0 justify-start align-center"
                        style="height: 100%;"
                      >
                        <h5>{{ label.product.name }}</h5>
                      </v-col>
                      <v-col
                        cols="2"
                        class="pa-0 ma-0 justify-start align-center"
                        style="height: 100%;"
                      >
                        <h6 class="grey--text text--darken-2" v-if="label.product.id">
                          {{ (label.weight).toFixed(3) }} / kg
                        </h6>
                        <h6 class="grey--text text--darken-2" v-else>
                          {{ label.weight }}
                        </h6>
                      </v-col>
                    </v-row>
                  </v-card-title>
                </v-card>
              </v-row>
            </v-container>
          </v-menu>
          <v-menu
            top
            :offset-x="true"
            :offset-y="true"
            class="white"
            v-bind:close-on-content-click="false"
            v-model="searchOpened"
          >
            <template v-slot:activator="{ on, attrs }">
              <v-btn
                v-bind="attrs"
                v-on="on"
                fab
                @click="clearFilter"
                :disabled="inProgress"
              >
                <v-icon>
                  mdi-magnify
                </v-icon>
              </v-btn>
            </template>

            <v-container class="pa-0 ma-0">
              <v-row class="pa-0 ma-0" align="center">
                <Keyboard ref="keyboard" @pressed="pressed" @close="searchOpened=false"/>
              </v-row>
            </v-container>
          </v-menu>
        </v-row>
        <v-row class="refresh-row d-flex flex-row justify-space-around"
               no-gutters>
          <v-btn
            @click="cutTicket"
            fab
            :disabled="inProgress"
          >
            <v-icon>
              mdi-scissors-cutting
            </v-icon>
          </v-btn>
          <v-btn
            @click="refreshProducts"
            fab
            :disabled="inProgress"
          >
            <v-icon>
              mdi-refresh
            </v-icon>
          </v-btn>
        </v-row>
        <v-divider v-if="lastSyncDate" class="white mb-6"></v-divider>
        <v-row v-if="lastSyncDate" style="max-height: 10%">
          <v-col>
            <h5 :class="isSynced?'white--text text-right':'orange--text text-right'">
              MAJ produits :
            </h5>
          </v-col>
          <v-col>
            <h5 :class="isSynced?'white--text':'orange--text'">
              {{ lastSyncDate }}
            </h5>
          </v-col>
        </v-row>
<!--
<v-row v-if="lastSyncDate" style="max-height: 10%">
  <v-col>
    <h5 :class="isSynced?'white&#45;&#45;text text-right':'orange&#45;&#45;text text-right'">
      Antifreeze:
    </h5>
  </v-col>
  <v-col>
    <h5 :class="isFreezed?'white&#45;&#45;text':'orange&#45;&#45;text'">
      {{ isFreezed?"TRUE":"FALSE" }}
    </h5>
  </v-col>
</v-row>
-->
      </v-col>
      <Products
        :filter="filter"
        :productsCategory="productsCategory"
        @clearFilter="clearFilter"
      />
    </v-row>
  </v-container>
</template>

<script>
import asEuro from '@/mixin/euro';
import print from '@/mixin/print';
import Keyboard from './Keyboard.vue';
import Products from './Products.vue';
import Scale from './Scale.vue';

export default {
  name: 'Main',
  components: {
    Keyboard,
    Products,
    Scale,
  },
  data: () => ({
    productsCategory: null,
    onlyBio: false,
    onlyVariable: false,
    filter: null,
    freeze: false,
    searchOpened: false,
  }),
  created() {
    this.refreshProducts();
  },
  watch: {
    productsCategory() {
      if (this.productsCategory) {
        this.filter = null;
      }
    },
  },
  computed: {
    labels() {
      return this.$store.state.ticket.labels;
    },
    inProgress() {
      return this.$store.state.products.inProgress;
    },
    isSynced() {
      return this.$store.state.products.synced;
    },
    isFreezed() {
      return this.$store.state.antifreeze.weights.length > 2;
    },
    lastSyncDate() {
      return this.$store.state.products.date;
    },
    categories() {
      const categories = [];
      let addOther = false;
      this.$store.state.products.products.forEach((product) => {
        const { category } = product;
        if (category === 'autre') {
          addOther = true;
        } else if (categories.indexOf(category) < 0) {
          categories.push(category);
        }
      });
      if (addOther) {
        categories.push('autre');
      }
      return categories;
    },
  },
  methods: {
    asEuro,
    refreshProducts() {
      this.$store.dispatch('products/get');
    },
    cutTicket() {
      print(
        null,
        null,
        null,
        null,
        true,
      );
      this.$store.dispatch('ticket/reset');
    },
    pressed(value) {
      if (value) {
        this.productsCategory = null;
        this.filter = value;
      } else {
        this.filter = null;
      }
    },
    clearFilter() {
      if (this.$refs.keyboard) {
        this.$refs.keyboard.resetValue();
      }
      this.filter = null;
    },
  },
};
</script>

<style scoped>
  .scale-row {
    max-height: 20%;
  }
  .refresh-row {
    max-height: 10%;
  }
  .filters {
    height: 100%;
    width: 100%;
    align-items: center;
  }
  .theme--light.v-btn--active::before {
    opacity: 0.4;
  }
</style>
