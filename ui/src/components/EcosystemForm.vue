<template>
  <v-form ref="form">
    <v-row>
      <v-col cols="4">
        <v-text-field
          v-model="form.title"
          :rules="validations.required"
          label="Ecosystem title"
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
          :rules="validations.required"
          label="Ecosystem name"
          outlined
          dense
          @input="touchedName = true"
        ></v-text-field>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="4">
        <v-textarea
          v-model="form.description"
          label="Ecosystem description (optional)"
          :rules="validations.maxLength"
          outlined
          dense
          counter="128"
          rows="4"
        ></v-textarea>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="4" class="d-flex justify-end">
        <v-btn color="primary" depressed @click="save">
          Save
        </v-btn>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="4">
        <v-alert v-if="error" text outlined type="error">
          {{ error }}
        </v-alert>
      </v-col>
    </v-row>
  </v-form>
</template>

<script>
export default {
  name: "EcosystemForm",
  props: {
    saveFunction: {
      type: Function,
      required: true
    },
    id: {
      type: [Number, String],
      required: false
    },
    name: {
      type: String,
      required: false
    },
    title: {
      type: String,
      required: false
    },
    description: {
      type: String,
      required: false
    }
  },
  data() {
    return {
      form: {
        name: this.name,
        title: this.title,
        description: this.description
      },
      validations: {
        required: [v => !!v || "Required"],
        maxLength: [v => (v ? v.length <= 128 : true) || "Max 128 characters"]
      },
      touchedName: false,
      error: null
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
    async save() {
      if (!this.$refs.form.validate()) {
        return;
      }
      try {
        const data = {
          name: this.form.name.trim(),
          title: this.form.title.trim(),
          description: this.form.description
        };
        const response = await this.saveFunction(data);
        if (response && !response.errors) {
          this.$router.push({ path: `/ecosystem/${response.id}` });
        } else if (response.errors) {
          this.error = response.errors[0].message;
        }
      } catch (error) {
        this.error = error;
      }
    }
  }
};
</script>
