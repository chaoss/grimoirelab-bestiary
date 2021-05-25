<template>
  <section>
    <div class="d-flex justify-space-between">
      <h3 class="text-h6 d-flex align-center">
        Projects
        <v-chip small pill class="ml-2">{{ list.length }}</v-chip>
      </h3>
      <v-btn
        class="primary--text button--lowercase"
        :to="{
          name: 'project-new',
          params: {
            id: ecosystemId,
            parent: parentProject
          }
        }"
      >
        <v-icon dense left>mdi-plus</v-icon>
        Add project
      </v-btn>
    </div>
    <v-list two-line>
      <project-entry
        v-for="project in list"
        :key="project.id"
        :title="project.title"
        :route="project.route"
        :path="project.path"
      />
    </v-list>
  </section>
</template>

<script>
import ProjectEntry from "./ProjectEntry";

export default {
  name: "ProjectList",
  components: { ProjectEntry },
  props: {
    projects: {
      type: Array,
      required: true
    },
    ecosystemId: {
      type: [Number, String],
      required: true
    },
    parentProject: {
      type: Object,
      required: false
    }
  },
  data() {
    return {
      list: []
    };
  },
  methods: {
    flattenProjects(projects, prefix) {
      let result = [];
      prefix = prefix ? `${prefix} / ` : " ";
      projects.forEach(project => {
        const path = `${prefix}${project.name}`;
        const route = `/ecosystem/${project.ecosystem.id}/project/${project.name}`;
        result.push(Object.assign(project, { path, route }));
        if (Array.isArray(project.subprojects)) {
          result = result.concat(
            this.flattenProjects(project.subprojects, path)
          );
        } else {
          result = result.concat(Object.assign(project, { path, route }));
        }
      });
      return result;
    },
    highlightName(route) {
      let names = route.split("/");
      if (names.length === 1) {
        return `<span>${route}</span>`;
      } else {
        const last = names.pop();
        return `${[...names].join(" / ")} / <span>${last}</span>`;
      }
    }
  },
  watch: {
    projects(value) {
      this.list = this.flattenProjects(value);
    }
  },
  mounted() {
    this.list = this.flattenProjects(this.projects);
  }
};
</script>

<style lang="scss" scoped>
::v-deep .v-list-item__title span {
  font-weight: 500;
}
.button--lowercase {
  text-transform: none;
  letter-spacing: normal;
}
.v-list-item:not(:last-child) {
  border-bottom: thin solid rgba(0, 0, 0, 0.12);
}
</style>
