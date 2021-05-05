import Vue from "vue";
import VueRouter from "vue-router";
import router from "./../../src/router";
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

addDecorator(() => ({
  router,
  vuetify: VuetifyConfig,
  template: "<v-app><story/></v-app>"
}));
