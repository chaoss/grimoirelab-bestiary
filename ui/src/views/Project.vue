<template>
  <div class="pa-5" v-if="project">
    <nav class="text-body-1 font-weight-light mb-9">
      Bestiary / {{ project.ecosystem.name }} /
      <span v-if="project.parentProject">
        {{ project.parentProject.name }} /
      </span>
      <span class="font-weight-bold">{{ project.name }}</span>
    </nav>

    <h2 class="text-h5 font-weight-medium mb-9">{{ project.title }}</h2>

    <project-list
      :projects="project.subprojects"
      :ecosystem-id="ecosystemId"
      :parent-project="{ name: project.name, id: project.id }"
    />
  </div>
</template>

<script>
import { getProjectByName } from "../apollo/queries";
import ProjectList from "../components/ProjectList";

export default {
  name: "Project",
  components: { ProjectList },
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
    }
  },
  async mounted() {
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
  }
};
</script>
