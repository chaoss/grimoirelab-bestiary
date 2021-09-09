<template>
  <div class="pa-5" v-if="project">
    <breadcrumbs :items="breadcrumbs" />
    <v-row class="ma-0 mb-9 justify-space-between">
      <h2 class="text-h5 font-weight-medium">{{ project.title }}</h2>
      <div>
        <v-btn
          class="button--lowercase button--secondary mr-6"
          :to="{
            name: 'project-edit',
            params: {
              id: ecosystemId,
              name: name
            }
          }"
          outlined
        >
          <v-icon dense left>mdi-pencil-outline</v-icon>
          Edit
        </v-btn>
        <v-btn
          class="button--lowercase button--secondary"
          outlined
          @click="confirmDelete"
        >
          <v-icon dense left>mdi-trash-can-outline</v-icon>
          Delete
        </v-btn>
      </div>
    </v-row>

    <project-list
      :projects="project.subprojects"
      :ecosystem-id="ecosystemId"
      :parent-project="{ name: project.name, id: project.id }"
      class="mb-9"
    />

    <datasource-list
      :items="project.datasetSet"
      :project-id="project.id"
      :delete-dataset="deleteDataset"
      @updateDatasets="getProject"
    />
  </div>
</template>

<script>
import { getProjectByName } from "../apollo/queries";
import { deleteProject, deleteDataset } from "../apollo/mutations";
import { getProjectBreadcrumbs } from "../utils";
import Breadcrumbs from "../components/Breadcrumbs";
import ProjectList from "../components/ProjectList";
import DatasourceList from "../components/DatasourceList";

export default {
  name: "Project",
  components: { Breadcrumbs, ProjectList, DatasourceList },
  data() {
    return {
      project: null
    };
  },
  computed: {
    ecosystemId() {
      return this.$route.params.ecosystemId;
    },
    name() {
      return this.$route.params.name;
    },
    breadcrumbs() {
      return getProjectBreadcrumbs(this.project);
    }
  },
  methods: {
    async getProject() {
      try {
        const response = await getProjectByName(
          this.$apollo,
          this.name,
          this.ecosystemId
        );
        this.project = response.data.projects.entities[0];
      } catch (error) {
        console.error(error);
      }
    },
    confirmDelete() {
      const dialog = {
        isOpen: true,
        title: `Delete project ${this.project.title}?`,
        warning: "This will delete every project inside it.",
        action: () => this.deleteProject(this.project.id)
      };
      this.$store.commit("setDialog", dialog);
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
        this.$emit("updateSidebar");
        this.$router.push("/");
      } catch (error) {
        this.$store.commit("clearDialog");
        this.$store.commit("setSnackbar", {
          isOpen: true,
          text: error,
          color: "error"
        });
      }
    },
    async deleteDataset(id) {
      const response = await deleteDataset(this.$apollo, id);
      return response;
    }
  },
  mounted() {
    this.getProject();
  },
  watch: {
    "$store.state.ecosystems": function() {
      this.getProject();
    }
  }
};
</script>
<style lang="scss" scoped>
@import "../styles/_buttons";
</style>
