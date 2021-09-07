<template>
  <v-menu
    v-model="showMenu"
    max-height="40vh"
    offset-y
    :close-on-content-click="false"
  >
    <template v-slot:activator="{ on }">
      <v-btn
        v-on="on"
        :disabled="disabled"
        color="info"
        depressed
        class="button--lowercase"
        @click="loadProjects({ term: '' })"
      >
        {{ text }}
        <v-icon right small>mdi-chevron-down</v-icon>
      </v-btn>
    </template>

    <v-card class="pa-2 pt-0">
      <search @search="loadProjects" class="search pt-2" filled />
      <v-list dense class="pt-0">
        <v-list-item
          v-for="project in projects"
          :key="project.id"
          class="v-list-item--link"
          @click="select(project)"
        >
          <v-list-item-content>
            <v-list-item-subtitle v-html="project.path" />
          </v-list-item-content>
        </v-list-item>
      </v-list>
    </v-card>
  </v-menu>
</template>

<script>
import Search from "../components/Search";

export default {
  name: "ProjectSelector",
  components: { Search },
  props: {
    disabled: {
      type: Boolean,
      required: false,
      default: false
    },
    getProjects: {
      type: Function,
      required: true
    },
    text: {
      type: String,
      required: false,
      default: "Add to project"
    }
  },
  data() {
    return {
      projects: [],
      showMenu: false
    };
  },
  methods: {
    async loadProjects(term) {
      const response = await this.getProjects(term);
      if (response) {
        this.projects = response;
        this.projects.forEach(res => {
          Object.assign(res, { path: this.getPath(res) });
        });
      }
    },
    getPath(project) {
      const path = [project.name];
      function findParents(parent) {
        if (parent) {
          path.push(parent.name);
          findParents(parent.parentProject);
        }
      }
      findParents(project.parentProject);

      return path
        .reverse()
        .toString()
        .replace(/,/g, " / ");
    },
    select(project) {
      this.showMenu = false;
      this.$emit("selectedProject", project);
    }
  }
};
</script>

<style lang="scss" scoped>
@import "../styles/_buttons";
@import "../styles/_lists";

.search {
  position: sticky;
  top: 0;
  background-color: #ffffff;
  z-index: 2;
}
.v-list-item__title,
.v-list-item__subtitle {
  text-overflow: unset;
  white-space: break-spaces;
}
::v-deep .v-text-field__details {
  display: none;
}
</style>
