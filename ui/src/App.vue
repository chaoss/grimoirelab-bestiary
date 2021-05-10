<template>
  <v-app>
    <v-navigation-drawer permanent app class="pa-3" color="#F5F5F5">
      <div v-for="ecosystem in ecosystems" :key="ecosystem.id">
        <ecosystem-tree :ecosystem="ecosystem" />
        <v-btn
          :to="{ name: 'project-new', params: { id: ecosystem.id } }"
          class="link"
          color="#7a7a7a"
          text
          block
        >
          <v-icon dense left>mdi-plus</v-icon>
          Add project
        </v-btn>
      </div>
    </v-navigation-drawer>
    <v-main>
      <v-container>
        <transition name="fade" mode="out-in">
          <router-view :key="$route.fullPath" />
        </transition>
      </v-container>
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

<style lang="scss">
.fade-enter-active,
.fade-leave-active {
  transition-duration: 0.3s;
  transition-property: opacity;
  transition-timing-function: ease;
}

.fade-enter,
.fade-leave-active {
  opacity: 0;
}

@media (min-width: 1904px) {
  .v-main__wrap .container {
    max-width: 1185px;
  }
}

.link .v-btn__content {
  text-transform: none;
  justify-content: left;
}
</style>
