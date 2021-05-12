<template>
  <v-treeview
    v-if="items"
    dense
    hoverable
    open-all
    expand-icon="mdi-chevron-down"
    item-key="name"
    item-text="title"
    item-children="subprojects"
    :items="items"
  >
    <template v-slot:label="{ item }">
      <div class="d-flex justify-space-between align-center hidden">
        <router-link :to="getLink(item)">
          {{ item.title }}
        </router-link>
        <v-tooltip right>
          <template v-slot:activator="{ on }">
            <v-btn
              v-if="item.projectSet"
              :to="{ name: 'project-new', params: { id: item.id } }"
              v-on="on"
              color="transparent"
              icon
            >
              <v-icon>mdi-plus-box-outline</v-icon>
            </v-btn>
          </template>
          <span class="text-caption">Add a project</span>
        </v-tooltip>
      </div>
    </template>
  </v-treeview>
</template>

<script>
export default {
  name: "EcosystemTree",
  props: {
    ecosystem: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      items: null
    };
  },
  methods: {
    filterDuplicateProjects(ecosystem) {
      if (this.ecosystem.projectSet) {
        const subprojects = this.ecosystem.projectSet.filter(
          project => !project.parentProject
        );
        return [Object.assign(ecosystem, { subprojects })];
      } else {
        return [ecosystem];
      }
    },
    getLink(item) {
      if (item.projectSet) {
        return `/ecosystem/${item.id}`;
      } else {
        return `/ecosystem/${item.ecosystem.id}/project/${item.name}`;
      }
    },
    addActiveClass() {
      const activeNode = document.querySelector(".v-treeview-node--active");
      if (activeNode) {
        activeNode.classList.remove("v-treeview-node--active", "primary--text");
      }
      const activeRouterLink = document.querySelector(
        ".router-link-exact-active"
      );
      if (activeRouterLink) {
        const parent = activeRouterLink.closest(".v-treeview-node__root");
        parent.classList.add("v-treeview-node--active", "primary--text");
      }
    }
  },
  mounted() {
    this.items = this.filterDuplicateProjects(this.ecosystem);
    this.$nextTick(this.addActiveClass);
  },
  watch: {
    ecosystem(value) {
      this.items = this.filterDuplicateProjects(value);
    },
    $route() {
      this.$nextTick(this.addActiveClass);
    }
  }
};
</script>

<style lang="scss" scoped>
@import "../styles/_variables";
.v-treeview-node__root a {
  font-family: "Roboto", sans-serif;
  font-size: 0.875rem;
  color: $text-color;
  letter-spacing: 0.2px;
}
::v-deep .v-treeview-node__children {
  .theme--light.v-icon,
  a {
    color: $text-color--light;
  }
}
.v-treeview-node__label a {
  text-decoration: none;
  font-weight: 500;
}
.v-treeview-node__root .router-link-exact-active {
  color: $primary-color;
  font-weight: 700;
}
::v-deep .mdi::before,
.mdi-set {
  font-size: 18px;
}
::v-deep .v-treeview-node__toggle,
::v-deep .v-treeview-node__level {
  width: 18px;
}
::v-deep .v-treeview-node--active {
  .theme--light.v-icon,
  .hidden:hover .v-icon.v-icon {
    color: $primary-color;
  }
}
.hidden {
  .v-icon.v-icon {
    color: transparent;
  }
  &:hover,
  &:focus {
    .v-icon.v-icon {
      color: $text-color;
    }
  }
}
</style>
