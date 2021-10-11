import Vue from "vue";
import VueRouter from "vue-router";
import Vuex from "vuex";
import router from "./../../src/router";
import store from "./../../src/store";
import * as _Vuetify from "vuetify/lib";
import { configure, addDecorator } from "@storybook/vue";

const Vuetify = _Vuetify.default;

const isVueComponent = obj => obj.name === "VueComponent";

const VComponents = Object.keys(_Vuetify).reduce((acc, key) => {
  if (isVueComponent(_Vuetify[key])) {
    acc[key] = _Vuetify[key];
  }
  return acc;
}, {});

Vue.use(Vuetify, {
  components: {
    ...VComponents
  }
});

Vue.use(VueRouter);
Vue.use(Vuex);

const VuetifyConfig = new Vuetify({
  icons: {
    iconfont: "mdi"
  },
  theme: {
    themes: {
      light: {
        primary: "#003756",
        secondary: "#f4bc00",
        "info--background": "#e4f2fE",
        text: "#3f3f3f"
      }
    }
  }
});

addDecorator(() => ({
  router,
  store,
  vuetify: VuetifyConfig,
  template: "<v-app><story/></v-app>"
}));
