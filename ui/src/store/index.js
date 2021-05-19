import Vue from "vue";
import Vuex from "vuex";

Vue.use(Vuex);

export default new Vuex.Store({
  state: {
    ecosystems: [],
    dialog: {
      isOpen: false,
      title: null,
      text: null,
      action: null,
      warning: null
    },
    snackbar: {
      isOpen: false,
      color: "success",
      text: null
    }
  },
  mutations: {
    setEcosystems(state, ecosystems) {
      state.ecosystems = ecosystems;
    },
    setDialog(state, dialog) {
      Object.assign(state.dialog, dialog);
    },
    clearDialog(state) {
      state.dialog = {
        isOpen: false,
        title: null
      };
    },
    setSnackbar(state, snackbar) {
      Object.assign(state.snackbar, snackbar);
    },
    clearSnackbar(state) {
      state.snackbar = {
        isOpen: false,
        color: "success",
        text: null
      };
    }
  },
  getters: {
    ecosystems: state => state.ecosystems,
    findEcosystem: state => id => {
      return state.ecosystems.find(
        ecosystem => ecosystem.id.toString() === id.toString()
      );
    },
    dialog: state => state.dialog,
    snackbar: state => state.snackbar
  },
  modules: {}
});
