<template>
  <v-col
    class="pa-0 ma-0"
    style="height: 100vh"
  >
    <v-dialog
      v-if="selectedProduct"
      v-model="showDialog"
      max-width="50%"
    >
      <Product :product="selectedProduct" selected @cancel="cancelSelection"/>
    </v-dialog>
    <v-container
      v-if="inProgress"
      class="d-flex flex-column justify-center text-center"
      style="height: 100%; width: 100%; align-items: center"
    >
      <h2 class="pa-6">
        La mise à jour des produits peut prendre un certain temps.<br/>
        Merci de patienter.
      </h2>
      <v-progress-circular
        indeterminate
        :size="100"
        :width="7"
        color="primary"
      />
    </v-container>
    <v-card v-else-if="bagsOfProducts.length > 0" variant="flat" style="height: 100%">
      <v-card-actions class="justify-space-around" style="height: 10%">
        <v-btn
          variant="outlined"
          size="x-large"
          @click="prev"
        >
          <v-icon>mdi-chevron-left</v-icon>
        </v-btn>
        <v-item-group
          v-model="onBoarding"
          class="text-center d-flex justify-space-around"
          mandatory
          style="width: 100%"
        >
          <v-item
            v-for="n in bagsOfProducts.length"
            :key="`btn-${n}`"
            v-slot="{ isSelected, toggle }"
          >
            <v-btn
              :active="isSelected"
              rounded
              @click="toggle"
            >
              <v-icon>mdi-record</v-icon>
              {{bagsOfProducts[n-1][0][0] ? bagsOfProducts[n-1][0][0].name.substring(0, 2) : ''}}
            </v-btn>
          </v-item>
        </v-item-group>
        <v-btn
          variant="outlined"
          size="x-large"
          @click="next"
        >
          <v-icon>mdi-chevron-right</v-icon>
        </v-btn>
      </v-card-actions>
      <v-window v-model="onBoarding" style="height: 85%">
        <v-window-item
          v-for="(page, p) in bagsOfProducts"
          :key="`page-${p}`"
          style="height: 100%"
        >
          <v-card
            style="height: 100%"
            variant="flat"
            class="d-flex flex-column">
            <v-row
              v-for="(row, r) in page"
              :key="`row-${r}`"
              class="pa-0 ma-0"
              :style="`height: ${100/rowsNb}%`"
            >
              <v-col
                v-for="(product, c) in row"
                :key="`col-${c}`"
                class="pa-0 ma-0"
              >
                <div
                  v-if="product"
                  class="pa-0 ma-0 product-item"
                  style="height: 100%; cursor: pointer;"
                  @click="selectProduct(product)"
                >
                  <Product :product="product"/>
                </div>
              </v-col>
            </v-row>
          </v-card>
        </v-window-item>
      </v-window>
    </v-card>
  </v-col>
</template>

<script>

import Product from './Product.vue';

export default {
  name: 'Products',
  components: {
    Product,
  },
  props: {
    filter: String,
    productsCategory: String,
  },
  data: () => ({
    selectedProduct: null,
    showDialog: false,
    onBoarding: 0,
    columnsNb: 4,
    rowsNb: 4,
  }),
  watch: {
    productsCategory() {
      this.onBoarding = 0;
    },
  },
  methods: {
    next() {
      if (this.onBoarding + 1 === this.bagsOfProducts.length) {
        this.onBoarding = 0;
      } else {
        this.onBoarding += 1;
      }
    },
    prev() {
      if (this.onBoarding - 1 < 0) {
        this.onBoarding = this.bagsOfProducts.length - 1;
      } else {
        this.onBoarding -= 1;
      }
    },
    selectProduct(product) {
      this.selectedProduct = product;
      this.showDialog = true;
    },
    cancelSelection() {
      this.$emit('clearFilter');
      this.selectedProduct = null;
      this.showDialog = false;
    },
  },
  computed: {
    bagsOfProducts() {
      const nbProductsByPage = this.columnsNb * this.rowsNb;
      const nbPages = Math.ceil(this.products.length / nbProductsByPage);
      const bagsOfProducts = new Array(nbPages);
      for (let p = 0; p < bagsOfProducts.length; p += 1) {
        bagsOfProducts[p] = new Array(this.rowsNb);
        for (let r = 0; r < this.rowsNb; r += 1) {
          bagsOfProducts[p][r] = new Array(this.columnsNb);
        }
      }
      this.products.forEach((product, i) => {
        const p = Math.floor(i / nbProductsByPage);
        const r = Math.floor((i % nbProductsByPage) / this.columnsNb);
        const c = i % this.columnsNb;
        bagsOfProducts[p][r][c] = product;
      });
      return bagsOfProducts;
    },
    products() {
      let { products } = this.$store.state.products;
      if (this.filter) {
        products = products.filter((product) => {
          if (String(product.id).startsWith(this.filter)) {
            return true;
          }
          const name = product.name.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
          const words = this.filter.toLowerCase().split(' ');
          for (let i = 0; i < words.length; i += 1) {
            const word = words[i];
            if (!name.includes(word.toLowerCase())) {
              return false;
            }
          }
          return true;
        });
      }
      if (this.productsCategory) {
        products = products.filter((product) => product.category === this.productsCategory);
      }
      return products;
    },
    inProgress() {
      return this.$store.state.products.inProgress;
    },
  },
};
</script>

<style>
  .product-item {
    width: 20vw;
    height: 20vh;
  }
  .v-window__container {
    height: 100% !important;
  }
</style>
