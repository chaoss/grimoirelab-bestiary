<template>
  <div class="pa-5">
    <h2 v-if="project" class="text-body-1 font-weight-light mb-9">
      Bestiary / {{ project.ecosystem.name }} /
      <span v-if="project.parentProject">
        {{ project.parentProject.name }} /
      </span>
      {{ name }} /
      <span class="font-weight-bold">Edit project</span>
    </h2>
    <project-form
      v-if="showForm"
      :ecosystemId="ecosystemId"
      :get-projects="getParentProjects"
      :save-function="updateProject"
      :name="name"
      :title="project.title"
      :parent="project.parentProject"
    />

    <v-alert v-if="error" text outlined type="error" width="32%" class="mt-9">
      {{ error }}
    </v-alert>
  </div>
</template>

<script>
import ProjectForm from "../components/ProjectForm";
import { getProjects, getProjectByName } from "../apollo/queries";
import { moveProject, updateProject } from "../apollo/mutations";

export default {
  name: "EditProject",
  components: { ProjectForm },
  data() {
    return {
      error: null,
      showForm: false,
      project: null
    };
  },
  computed: {
    ecosystemId() {
      return this.$route.params.id ? Number(this.$route.params.id) : null;
    },
    name() {
      return this.$route.params.name;
    }
  },
  methods: {
    async getProjectMetadata() {
      try {
        const response = await getProjectByName(
          this.$apollo,
          this.name,
          this.ecosystemId
        );
        if (response && response.data.projects.entities[0]) {
          this.project = response.data.projects.entities[0];
          this.showForm = true;
        } else {
          this.error = "Project not found";
        }
      } catch (error) {
        this.error = error;
      }
    },
    async getParentProjects(ecosystem, pageSize = 50, page = 1) {
      const response = await getProjects(this.$apollo, pageSize, page, {
        ecosystemId: ecosystem
      });
      if (response && !response.errors) {
        return this.validateParentProjects(response.data.projects.entities);
      }
    },
    async updateProject(formData) {
      const data = {
        name: formData.name,
        title: formData.title,
        parentProject: formData.parentId
      };
      try {
        const response = await updateProject(
          this.$apollo,
          data,
          this.project.id
        );
        if (response && !response.errors) {
          if (
            formData.parentId &&
            formData.parentId.toString() !==
              (this.project.parentProject
                ? this.project.parentProject.id.toString()
                : null)
          ) {
            try {
              await this.moveProject(this.project.id, formData.parentId);
            } catch (error) {
              this.error = error;
              return;
            }
          }
          this.$emit("updateSidebar");
          return response.data.updateProject.project;
        }
      } catch (error) {
        this.error = error;
      }
    },
    async moveProject(from, to) {
      const response = await moveProject(this.$apollo, from, to);
      return response;
    },
    validateParentProjects(projects) {
      return projects.filter(project => {
        if (project.name === this.name) {
          return false;
        } else if (
          this.project.parentProject &&
          this.getRoot(this.project.parentProject).id !==
            this.getRoot(project).id
        ) {
          // If the project is not a root one, when the parent comes from a
          // different root project.
          return false;
        } else if (this.isDescendant(project, this.project)) {
          return false;
        }
        return true;
      });
    },
    getRoot(project) {
      const parent = project ? project.parentProject : null;
      if (parent) {
        project = this.getRoot(parent);
      }
      return project;
    },
    isDescendant(project, fromProject) {
      const queue = [fromProject];
      while (queue.length > 0) {
        const current = queue.pop(0);
        if (current.subprojects) {
          for (let subproject of current.subprojects) {
            if (subproject.id === project.id) {
              return true;
            }
            queue.push(subproject);
          }
        }
      }
    }
  },
  mounted() {
    this.getProjectMetadata();
  }
};
</script>
