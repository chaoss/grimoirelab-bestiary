<template>
  <div class="pa-5">
    <h2 class="text-body-1 font-weight-light mb-9">
      Bestiary /
      <span class="font-weight-bold">New project</span>
    </h2>
    <project-form
      v-if="isEcosystem"
      :ecosystemId="ecosystemId"
      :get-projects="getProjects"
      :add-project="addProject"
      :parent="parent"
    />
    <v-alert v-else text outlined type="error" width="50%">
      No ecosystem with id <code>{{ this.$route.params.id }}</code>
    </v-alert>
  </div>
</template>

<script>
import ProjectForm from "../components/ProjectForm";
import { getProjects } from "../apollo/queries";
import { addProject } from "../apollo/mutations";

export default {
  name: "NewProject",
  components: { ProjectForm },
  computed: {
    ecosystemId() {
      return this.$route.params.id ? Number(this.$route.params.id) : null;
    },
    isEcosystem() {
      return this.$store.getters.findEcosystem(this.ecosystemId);
    },
    parent() {
      return this.$route.params.parent;
    }
  },
  methods: {
    async getProjects(ecosystem, pageSize = 50, page = 1) {
      const response = await getProjects(this.$apollo, pageSize, page, {
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
