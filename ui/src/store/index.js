import Vue from "vue";
import Vuex from "vuex";

Vue.use(Vuex);

export default new Vuex.Store({
  state: {
    ecosystems: []
  },
  mutations: {
    setEcosystems(state, ecosystems) {
      state.ecosystems = ecosystems;
    }
  },
  getters: {
    ecosystems: state => state.ecosystems,
    findEcosystem: state => id => {
      return state.ecosystems.find(
        ecosystem => ecosystem.id.toString() === id.toString()
      );
    }
  },
  modules: {}
});
