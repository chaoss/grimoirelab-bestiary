<template>
  <div class="pa-5">
    <breadcrumbs :items="breadcrumbs" />
    <project-form
      v-if="isEcosystem"
      :ecosystemId="ecosystemId"
      :get-projects="getProjects"
      :save-function="addProject"
      :parent="parent"
    />
    <v-alert v-else text outlined type="error" width="50%">
      No ecosystem with id <code>{{ this.$route.params.id }}</code>
    </v-alert>
  </div>
</template>

<script>
import Breadcrumbs from "../components/Breadcrumbs";
import ProjectForm from "../components/ProjectForm";
import { GetBasicProjectInfo } from "../apollo/queries";
import { addProject } from "../apollo/mutations";
import { getViewBreadCrumbs } from "../utils";

export default {
  name: "NewProject",
  components: { Breadcrumbs, ProjectForm },
  computed: {
    ecosystemId() {
      return this.$route.params.id ? Number(this.$route.params.id) : null;
    },
    isEcosystem() {
      return this.$store.getters.findEcosystem(this.ecosystemId);
    },
    parent() {
      return this.$route.params.parent;
    },
    breadcrumbs() {
      return getViewBreadCrumbs("New project", this.isEcosystem, this.parent);
    }
  },
  methods: {
    async getProjects(ecosystem, pageSize = 50, page = 1) {
      const response = await GetBasicProjectInfo(this.$apollo, pageSize, page, {
        ecosystemId: ecosystem
      });
      if (response) {
        return response.data.projects.entities;
      }
    },
    async addProject(data) {
      const response = await addProject(this.$apollo, data);
      if (response) {
        this.$emit("updateSidebar");
        return response.data.addProject.project;
      }
    }
  }
};
</script>
