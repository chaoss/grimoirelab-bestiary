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

    <repository-table
      :items="items"
      :add-data-sets="addDataSets"
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
import { addDataSets } from "../apollo/mutations";
import RepositoryTable from "../components/RepositoryTable";

export default {
  name: "DatasourcesJob",
  components: { RepositoryTable },
  data() {
    return {
      items: [],
      error: "",
      isLoading: true
    };
  },
  computed: {
    datasourceName() {
      return this.$route.params.datasource;
    },
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
    async addDataSets(datasets, project_id) {
      let batch = [];
      let added = [];
      for (let dataset of datasets) {
        batch.push({
          uri: dataset.url,
          category: dataset.category,
          filters: "{}"
        });
        if (batch.length >= 100) {
          let response = await addDataSets(this.$apollo, project_id, this.datasourceName, batch);
          added.push.apply(added, response.data.addDatasets.datasets)
          batch = [];
        }
      }
      if (batch.length > 0) {
        let response = await addDataSets(this.$apollo, project_id, this.datasourceName, batch);
        added.push.apply(added, response.data.addDatasets.datasets)
      }
      return added;
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
        // Stop running the query if its status is 'finished' or 'failed'
        if (
          (result.data && result.data.job.status === "finished") ||
          result.data.job.status === "failed"
        ) {
          this.$apollo.queries.job.stopPolling();
          this.isLoading = false;

          if (result.data.job.errors.length > 0) {
            this.error = result.data.job.errors;
            return;
          }

          this.items = result.data.job.result;
          this.error = "";
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
