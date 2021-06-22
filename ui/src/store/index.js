import Vue from "vue";
import Vuex from "vuex";
import Cookies from "js-cookie";
import { tokenAuth } from "../apollo/mutations";
import router from "../router";

Vue.use(Vuex);

export default new Vuex.Store({
  state: {
    auth: {
      token: Cookies.get("bestiary_authtoken"),
      user: Cookies.get("bestiary_user")
    },
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
    setToken(state, token) {
      state.auth.token = token;
    },
    setUser(state, user) {
      state.auth.user = user;
    },
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
    isAuthenticated: state => !!state.auth.token,
    user: state => state.auth.user,
    ecosystems: state => state.ecosystems,
    findEcosystem: state => id => {
      return state.ecosystems.find(
        ecosystem => ecosystem.id.toString() === id.toString()
      );
    },
    dialog: state => state.dialog,
    snackbar: state => state.snackbar
  },
  actions: {
    async login({ commit }, authDetails) {
      const response = await tokenAuth(
        authDetails.apollo,
        authDetails.username,
        authDetails.password
      );
      if (response && !response.errors) {
        const token = response.data.tokenAuth.token;
        commit("setToken", token);
        Cookies.set("bestiary_authtoken", token, { sameSite: "strict" });
        commit("setUser", authDetails.username);
        Cookies.set("bestiary_user", authDetails.username, {
          sameSite: "strict"
        });
        return token;
      }
      return response;
    },
    logout({ commit }) {
      commit("setToken", null);
      commit("setUser", null);
      Cookies.remove("bestiary_authtoken");
      Cookies.remove("bestiary_user");
      router.push("/login");
    }
  },
  modules: {}
});
