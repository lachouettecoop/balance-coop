const initialState = {
  weights: [],
};

const getters = {
  freezed: (state) => state.weights.length >= 3,
};

const antifreeze = {
  namespaced: true,
  state: initialState,
  getters,
  actions: {
    add({ commit }, { weight }) {
      commit('addWeight', weight);
    },
  },
  mutations: {
    addWeight(state, weight) {
      while (state.weights.length > 2) {
        state.weights.pop();
      }
      if (state.weights.length === 2 && state.weights[1] !== weight) {
        state.weights.pop();
      }
      if (state.weights.length === 1 && state.weights[0] !== weight) {
        state.weights.pop();
      }
      state.weights.unshift(weight);
    },
    reset(state) {
      state.labels = [];
    },
  },
};

export default antifreeze;
