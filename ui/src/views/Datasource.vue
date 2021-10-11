<template>
  <div class="pa-5">
    <breadcrumbs :items="breadcrumbs" />
    <dataset-table
      :datasets="datasets"
      :delete-dataset="deleteDataset"
      :archive-dataset="archiveDataset"
      :unarchive-dataset="unarchiveDataset"
      @updateDatasets="getDatasets"
    />
  </div>
</template>

<script>
import { getDatasetsByUri } from "../apollo/queries";
import {
  archiveDataset,
  deleteDataset,
  unarchiveDataset
} from "../apollo/mutations";
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
      datasets: [],
      ecosystemId: null,
      projectName: null
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
        if (this.datasets.length > 0) {
          this.ecosystemId = this.datasets[0].project.ecosystem.id;
          this.projectName = this.datasets[0].project.name;
        } else if (this.ecosystemId) {
          this.$router.push({
            name: "project",
            params: {
              ecosystemId: this.ecosystemId,
              name: this.projectName
            }
          });
        }
      } catch (error) {
        console.error(error);
      }
    },
    async deleteDataset(id) {
      const response = await deleteDataset(this.$apollo, id);
      return response;
    },
    async archiveDataset(id) {
      const response = await archiveDataset(this.$apollo, id);
      return response;
    },
    async unarchiveDataset(id) {
      const response = await unarchiveDataset(this.$apollo, id);
      return response;
    }
  },
  mounted() {
    this.getDatasets();
  }
};
</script>
