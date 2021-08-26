<template>
  <section class="d-flex flex-column">
    <h3 class="text-h6 mt-6 mb-4">
      Add data sources
    </h3>

    <transition name="opacity">
      <div v-if="isLoading" class="d-flex justify-center">
        <v-progress-circular
          :size="50"
          color="primary"
          indeterminate
        ></v-progress-circular>
      </div>
    </transition>

    <v-form v-if="!isLoading">
      <p class="mt-3 mb-0 text--secondary">
        Load all repositories from a GitHub user or organization. You will be
        able to add all of their commits, pull requests and issues to the
        project or review and select each one individually.
      </p>
      <v-row class="mt-2">
        <v-col cols="4">
          <v-text-field
            v-model="owner"
            label="GitHub owner"
            outlined
            dense
            @keydown.enter.prevent="getGithubOwnerRepos"
          />
        </v-col>
        <v-col>
          <v-btn
            :disabled="!owner"
            color="info"
            class="button--lowercase"
            depressed
            @click.prevent="getGithubOwnerRepos"
          >
            Load
          </v-btn>
        </v-col>
      </v-row>
    </v-form>
  </section>
</template>

<script>
import { fetchGithubOwnerRepos } from "../apollo/mutations";

export default {
  name: "AddDatasources",
  data() {
    return {
      owner: "",
      isLoading: false
    };
  },
  methods: {
    async getGithubOwnerRepos() {
      this.isLoading = true;
      const response = await fetchGithubOwnerRepos(this.$apollo, this.owner);
      if (response.data.fetchGithubOwnerRepos.jobId) {
        this.$router.push({
          name: "github-datasources",
          params: { jobID: response.data.fetchGithubOwnerRepos.jobId }
        });
      }
    }
  }
};
</script>

<style lang="scss" scoped>
.v-progress-circular {
  margin-top: 130px;
}
.opacity-enter {
  opacity: 0;

  &-active {
    transition: opacity 2.5s;
  }
}
</style>
