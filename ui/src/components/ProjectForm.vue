<template>
  <v-form ref="form">
    <v-row>
      <v-col cols="4">
        <v-text-field
          v-model="title"
          label="Project title"
          :rules="validations.required"
          outlined
          dense
          @change="suggestName"
        ></v-text-field>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="4">
        <v-text-field
          v-model="name"
          label="Project name"
          :rules="validations.required"
          outlined
          dense
          @input="touchedName = true"
        ></v-text-field>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="4">
        <v-autocomplete
          v-model="parentId"
          :items="projects"
          label="Parent project (optional)"
          item-text="title"
          item-value="id"
          clearable
          outlined
          dense
          @click.once="loadParentProjects"
        >
          <template v-slot:no-data>
            <v-list-item>
              <v-list-item-content>
                <v-list-item-title class="text--disabled">
                  No available projects
                </v-list-item-title>
              </v-list-item-content>
            </v-list-item>
          </template>
        </v-autocomplete>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="4" class="d-flex justify-end">
        <v-btn color="primary" depressed @click="save">
          Save
        </v-btn>
      </v-col>
    </v-row>
  </v-form>
</template>

<script>
export default {
  name: "ProjectForm",
  props: {
    ecosystemId: {
      type: Number,
      required: false
    },
    getProjects: {
      type: Function,
      required: true
    },
    addProject: {
      type: Function,
      required: true
    },
    parent: {
      type: Object,
      required: false,
      default: null
    }
  },
  data() {
    return {
      name: null,
      title: null,
      parentId: null,
      touchedName: false,
      projects: [],
      validations: {
        required: [value => !!value || "Required"]
      }
    };
  },
  methods: {
    suggestName(value) {
      if (value && !this.touchedName) {
        this.name = value
          .trim()
          .replace(/\s+/g, "-")
          .toLowerCase();
      }
    },
    async loadParentProjects() {
      const response = await this.getProjects(Number(this.ecosystemId));
      if (response) {
        this.projects = response;
      }
    },
    async save() {
      if (!this.$refs.form.validate()) {
        return;
      }
      const data = {
        name: this.name.trim(),
        title: this.title,
        parentId: this.parentId ? Number(this.parentId) : null,
        ecosystemId: this.ecosystemId
      };
      const response = await this.addProject(data);
      if (response) {
        const projectName = response.name;
        this.$router.push({
          path: `/ecosystem/${this.ecosystemId}/project/${projectName}`
        });
      }
    }
  },
  created() {
    if (this.parent) {
      this.loadParentProjects();
      this.parentId = this.parent.id;
    }
  }
};
</script>
