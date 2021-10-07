<template>
  <div>
    <v-alert
      v-if="error"
      text
      dense
      dismissible
      color="error"
      icon="mdi-alert-circle-outline"
      border="left"
      class="mb-8"
    >
      {{ error }}
    </v-alert>

    <v-row
      v-if="isLoading || repositories.length > 0"
      class="mb-3 justify-space-between align-center flex-grow-0"
    >
      <v-switch
        v-model="showForks"
        label="Show forks"
        color="info"
        flat
        dense
        @change="filterForks($event)"
      />

      <project-selector
        :get-projects="getProjects"
        :disabled="selected.length === 0"
        @selectedProject="addDatasets"
      />
    </v-row>

    <v-data-table
      v-model="selected"
      :headers="headers"
      :items="repositories"
      :loading="isLoading"
      :hide-default-header="!isLoading && repositories.length === 0"
      :hide-default-footer="!isLoading && repositories.length === 0"
      item-key="url"
      disable-sort
      show-select
    >
      <template v-slot:item="{ item, isSelected, select }">
        <tr
          draggable
          class="table-row"
          :class="{ 'v-data-table__selected': isSelected }"
          @dragstart="startDrag(item, isSelected, $event)"
        >
          <td>
            <v-simple-checkbox
              :value="isSelected"
              :ripple="false"
              @click="select(!isSelected)"
            />
          </td>
          <td>
            <span>{{ item.url }}</span>
            <v-chip
              small
              v-if="item.fork"
              class="ml-2"
              color="info--background"
              text-color="info"
            >
              <v-icon small left>mdi-source-fork</v-icon>
              fork
            </v-chip>
          </td>
          <td>
            <v-simple-checkbox
              v-model="item.form.commit"
              :ripple="false"
              color="info"
            ></v-simple-checkbox>
          </td>
          <td>
            <v-simple-checkbox
              v-model="item.form.issue"
              :disabled="item.disableIssues"
              :ripple="false"
              color="info"
            ></v-simple-checkbox>
          </td>
          <td>
            <v-simple-checkbox
              v-model="item.form.pr"
              :ripple="false"
              color="info"
            ></v-simple-checkbox>
          </td>
        </tr>
      </template>
      <template v-slot:progress>
        <div class="d-flex justify-center mt-4 mb-2">
          <v-progress-circular
            :size="50"
            color="primary"
            indeterminate
          ></v-progress-circular>
        </div>
      </template>
      <template v-slot:no-data>
        <div class="d-flex flex-column justify-center align-center mt-4">
          <v-icon large>mdi-magnify-remove-outline</v-icon>
          <p class="mt-4 text-body-1">No repositories found</p>
        </div>
      </template>
    </v-data-table>

    <v-card class="dragged-item" color="primary" dark>
      <v-card-subtitle>
        Add {{ selected.length }} datasets to a project
      </v-card-subtitle>
    </v-card>
  </div>
</template>

<script>
import ProjectSelector from "../components/ProjectSelector";

export default {
  name: "RepositoryTable",
  components: { ProjectSelector },
  props: {
    items: {
      type: Array,
      required: true
    },
    getProjects: {
      type: Function,
      required: true
    },
    addDataSet: {
      type: Function,
      required: true
    },
    showLoader: {
      type: Boolean,
      required: false,
      default: false
    }
  },
  data() {
    return {
      headers: [
        { text: "URL", value: "url" },
        { text: "Commits", value: "commits" },
        { text: "Issues", value: "issues" },
        { text: "Pull Requests", value: "prs" }
      ],
      repositories: [],
      selected: [],
      projects: [],
      showForks: true,
      showMenu: false,
      isLoading: this.showLoader,
      error: null
    };
  },
  methods: {
    addFormValues(array) {
      return array.map(item => {
        return {
          url: item.url,
          fork: item.fork,
          disableIssues: !item.hasIssues,
          form: {
            commit: true,
            pr: true,
            issue: item.hasIssues
          }
        };
      });
    },
    filterForks(value) {
      if (value) {
        this.repositories = this.addFormValues(this.items);
      } else {
        this.repositories = this.addFormValues(this.items).filter(
          item => !item.fork
        );
        this.selected = this.selected.filter(item => !item.fork);
      }
    },
    startDrag(item, isSelected, event) {
      if (!isSelected) {
        this.selected.push(item);
      }
      event.dataTransfer.setData("type", "AddDatasources");
      event.dataTransfer.setData(
        "text/plain",
        JSON.stringify(this.selectedByCategory)
      );
      const dragImage = document.querySelector(".dragged-item");
      event.dataTransfer.setDragImage(dragImage, 0, 0);
    },
    async addDatasets(project) {
      this.showMenu = false;
      this.error = null;
      let added = [];

      this.$store.commit("setSnackbar", {
        isOpen: true,
        text: `Adding datasets to ${project.title}`,
        color: "info"
      });

      try {
        for (let selected of this.selectedByCategory) {
          const mutation = await this.addDataSet(
            selected.category,
            selected.url,
            project.id
          );
          added.push(
            Object.assign(mutation, {
              project: project.id
            })
          );
        }
      } catch (error) {
        this.error = error;
        this.$store.commit("setSnackbar", {
          isOpen: false
        });
      }

      if (added.length !== 0) {
        this.$store.commit("setSnackbar", {
          isOpen: true,
          text: `Added ${added.length} datasets to ${project.title}`,
          color: "success"
        });
      }
    }
  },
  computed: {
    selectedByCategory() {
      return this.selected.reduce((list, current) => {
        Object.entries(current.form).forEach(category => {
          const [key, value] = category;
          if (value) {
            list.push({
              category: key,
              url: current.url
            });
          }
        });
        return list;
      }, []);
    }
  },
  watch: {
    items(list) {
      this.repositories = this.addFormValues(list);
    },
    showLoader(value) {
      this.isLoading = value;
    }
  },
  mounted() {
    this.repositories = this.addFormValues(this.items);
  }
};
</script>

<style lang="scss" scoped>
@import "../styles/_buttons";
@import "../styles/_lists";
@import "../styles/_tables";

::v-deep
  .theme--light.v-data-table
  > .v-data-table__wrapper
  > table
  > tbody
  > tr {
  cursor: grab;
}

.dragged-item {
  max-width: 300px;
  position: absolute;
  top: -300px;
}

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
</style>
