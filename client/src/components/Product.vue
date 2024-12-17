<template>
  <v-list-item-content class="pa-0 ma-0">
    <v-dialog
      v-model="printError"
      width="500"
    >
      <v-card class="text-center">
        <v-card-title class="headline red lighten-2" style="justify-content: center">
          Erreur d'impression !
        </v-card-title>

        <v-card-text class="pa-3 ma-0">
          Il semble impossible d'imprimer le ticket.<br/>
          Verifier la mise sous tention et le cablage de l'imprimante.<br/>
          Si le problème perciste, contacter le groupe informatique.<br/>
        </v-card-text>

        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="green darken-1"
            text
            @click="printError = false"
          >
            Ok
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <v-card>
      <v-card-title class="pb-1 pr-0">
        <h5>{{ product.name }}</h5>
      </v-card-title>
      <v-card-text class="pa-0 ma-0">
        <v-row class="pa-0 ma-0 pr-4">
          <v-col class="pa-0 ma-0 pl-4">
            <v-img
              v-if="product.image_medium"
              :src="'data:image/jpeg;base64,'+product.image_medium"
              :aspect-ratio="4/3"
              height="90%"
            />
            <v-img
              v-else
              src="@/assets/logo.png"
              :aspect-ratio="4/3"
              height="100%"
              class="mx-auto"
            />
          </v-col>
          <v-col
            class="pa-0 ma-0 d-flex flex-column justify-start align-center"
            style="height: 100%"
          >
            <template v-if="variableWeightProduct()">
              <h3>Id. {{ product.id }}</h3>
              <h3><br/>{{ asEuro(product.lst_price) }} / kg</h3>
            </template>
            <template v-else>
              <h3>Vendu à la pièce</h3>
              <h3><br/>{{ asEuro(product.lst_price) }}</h3>
            </template>
            <v-img
              v-if="product.bio"
              src="@/assets/bio.jpeg"
              max-height="50"
              max-width="40"
              class="ma-3"
            />
          </v-col>
          <v-col v-if="selected"
                 class="pa-0 ma-0 align-self-center" align="center">
            <v-row v-if="variableWeightProduct()">
              <v-col>
                <h2 :class="weight>0&&weight<100?'text-right':'orange--text text-right'">
                  Poids :
                </h2>
              </v-col>
              <v-col>
                <h2 :class="weight>0&&weight<100?'text-left':'orange--text'">
                  {{ Number((weight).toFixed(3)) }} kg
                </h2>
              </v-col>
            </v-row>
            <v-row v-else>
              <v-col>
                <h2 :class="weight>0&&weight<100?'text-right':'orange--text text-right'">
                  Quantité :
                </h2>
              </v-col>
              <v-col>
                <h2 :class="weight>0&&weight<100?'text-left':'orange--text'">
                  {{ Number(weight) }}
                </h2>
              </v-col>
            </v-row>
            <v-row>
              <v-col>
                <h2 :class="weight>0&&weight<100?'text-right':'orange--text text-right'">
                  Prix * :
                </h2>
              </v-col>
              <v-col>
                <h2 :class="weight>0&&weight<100?'text-left':'orange--text'">
                  {{ price() }}
                </h2>
              </v-col>
            </v-row>
            <v-row class="justify-space-around">
              <v-checkbox
                v-model="discount20"
                hide-details
                label="-20%"
              ></v-checkbox>
              <v-checkbox
                v-model="discount50"
                hide-details
                label="-50%"
              ></v-checkbox>
            </v-row>
          </v-col>
        </v-row>
      </v-card-text>
      <v-card-actions v-if="printInProgress && selected"  class="justify-center">
        <v-progress-circular
          indeterminate
          :size="100"
          :width="7"
          color="primary"
        />
      </v-card-actions>
      <v-card-actions v-if="!printInProgress && selected" class="justify-space-around">
        <v-btn width="200px" height="80px"
               @click="$emit('cancel')">
          Annuler
        </v-btn>
        <v-btn v-if="variableWeightProduct()"
               width="200px" height="80px"
               @click="weightChange=!weightChange"
               :input-value="weightChange">
          Modifier le poids
        </v-btn>
        <v-btn width="200px" height="80px"
               @click="printLabel(false)"
               :disabled="weight<=0 || weight>=100">
          Valider
        </v-btn>
        <v-btn width="200px" height="80px"
               @click="printLabel(true)"
               :disabled="weight<=0 || weight>=100">
          Valider<br/>et<br/>Couper le ticket
        </v-btn>
      </v-card-actions>
      <v-card-actions v-if="selected && weightChange">
        <Keyboard @pressed="pressed" onlyNum />
      </v-card-actions>
      <v-card-text v-if="selected" class="pr-0">
        <h4 v-if="variableWeightProduct()">
          * Le prix est donné à titre indicatif. Le calcul se fera en caisse au regard du poid.
        </h4>
        <h4 v-else>
          * Le prix est donné à titre indicatif. Le calcul se fera en caisse.
        </h4>
      </v-card-text>
    </v-card>
  </v-list-item-content>
</template>

<script>

import asEuro from '@/mixin/euro';
import print from '@/mixin/print';
import Keyboard from './Keyboard.vue';

export default {
  name: 'Product',
  props: {
    product: Object,
    selected: Boolean,
  },
  components: {
    Keyboard,
  },
  data: () => ({
    weight: 0.0,
    weightChange: false,
    printInProgress: false,
    printError: '',
    discount: 0,
    discount20: false,
    discount50: false,
  }),
  created() {
    if (!this.healthy || !this.connected || !this.variableWeightProduct()) {
      this.weightChange = true;
      this.weight = 0.0;
    } else {
      this.weight = this.weightFromScale;
    }
  },
  watch: {
    weightChange() {
      if (!this.weightChange) {
        this.weight = this.weightFromScale;
      }
    },
    weightFromScale() {
      if (!this.weightChange) {
        this.weight = this.weightFromScale;
      }
    },
    healthy() {
      if (!this.healthy || !this.connected) {
        this.weightChange = true;
        this.weight = 0.0;
      }
    },
    connected() {
      if (!this.healthy || !this.connected) {
        this.weightChange = true;
        this.weight = 0.0;
      }
    },
    discount20() {
      if (this.discount20) {
        if (this.discount50) {
          this.discount50 = false;
        }
        this.discount = 20;
      } else {
        this.discount = 0;
      }
    },
    discount50() {
      if (this.discount50) {
        if (this.discount20) {
          this.discount20 = false;
        }
        this.discount = 50;
      } else {
        this.discount = 0;
      }
    },
  },
  computed: {
    weightFromScale() {
      return this.$store.state.scale.weight;
    },
    healthy() {
      return this.$store.state.scale.healthy;
    },
    connected() {
      return this.$store.state.scale.connected;
    },
  },
  methods: {
    variableWeightProduct() {
      return !!this.product.id;
    },
    asEuro,
    price() {
      let price = this.product.lst_price * this.weight;
      if (this.discount20) {
        price *= 0.8;
      } else if (this.discount50) {
        price *= 0.5;
      }
      return asEuro(price);
    },
    pressed(value) {
      if (value) {
        this.weight = parseFloat(value);
      } else {
        this.weight = 0.0;
      }
    },
    printLabel(cut) {
      this.printInProgress = true;
      if (this.product.id) {
        this.$store.dispatch({
          type: 'antifreeze/add',
          weight: this.weight,
        });
      }
      print(
        this.product,
        this.$store.state.ticket.labels.length + 1,
        this.weight,
        this.discount,
        cut,
      ).then(() => {
        if (cut) {
          this.$store.dispatch('ticket/reset');
        } else {
          this.$store.dispatch({
            type: 'ticket/add',
            label: {
              product: this.product,
              weight: this.weight,
            },
          });
        }
        this.printInProgress = false;
        this.$emit('cancel');
      }).catch(() => {
        this.printInProgress = false;
        this.printError = true;
      });
    },
  },
};
</script>

<style scoped>
</style>
