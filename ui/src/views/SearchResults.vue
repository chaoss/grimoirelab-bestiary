<template>
  <section class="pa-5">
    <h2 class="text-h5 font-weight-medium mb-9">
      Search
    </h2>
    <search :set-value="setValue" @search="search" filter-selector />
    <h3 class="text-body-1 font-weight-bold d-flex align-center mt-3 mb-1">
      Projects
      <v-chip small class="ml-3" color="#F5F7F8">{{ results.length }}</v-chip>
    </h3>
    <v-list two-line>
      <project-entry
        v-for="project in results"
        :key="project.id"
        :title="project.title"
        :route="project.route"
        :path="project.path"
      />
    </v-list>
    <v-pagination
      v-if="results.length > 0"
      v-model="page"
      class="my-4 pagination"
      :length="totalPages"
      @input="queryProjects($event)"
    ></v-pagination>
  </section>
</template>

<script>
import ProjectEntry from "../components/ProjectEntry";
import Search from "../components/Search";
import { getProjects } from "../apollo/queries";

export default {
  name: "SearchResults",
  components: { ProjectEntry, Search },
  data() {
    return {
      filters: {},
      results: [],
      page: 1,
      totalPages: 1
    };
  },
  computed: {
    setValue() {
      return Object.entries(this.query)
        .map(([key, value]) => {
          value = value.replace(/"/g, "");
          if (key === "term") {
            return value;
          } else {
            return `${key}:"${value}"`;
          }
        })
        .toString()
        .replace(",", " ");
    },
    query() {
      return this.$route.query;
    }
  },
  methods: {
    search(filters) {
      this.filters = filters;
      this.queryProjects(1, filters);
      this.$router.replace({ name: "search", query: filters }).catch(() => {});
    },
    async queryProjects(page = this.page, filters = this.filters) {
      const response = await getProjects(this.$apollo, 20, page, filters);
      if (response) {
        this.results = response.data.projects.entities;
        this.results.forEach(res => {
          const path = this.getPath(res);
          const route = `/ecosystem/${res.ecosystem.id}/project/${res.name}`;
          Object.assign(res, { path, route });
        });
        this.page = response.data.projects.pageInfo.page;
        this.totalPages = response.data.projects.pageInfo.numPages;
      }
    },
    getPath(project) {
      const path = [project.name];

      function findParents(parent) {
        if (parent) {
          path.push(parent.name);
          findParents(parent.parentProject);
        } else {
          path.push(project.ecosystem.name);
        }
      }

      findParents(project.parentProject);

      return path
        .reverse()
        .toString()
        .replace(/,/g, " / ");
    }
  }
};
</script>

<style lang="scss" scoped>
@import "../styles/_buttons";
.v-list-item:not(:last-child) {
  border-bottom: thin solid rgba(0, 0, 0, 0.12);
}
</style>
