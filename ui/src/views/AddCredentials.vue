<template>
  <section>
    <h3 class="text-h6 mt-8 mb-6">Add credentials</h3>
    <v-form>
      <v-row class="mt-4 pb-4">
        <v-col cols="4">
          <v-select
            v-model="datasource"
            :items="sources"
            label="Data source"
            color="info"
            hide-details
            outlined
            dense
          ></v-select>
        </v-col>
      </v-row>
      <v-row class="mt-4 pb-4">
        <v-col cols="4">
          <v-text-field
            v-model="token"
            label="Token"
            color="info"
            hide-details
            outlined
            dense
          />
        </v-col>
      </v-row>
      <v-row class="mt-4">
        <v-col cols="4">
          <v-text-field
            v-model="name"
            label="Name"
            color="info"
            hide-details
            outlined
            dense
          />
        </v-col>
      </v-row>
      <v-btn
        :disabled="!datasource || !token || !name"
        color="info"
        class="button--lowercase mt-8"
        depressed
        @click.prevent="addToken"
      >
        Save
      </v-btn>
    </v-form>
  </section>
</template>

<script>
import { addCredential } from "../apollo/mutations";
export default {
  name: "AddCredentials",
  data() {
    return {
      sources: ["GitHub", "GitLab"],
      datasource: null,
      token: "",
      name: ""
    };
  },
  methods: {
    async addToken() {
      try {
        const response = await addCredential(
          this.$apollo,
          this.datasource,
          this.token,
          this.name
        );
        if (!response.errors) {
          this.$router.push({ name: "credentials" });
        }
      } catch (error) {
        this.$store.commit("setSnackbar", {
          isOpen: true,
          text: error,
          color: "error"
        });
      }
    }
  }
};
</script>

<style lang="scss" scoped>
@import "../styles/_buttons";
</style>
