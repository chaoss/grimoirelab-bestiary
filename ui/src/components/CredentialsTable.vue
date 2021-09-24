<template>
  <section>
    <h3 class="text-h6 d-flex align-center mt-8 mb-6">
      Credentials
      <v-chip small pill class="ml-2 info--text" color="info--background">
        {{ totalResults }}
      </v-chip>
      <v-btn
        class="button--lowercase button--secondary ml-auto"
        :to="{ name: 'credentials-new' }"
        outlined
      >
        <v-icon dense left>mdi-plus</v-icon>
        Add credentials
      </v-btn>
    </h3>
    <v-data-table
      :headers="headers"
      :items="credentials"
      :items-per-page="pageSize"
      :page.sync="page"
      item-key="name"
      sort-by="createdAt"
      hide-default-footer
      :hide-default-header="totalResults === 0"
    >
      <template v-slot:item.datasource.name="{ item }">
        <source-icon
          :source="item.datasource.name"
          color="text"
          class="mr-2 mb-1"
          small
        />
        {{ item.datasource.name }}
      </template>
      <template v-slot:item.createdAt="{ item }">
        <span class="text--secondary">
          {{ new Date(item.createdAt).toLocaleString() }}
        </span>
      </template>
      <template v-slot:item.actions="{ item }">
        <v-btn icon color="text" @click="confirmDelete(item)">
          <v-icon small>
            mdi-trash-can-outline
          </v-icon>
        </v-btn>
      </template>
      <template v-slot:no-data>
        <v-alert text dense color="warning" border="left">
          This user has no access tokens saved.
          <router-link :to="{ name: 'credentials-new' }">
            Add a token
          </router-link>
        </v-alert>
      </template>
    </v-data-table>
    <v-pagination
      v-if="pages !== 1"
      v-model="page"
      :length="pages"
      class="mt-6"
      @input="getCredentials($event)"
    ></v-pagination>
  </section>
</template>

<script>
import SourceIcon from "./SourceIcon";

export default {
  name: "CredentialsTable",
  components: { SourceIcon },
  props: {
    fetchCredentials: {
      type: Function,
      required: true
    },
    deleteCredential: {
      type: Function,
      required: true
    }
  },
  data() {
    return {
      credentials: [],
      page: 1,
      pageSize: 20,
      pages: 1,
      totalResults: 0,
      headers: [
        { text: "Data source", value: "datasource.name" },
        { text: "Name", value: "name" },
        { text: "Date added", value: "createdAt" },
        { text: "", value: "actions" }
      ]
    };
  },
  methods: {
    async getCredentials(page = this.page, pageSize = this.pageSize) {
      const response = await this.fetchCredentials(page, pageSize);
      this.credentials = response.data.credentials.entities;
      this.totalResults = response.data.credentials.pageInfo.totalResults;
      this.pages = response.data.credentials.pageInfo.numPages;
    },
    confirmDelete(item) {
      const dialog = {
        isOpen: true,
        title: `Remove ${item.datasource.name} token "${item.name}"?`,
        action: () => this.removeCredential(item.id)
      };
      this.$store.commit("setDialog", dialog);
    },
    async removeCredential(id) {
      this.$store.commit("clearDialog");
      try {
        const response = await this.deleteCredential(id);
        if (!response.errors) {
          this.getCredentials();
          this.$store.commit("setSnackbar", {
            isOpen: true,
            text: "Token removed successfully",
            color: "success"
          });
        }
      } catch (error) {
        this.$store.commit("setSnackbar", {
          isOpen: true,
          text: error,
          color: "error"
        });
      }
    }
  },
  created() {
    this.getCredentials();
  }
};
</script>

<style lang="scss" scoped>
@import "../styles/_buttons";
@import "../styles/_tables";
</style>
