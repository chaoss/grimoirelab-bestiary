<template>
  <v-app>
    <v-main>
      <v-navigation-drawer permanent class="pa-3" color="#F5F5F5">
        <div v-for="ecosystem in ecosystems" :key="ecosystem.id">
          <ecosystem-tree :ecosystem="ecosystem" />
        </div>
      </v-navigation-drawer>
    </v-main>
  </v-app>
</template>

<script>
import { getEcosystems } from "./apollo/queries";
import EcosystemTree from "./components/EcosystemTree";

export default {
  name: "App",
  components: {
    EcosystemTree
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
