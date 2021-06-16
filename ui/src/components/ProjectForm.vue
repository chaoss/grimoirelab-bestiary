<template>
  <v-form ref="form">
    <v-row>
      <v-col cols="4">
        <v-text-field
          v-model="form.title"
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
          v-model="form.name"
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
          v-model="form.parentId"
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
    saveFunction: {
      type: Function,
      required: true
    },
    name: {
      type: String,
      required: false
    },
    title: {
      type: String,
      required: false
    },
    parent: {
      type: Object,
      required: false,
      default: null
    }
  },
  data() {
    return {
      form: {
        name: this.name,
        title: this.title,
        parentId: null
      },
      touchedName: false,
      projects: [],
      validations: {
        required: [value => !!value || "Required"]
      }
    };
  },
  methods: {
    suggestName(value) {
      if (value && !this.name && !this.touchedName) {
        this.form.name = value
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
        name: this.form.name.trim(),
        title: this.form.title,
        parentId: this.form.parentId,
        ecosystemId: this.ecosystemId
      };
      const response = await this.saveFunction(data);
      if (response) {
        const projectName = response.name;
        this.$router.push({
          path: `/ecosystem/${this.ecosystemId}/project/${projectName}`
        });
      }
    }
  },
  watch: {
    title(value) {
      this.form.title = value;
    },
    parent(value) {
      this.loadParentProjects();
      this.form.parentId = value.id;
    }
  },
  created() {
    if (this.parent) {
      this.loadParentProjects();
      this.form.parentId = this.parent.id;
    }
  }
};
</script>
