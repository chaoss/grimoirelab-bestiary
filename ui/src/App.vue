<template>
  <v-app>
    <v-app-bar app color="primary" dark>
      <div class="d-flex align-center">
        <v-img
          alt="Vuetify Logo"
          class="shrink mr-2"
          contain
          src="https://cdn.vuetifyjs.com/images/logos/vuetify-logo-dark.png"
          transition="scale-transition"
          width="40"
        />

        <v-img
          alt="Vuetify Name"
          class="shrink mt-1 hidden-sm-and-down"
          contain
          min-width="100"
          src="https://cdn.vuetifyjs.com/images/logos/vuetify-name-dark.png"
          width="100"
        />
      </div>

      <v-spacer></v-spacer>

      <v-btn
        href="https://github.com/vuetifyjs/vuetify/releases/latest"
        target="_blank"
        text
      >
        <span class="mr-2">Latest Release</span>
        <v-icon>mdi-open-in-new</v-icon>
      </v-btn>
    </v-app-bar>

    <v-main>
      <v-container>
        <v-row>
          <v-col v-for="ecosystem in ecosystems" :key="ecosystem.id" cols="6">
            <example-card
              :name="ecosystem.name"
              :title="ecosystem.title"
              :description="ecosystem.description"
            >
            </example-card>
          </v-col>
        </v-row>
      </v-container>
    </v-main>
  </v-app>
</template>

<script>
import { getEcosystems } from "./apollo/queries";
import ExampleCard from "./components/ExampleCard";

export default {
  name: "App",
  components: {
    ExampleCard
  },
  data: () => ({
    ecosystems: []
  }),
  methods: {
    async getEcosystemsPage(pageSize = 10, page = 1) {
      const response = await getEcosystems(this.$apollo, pageSize, page);
      if (response && response.data) {
        this.ecosystems = response.data.ecosystems.entities;
      }
    }
  },
  created() {
    this.getEcosystemsPage(10, 1);
  }
};
</script>
