<template>
  <section class="d-flex flex-column">
    <h3 class="text-h6 mt-6 mb-6">
      Add data sources
    </h3>

    <v-tabs color="text">
      <v-tab class="button--lowercase button--secondary">
        <v-icon dense left>mdi-github</v-icon>
        GitHub
      </v-tab>
      <v-tab-item transition="fade">
        <div v-if="isLoading" class="d-flex justify-center">
          <v-progress-circular
            :size="50"
            color="primary"
            indeterminate
          ></v-progress-circular>
        </div>
        <github-form
          v-else
          :get-projects="getProjects"
          :add-data-set="addDataSet"
          :get-repos="getGithubOwnerRepos"
          :get-token="getToken"
          :add-token="addToken"
        />
      </v-tab-item>
    </v-tabs>
  </section>
</template>

<script>
import { getProjects, getDatasourceCredentials } from "../apollo/queries";
import {
  addDataSet,
  addCredential,
  fetchGithubOwnerRepos
} from "../apollo/mutations";
import GithubForm from "../components/GithubForm";

export default {
  name: "AddDatasources",
  components: { GithubForm },
  data() {
    return {
      isLoading: false
    };
  },
  methods: {
    async getProjects(filters, pageSize = 50, page = 1) {
      const response = await getProjects(this.$apollo, pageSize, page, filters);
      if (response) {
        return response.data.projects.entities;
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
      if (response) {
        return response;
      }
    },
    async getGithubOwnerRepos(owner) {
      this.isLoading = true;
      const response = await fetchGithubOwnerRepos(this.$apollo, owner);
      if (response.data.fetchGithubOwnerRepos.jobId) {
        this.$router.push({
          name: "github-datasources",
          params: { jobID: response.data.fetchGithubOwnerRepos.jobId }
        });
      }
    },
    async getToken(datasource) {
      const response = await getDatasourceCredentials(this.$apollo, datasource);
      return response;
    },
    async addToken(datasource, token, name) {
      const response = await addCredential(
        this.$apollo,
        datasource,
        token,
        name
      );
      return response;
    }
  }
};
</script>

<style lang="scss" scoped>
@import "../styles/_buttons";
@import "../styles/_transitions";
@import "../styles/_variables";

::v-deep .v-tabs-items {
  border-top: thin solid $border-color;
}

::v-deep .v-tabs-slider {
  background-color: $primary-color;
}

.v-progress-circular {
  margin-top: 130px;
}
</style>
