import Vue from "vue";
import Vuetify from "vuetify/lib/framework";

Vue.use(Vuetify);

const opts = {
  icons: {
    iconfont: "mdi"
  },
  theme: {
    themes: {
      light: {
        primary: "#003756",
        secondary: "#f4bc00",
        "info--background": "#e4f2fE"
      }
    }
  }
};

export default new Vuetify(opts);
