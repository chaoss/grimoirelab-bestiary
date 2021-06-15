<template>
  <div>
    <v-treeview
      v-if="items"
      dense
      hoverable
      open-all
      expand-icon="mdi-chevron-down"
      active-class="dropzone"
      item-key="name"
      item-text="title"
      item-children="subprojects"
      :items="items"
      :active="active"
    >
      <template v-slot:label="{ item }">
        <div
          class="d-flex justify-space-between align-center hidden"
          :draggable="!item.projectSet"
          @dragstart.stop="startDrag(item, $event)"
          @drop.stop.prevent="onDrop(item, $event)"
          @dragenter.prevent
          @dragover.prevent="handleDrag(item, $event, true)"
          @dragleave.prevent="handleDrag(item, $event, false)"
          @dragend.prevent="onDragend"
        >
          <router-link
            v-slot="{ navigate, href, isExactActive }"
            :to="getLink(item)"
            custom
          >
            <a
              class="router-link"
              :class="{ 'router-link-exact-active': isExactActive }"
              :href="href"
              @click="navigate"
              @drop.prevent="onDrop(item, $event)"
            >
              {{ item.title }}
            </a>
          </router-link>

          <v-menu offset-y v-if="!item.projectSet">
            <template v-slot:activator="{ on }">
              <v-btn v-on="on" icon color="transparent">
                <v-icon>mdi-dots-horizontal</v-icon>
              </v-btn>
            </template>
            <v-list dense>
              <v-list-item
                :to="{
                  name: 'project-edit',
                  params: {
                    id: item.ecosystem.id,
                    name: item.name
                  }
                }"
              >
                <v-list-item-icon class="mr-2">
                  <v-icon small color="#3f3f3f">mdi-pencil-outline</v-icon>
                </v-list-item-icon>
                <v-list-item-title>Edit</v-list-item-title>
              </v-list-item>
              <v-list-item @click="confirmDeleteProject(item)">
                <v-list-item-icon class="mr-2">
                  <v-icon small color="#3f3f3f">mdi-trash-can-outline</v-icon>
                </v-list-item-icon>
                <v-list-item-title>Delete</v-list-item-title>
              </v-list-item>
            </v-list>
          </v-menu>

          <v-menu offset-y v-else>
            <template v-slot:activator="{ on }">
              <v-btn v-on="on" icon color="transparent">
                <v-icon>mdi-dots-horizontal</v-icon>
              </v-btn>
            </template>
            <v-list dense>
              <v-list-item
                :to="{ name: 'project-new', params: { id: item.id } }"
              >
                <v-list-item-icon class="mr-2">
                  <v-icon small color="#3f3f3f">mdi-plus</v-icon>
                </v-list-item-icon>
                <v-list-item-title>Add a project</v-list-item-title>
              </v-list-item>
              <v-list-item
                :to="{ name: 'ecosystem-edit', params: { id: item.id } }"
              >
                <v-list-item-icon class="mr-2">
                  <v-icon small color="#3f3f3f">mdi-pencil-outline</v-icon>
                </v-list-item-icon>
                <v-list-item-title>Edit</v-list-item-title>
              </v-list-item>
              <v-list-item @click="confirmDeleteEcosystem(item)">
                <v-list-item-icon class="mr-2">
                  <v-icon small color="#3f3f3f">mdi-trash-can-outline</v-icon>
                </v-list-item-icon>
                <v-list-item-title>Delete</v-list-item-title>
              </v-list-item>
            </v-list>
          </v-menu>
        </div>
      </template>
    </v-treeview>
    <div class="drag-image"></div>
  </div>
</template>

<script>
import { hasSameRoot, isDescendant, isParent } from "../utils/projects";
export default {
  name: "EcosystemTree",
  props: {
    ecosystem: {
      type: Object,
      required: true
    },
    deleteProject: {
      type: Function,
      required: true
    },
    moveProject: {
      type: Function,
      required: true
    },
    deleteEcosystem: {
      type: Function,
      required: true
    }
  },
  data() {
    return {
      items: null,
      dragged: null,
      active: []
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
    confirmDeleteProject(item) {
      const dialog = {
        isOpen: true,
        title: `Delete project ${item.title}?`,
        warning: "This will delete every project inside it.",
        action: () => this.deleteProject(item.id)
      };
      this.$store.commit("setDialog", dialog);
    },
    confirmDeleteEcosystem(item) {
      const dialog = {
        isOpen: true,
        title: `Delete ecosystem ${item.title}?`,
        warning: "This will delete every project inside it.",
        action: () => this.deleteEcosystem(item.id)
      };
      this.$store.commit("setDialog", dialog);
    },
    startDrag(item, event) {
      if (item.projectSet) {
        return;
      }
      const dragImage = document.querySelector(".drag-image");
      dragImage.innerHTML = event.target.closest(".v-treeview-node").innerHTML;
      event.dataTransfer.setDragImage(dragImage, 10, 10);
      event.dataTransfer.setData("move", item.id);
      this.dragged = item;
    },
    handleDrag(item, event, dragged) {
      if (dragged && this.allowDrag(item)) {
        this.active.push(item.name);
      } else {
        this.active = this.active.filter(project => project.name === item.name);
      }
    },
    allowDrag(item) {
      if (this.dragged && item.ecosystem) {
        return (
          item.ecosystem.id === this.dragged.ecosystem.id &&
          hasSameRoot(this.dragged, item) &&
          !isParent(this.dragged, item) &&
          !isDescendant(item, this.dragged) &&
          item.id !== this.dragged.id
        );
      }
      return false;
    },
    onDrop(item) {
      if (this.dragged && this.allowDrag(item)) {
        const project = this.dragged.id;
        const dialog = {
          isOpen: true,
          title: `Move project ${this.dragged.title} to ${item.title}?`,
          action: () => this.moveProject(project, item.id)
        };
        this.$store.commit("setDialog", dialog);
        this.active = this.active.filter(project => project.name === item.name);
        this.dragged = null;
      }
    },
    onDragend() {
      this.dragged = null;
      this.active = [];
    }
  },
  mounted() {
    this.items = this.filterDuplicateProjects(this.ecosystem);
  },
  watch: {
    ecosystem(value) {
      this.items = this.filterDuplicateProjects(value);
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
  &:focus,
  .v-btn:focus {
    .v-icon.v-icon {
      color: $text-color;
    }
    .router-link {
      overflow: hidden;
      text-overflow: ellipsis;
    }
  }
}
.v-btn--icon {
  min-width: 36px;
}
::v-deep .dropzone {
  &::before {
    border: thin solid;
    background: lighten($primary-color, 30%);
    opacity: 0.12;
    transition: none;
  }
}
.drag-image {
  position: absolute;
  top: -1000px;
  left: -1000px;
  background-color: #ffffff;
  border: 2px solid #003756;

  .v-treeview-node__level:first-child {
    display: none;
  }
}
</style>
