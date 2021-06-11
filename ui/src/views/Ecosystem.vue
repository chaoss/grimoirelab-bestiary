<template>
  <section class="pa-5" v-if="ecosystem">
    <breadcrumbs :items="[{ text: ecosystem.name, disabled: true }]" />
    <v-row class="ma-0 mb-9 justify-space-between">
      <h2 class="text-h5 font-weight-medium">{{ ecosystem.title }}</h2>
      <v-btn
        class="primary--text button--lowercase"
        :to="{ name: 'ecosystem-edit', params: { id: id } }"
      >
        <v-icon dense left>mdi-pencil-outline</v-icon>
        Edit
      </v-btn>
    </v-row>
    <p class="ma-0 mb-9 text-body-1 text--secondary">
      {{ ecosystem.description }}
    </p>
    <project-list :projects="projects" :ecosystem-id="id" />
  </section>
  <v-alert v-else-if="error" text outlined type="error" class="mt-5">
    {{ error }}
  </v-alert>
</template>

<script>
import { getEcosystemByID } from "../apollo/queries";
import Breadcrumbs from "../components/Breadcrumbs";
import ProjectList from "../components/ProjectList";

export default {
  name: "Ecosystem",
  components: {
    Breadcrumbs,
    ProjectList
  },
  data() {
    return {
      ecosystem: null,
      error: null
    };
  },
  computed: {
    id() {
      return this.$route.params.id;
    },
    projects() {
      let projects = [];
      if (this.ecosystem) {
        projects = this.ecosystem.projectSet.filter(
          project => !project.parentProject
        );
      }
      return projects;
    }
  },
  methods: {
    async getEcosystemData(id = this.id) {
      try {
        const response = await getEcosystemByID(this.$apollo, id);
        if (response && !response.errors) {
          this.ecosystem = response.data.ecosystems.entities[0];
        }
      } catch (error) {
        this.error = error;
      }
    }
  },
  mounted() {
    this.getEcosystemData();
  }
};
</script>

<style lang="scss" scoped>
@import "../styles/_buttons";
</style>
