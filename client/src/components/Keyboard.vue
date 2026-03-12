<template>
  <v-container class="d-flex flex-column bg-grey-lighten-5 align-center">
    <v-row style="width: 100%; height: 80px;" class="pa-0 ma-0">
      <v-col cols="2" class="pa-0 ma-0">
        <v-btn v-if="!onlyNum"
               width="100px"
               height="60px"
               class="pa-0 ma-0"
               @click="$emit('close')">
          <v-icon>mdi-magnify-close</v-icon>
        </v-btn>
      </v-col>
      <v-col cols="8">
        <h2 :class="isValid()?'pb-5':'text-red pb-5'" style="text-align: center">
          {{ getValue() }}
        </h2>
      </v-col>
      <v-col cols="2" class="pa-0 ma-0 d-flex flex-column">
        <v-btn v-if="!onlyNum"
               width="100px"
               height="60px"
               class="pa-0 ma-0"
               style="align-self: end"
               @click="$emit('close')">
          <v-icon>mdi-magnify-close</v-icon>
        </v-btn>
      </v-col>
    </v-row>
    <v-row
      v-for="r in getKeys()"
      :key="`row_${r}`"
      no-gutters>
      <v-col
        v-for="c in r"
        :key="`row_${r}-col_${c}`"
      >
        <v-btn width="100px" height="80px" @click="press(c)">
          <v-icon v-if="c==='SUPPR'">mdi-backspace</v-icon>
          <v-icon v-else-if="c==='SPACE'">mdi-keyboard-space</v-icon>
          <h2 v-else>{{ c }}</h2>
        </v-btn>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>

export default {
  props: {
    onlyNum: Boolean,
  },
  data() {
    return {
      value: '',
    };
  },
  methods: {
    press(key) {
      if (key === 'SUPPR') {
        if (this.value) {
          this.value = this.value.slice(0, -1);
        }
      } else if (key === 'SPACE') {
        if (this.value && this.value.slice(-1) !== ' ') {
          this.value = `${this.value} `;
        }
      } else {
        if (this.onlyNum && !this.value && key === '.') {
          this.value = '0';
        }
        this.value = `${this.value}${key}`;
      }
    },
    isValid() {
      if (!this.value) {
        return true;
      }
      if (this.onlyNum) {
        // eslint-disable-next-line no-restricted-globals
        if (isNaN(Number(this.value))) {
          return false;
        }
        return parseFloat(this.value) > 0;
      }
      return true;
    },
    getKeys() {
      if (this.onlyNum) {
        return [
          ['7', '8', '9'],
          ['4', '5', '6'],
          ['1', '2', '3'],
          ['SUPPR', '0', '.'],
        ];
      }
      return [
        ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
        ['A', 'Z', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
        ['Q', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', 'M'],
        ['SPACE', 'W', 'X', 'C', 'V', 'B', 'N', 'SUPPR'],
      ];
    },
    getValue() {
      if (!this.value) {
        return this.defaultValue();
      }
      return this.value;
    },
    defaultValue() {
      return this.onlyNum ? '0' : '';
    },
    resetValue() {
      this.value = this.defaultValue();
    },
  },
  watch: {
    value() {
      this.$emit('pressed', this.isValid() ? this.value : 0);
    },
  },
};
</script>

<style scoped>
</style>
