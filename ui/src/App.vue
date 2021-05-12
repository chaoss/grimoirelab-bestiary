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
          <v-icon small left>mdi-plus-box-outline</v-icon>
          Add project
        </v-btn>
      </div>
    </v-navigation-drawer>
    <v-main>
      <v-container>
        <transition name="fade" mode="out-in">
          <router-view
            :key="$route.fullPath"
            @updateSidebar="getEcosystemsPage"
          />
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
        this.$store.commit("setEcosystems", this.ecosystems);
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
  transition-duration: 0.35s;
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

.link.v-btn:not(.v-btn--round).v-size--default {
  padding: 0 32px;
  .v-btn__content {
    text-transform: none;
    justify-content: left;
    letter-spacing: 0;
  }
}

.link.v-btn--active {
  background: rgba(0, 55, 86, 0.12);
  .v-btn__content {
    color: #003756;
  }
}
</style>
