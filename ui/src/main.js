import Vue from "vue";
import App from "./App.vue";
import router from "./router";
import store from "./store";
import vuetify from "./plugins/vuetify";
import VueApollo from "vue-apollo";
import VueRouter from "vue-router";
import { ApolloClient } from "apollo-client";
import { createHttpLink } from "apollo-link-http";
import {
  InMemoryCache,
  IntrospectionFragmentMatcher
} from "apollo-cache-inmemory";
import Cookies from "js-cookie";
import { ApolloLink } from "apollo-link";

const API_URL = "/api/";

// Force HTTP GET to the Django Server for getting the csrf token
let xmlHttp = new XMLHttpRequest();
xmlHttp.open("GET", API_URL, false); // false for synchronous request
xmlHttp.withCredentials = true;
xmlHttp.send(null);
const csrftoken = Cookies.get("csrftoken");

// HTTP connection to the API
const httpLink = createHttpLink({
  uri: API_URL,
  credentials: "include"
});

// Match types for fragments and unions (... on Type)
const fragmentMatcher = new IntrospectionFragmentMatcher({
  introspectionQueryResultData: {
    __schema: {
      types: []
    }
  }
});

// Cache implementation
const cache = new InMemoryCache({ fragmentMatcher });

const AuthLink = (operation, next) => {
  const token = csrftoken;
  const authtoken = Cookies.get("bestiary_authtoken");
  operation.setContext(context => ({
    ...context,
    headers: {
      ...context.headers,
      "X-CSRFToken": token,
      Authorization: authtoken ? `JWT ${authtoken}` : ""
    }
  }));
  return next(operation);
};

const link = ApolloLink.from([AuthLink, httpLink]);

// Create the apollo client
const apolloClient = new ApolloClient({
  link: link,
  cache
});

Vue.use(VueApollo);
Vue.use(VueRouter);

const apolloProvider = new VueApollo({
  defaultClient: apolloClient
});

Vue.config.productionTip = false;

new Vue({
  router,
  store,
  vuetify,
  apolloProvider,
  render: h => h(App)
}).$mount("#app");
