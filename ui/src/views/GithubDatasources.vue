<template>
  <section class="d-flex flex-column">
    <h3 class="text-h6 mt-6 mb-4">
      Add data sources
    </h3>

    <v-alert
      v-if="error.length !== 0"
      text
      dense
      color="error"
      icon="mdi-alert-outline"
      border="left"
    >
      {{ error }}
    </v-alert>

    <git-hub-table
      :items="items"
      :add-data-set="addDataSet"
      :get-projects="getProjects"
      :show-loader="isLoading"
      class="pa-5"
    />

    <v-alert
      v-if="!isLoading && items.length > 0"
      text
      dense
      dismissible
      color="info"
      icon="mdi-lightbulb"
      border="left"
      class="mt-auto"
    >
      You can also add datasets by dragging and dropping them onto a project on
      the sidebar menu
    </v-alert>
  </section>
</template>

<script>
import { getProjects, GET_JOB } from "../apollo/queries";
import { addDataSet } from "../apollo/mutations";
import GitHubTable from "../components/GitHubTable";

export default {
  name: "GithubDatasources",
  components: { GitHubTable },
  data() {
    return {
      items: [],
      error: "",
      isLoading: true
    };
  },
  computed: {
    jobID() {
      return this.$route.params.jobID;
    }
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
    }
  },
  mounted() {
    // Run the 'job' query every second
    this.$apollo.queries.job.startPolling(1000);
  },
  apollo: {
    job: {
      query: GET_JOB,
      variables() {
        return {
          jobId: this.jobID
        };
      },
      result(result) {
        // Stop running the query if its status is 'finished'
        if (result.data && result.data.job.status === "finished") {
          this.$apollo.queries.job.stopPolling();
          this.items = result.data.job.result;
          this.error = "";
          this.isLoading = false;

          if (result.data.job.errors) {
            this.error = result.data.job.errors;
          }
        }
      },
      error(error) {
        this.$apollo.queries.job.stopPolling();
        this.error = error;
        this.isLoading = false;
      }
    }
  }
};
</script>

<style lang="scss" scoped>
section {
  min-height: 95vh;
}
</style>
