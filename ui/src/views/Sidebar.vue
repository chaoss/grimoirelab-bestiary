<template>
  <v-app>
    <v-navigation-drawer permanent app class="pa-3" color="#F5F7F8">
      <search class="mt-4" filled @search="search" ref="search" />
      <h2 class="text-subtitle-1 text--secondary ma-2">Ecosystems</h2>
      <div v-for="ecosystem in ecosystems" :key="ecosystem.id">
        <ecosystem-tree
          :ecosystem="ecosystem"
          :delete-project="deleteProject"
          :move-project="moveProject"
          :delete-ecosystem="deleteEcosystem"
          :add-data-set="addDataSet"
        />
      </div>
      <v-btn
        :to="{ name: 'ecosystem-new' }"
        class="link pl-2"
        color="#3f3f3f"
        text
        block
      >
        <v-icon small class="mr-1">mdi-plus</v-icon>
        Add ecosystem
      </v-btn>
      <v-divider class="mt-3 mb-3" />
      <h2 class="text-subtitle-1 text--secondary ma-2">Data sources</h2>
      <v-btn
        :to="{ name: 'add-datasources' }"
        class="link pl-2"
        color="text"
        text
        block
      >
        <v-icon small class="mr-1">mdi-plus</v-icon>
        Add data sources
      </v-btn>
      <template v-slot:append>
        <v-divider />
        <div class="d-flex align-center mt-3">
          <v-icon small color="#3f3f3f" class="pl-2 pr-2">
            mdi-account-circle
          </v-icon>
          <span class="text-subtitle-2">{{ user }}</span>
          <v-spacer />
          <v-tooltip right>
            <template v-slot:activator="{ on }">
              <v-btn icon color="#3f3f3f" v-on="on" @click="logout">
                <v-icon small>mdi-logout-variant</v-icon>
              </v-btn>
            </template>
            <span>Log out</span>
          </v-tooltip>
        </div>
      </template>
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
    <simple-dialog
      :is-open="dialog.isOpen"
      :title="dialog.title"
      :text="dialog.text"
      :action="dialog.action"
      :warning="dialog.warning"
      :width="dialog.width"
    >
    </simple-dialog>
    <v-snackbar
      v-model="snackbar.isOpen"
      :color="snackbar.color"
      timeout="8000"
    >
      {{ snackbar.text }}
    </v-snackbar>
  </v-app>
</template>

<script>
import { getEcosystems } from "../apollo/queries";
import {
  deleteProject,
  moveProject,
  deleteEcosystem,
  addDataSet
} from "../apollo/mutations";
import { mapGetters, mapActions } from "vuex";
import EcosystemTree from "../components/EcosystemTree";
import Search from "../components/Search";
import SimpleDialog from "../components/SimpleDialog";

export default {
  name: "Sidebar",
  components: {
    EcosystemTree,
    Search,
    SimpleDialog
  },
  data: () => ({
    ecosystems: []
  }),
  computed: {
    ...mapGetters(["dialog", "snackbar", "user"])
  },
  methods: {
    ...mapActions(["logout"]),
    async getEcosystemsPage(pageSize = 10, page = 1) {
      const response = await getEcosystems(this.$apollo, pageSize, page);
      if (response && response.data) {
        this.ecosystems = response.data.ecosystems.entities;
        this.$store.commit("setEcosystems", this.ecosystems);
      }
    },
    async deleteProject(id) {
      try {
        await deleteProject(this.$apollo, id);
        this.$store.commit("clearDialog");
        this.$store.commit("setSnackbar", {
          isOpen: true,
          text: "Project deleted successfully",
          color: "success"
        });
        this.getEcosystemsPage();
      } catch (error) {
        this.$store.commit("clearDialog");
        this.$store.commit("setSnackbar", {
          isOpen: true,
          text: error,
          color: "error"
        });
      }
    },
    async deleteEcosystem(id) {
      try {
        await deleteEcosystem(this.$apollo, id);
        this.$store.commit("clearDialog");
        this.$store.commit("setSnackbar", {
          isOpen: true,
          text: "Ecosystem deleted successfully",
          color: "success"
        });
        this.getEcosystemsPage();
      } catch (error) {
        this.$store.commit("clearDialog");
        this.$store.commit("setSnackbar", {
          isOpen: true,
          text: error,
          color: "error"
        });
      }
    },
    search(query) {
      this.$router.push({ name: "search", query });
      this.$refs.search.clearInput();
    },
    async moveProject(fromId, toId) {
      try {
        await moveProject(this.$apollo, fromId, toId);
        this.$store.commit("clearDialog");
        this.$store.commit("setSnackbar", {
          isOpen: true,
          text: "Project moved successfully",
          color: "success"
        });
        this.getEcosystemsPage();
      } catch (error) {
        this.$store.commit("clearDialog");
        this.$store.commit("setSnackbar", {
          isOpen: true,
          text: error,
          color: "error"
        });
      }
    },
    async addDataSet(category, datasourceName, uri, projectId, filters = {}) {
      const response = await addDataSet(
        this.$apollo,
        category,
        datasourceName,
        uri,
        projectId,
        filters
      );
      return response;
    }
  },
  created() {
    this.getEcosystemsPage(10, 1);
  }
};
</script>

<style lang="scss">
@import "../styles/_transitions.scss";

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
    .mdi::before {
      font-size: 1.1rem;
    }
  }
}

.link.v-btn--active {
  &::before {
    opacity: 0;
  }
  .v-btn__content {
    color: #003756;
  }
}

.text-subtitle-1 {
  color: #7a7a7a;
}
</style>
