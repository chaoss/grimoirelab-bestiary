<template>
  <div class="pa-5">
    <breadcrumbs :items="breadcrumbs" />
    <dataset-table :datasets="datasets" />
  </div>
</template>

<script>
import { getDatasetsByUri } from "../apollo/queries";
import { getViewBreadCrumbs } from "../utils";
import Breadcrumbs from "../components/Breadcrumbs";
import DatasetTable from "../components/DatasetTable";

export default {
  name: "Datasource",
  components: {
    Breadcrumbs,
    DatasetTable
  },
  data() {
    return {
      datasets: []
    };
  },
  computed: {
    projectId() {
      return this.$route.params.id;
    },
    uri() {
      return this.$route.params.uri;
    },
    breadcrumbs() {
      if (this.datasets.length > 0) {
        return getViewBreadCrumbs(
          this.uri,
          this.datasets[0].project.ecosystem,
          this.datasets[0].project
        );
      } else {
        return [];
      }
    }
  },
  methods: {
    async getDatasets() {
      try {
        const response = await getDatasetsByUri(
          this.$apollo,
          this.projectId,
          this.uri
        );
        this.datasets = response.data.datasets.entities;
      } catch (error) {
        console.error(error);
      }
    }
  },
  mounted() {
    this.getDatasets();
  }
};
</script>
