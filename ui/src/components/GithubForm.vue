<template>
  <div>
    <v-btn-toggle v-model="mode" class="mt-8" color="info" mandatory>
      <v-btn value="single" class="button--lowercase" text outlined>
        Add a repository
      </v-btn>

      <v-btn value="multiple" class="button--lowercase" text outlined>
        Load all from owner
      </v-btn>
    </v-btn-toggle>
    <v-form v-if="!token">
      <h5 class="text-subtitle-2 mt-8 mb-2">Add a GitHub token (optional)</h5>
      <p class="text-body-2 text--secondary">
        You can add a token to access the GitHub API and a name to identify it.
      </p>
      <v-row class="mt-4 pb-4">
        <v-col cols="6">
          <v-text-field
            v-model="newToken"
            label="Token"
            color="info"
            hide-details
            outlined
            dense
          />
        </v-col>
      </v-row>
      <v-row class="mt-4">
        <v-col cols="6">
          <v-text-field
            v-model="tokenName"
            label="Name"
            color="info"
            hide-details
            outlined
            dense
          />
        </v-col>
      </v-row>
      <div class="d-flex justify-end pb-4">
        <v-btn
          :disabled="!newToken || !tokenName"
          color="info"
          class="button--lowercase"
          depressed
          @click.prevent="addCredential"
        >
          Save
        </v-btn>
      </div>
      <v-divider class="mt-4" />
    </v-form>

    <transition name="fade" mode="out-in">
      <v-form v-if="mode === 'single'" class="v-list" key="single">
        <h5 class="text-subtitle-2 mt-6 mb-2">Add repositories</h5>
        <p class="text-body-2  text--secondary">
          Add the URL of the repository and select the data that you want to
          analyze.
        </p>
        <fieldset
          v-for="(repo, index) in repositories"
          :key="index"
          class="mt-4 pb-4 d-flex align-center"
        >
          <v-col cols="6" class="mr-6 pl-0">
            <v-text-field
              v-model="repo.url"
              label="Repository URL"
              color="info"
              hide-details
              outlined
              dense
              @keydown.enter.prevent="getGithubOwnerRepos"
            />
          </v-col>
          <v-checkbox
            v-model="repo.selected"
            label="Commits"
            value="commit"
            color="info"
            class="mr-6"
          ></v-checkbox>
          <v-checkbox
            v-model="repo.selected"
            label="Issues"
            value="issue"
            color="info"
            class="mr-6"
          ></v-checkbox>
          <v-checkbox
            v-model="repo.selected"
            label="Pull Requests"
            value="pr"
            color="info"
            class="mr-8"
          ></v-checkbox>
          <v-tooltip right>
            <template v-slot:activator="{ on }">
              <v-btn
                icon
                color="error"
                v-on="on"
                @click="removeFieldset(index)"
              >
                <v-icon dense>mdi-minus-circle-outline</v-icon>
              </v-btn>
            </template>
            <span>Remove</span>
          </v-tooltip>
        </fieldset>
        <v-row class="mt-2">
          <v-col>
            <v-btn
              class="button--lowercase button--secondary"
              outlined
              @click="addFieldset"
            >
              <v-icon small left>mdi-plus</v-icon>
              Add another
            </v-btn>
          </v-col>
        </v-row>
        <div class="d-flex justify-end">
          <project-selector
            :get-projects="getProjects"
            :disabled="disableSelector"
            @selectedProject="addDatasets"
          />
        </div>
      </v-form>
      <v-form v-else>
        <h5 class="text-subtitle-2 mt-6 mb-2">GitHub owner</h5>
        <p class="mt-3 mb-0 text-body-2  text--secondary">
          Load all repositories from a GitHub user or organization. You will be
          able to add all of their commits, pull requests and issues to the
          project or review and select each one individually.
        </p>
        <v-row class="mt-2">
          <v-col cols="6">
            <v-text-field
              v-model="owner"
              label="GitHub owner"
              outlined
              dense
              @keydown.enter.prevent="getRepos(owner)"
            />
          </v-col>
          <v-col>
            <v-btn
              :disabled="!owner"
              color="info"
              class="button--lowercase"
              depressed
              @click.prevent="getRepos(owner)"
            >
              Load
            </v-btn>
          </v-col>
        </v-row>
      </v-form>
    </transition>
  </div>
</template>

<script>
import ProjectSelector from "../components/ProjectSelector";

export default {
  name: "GithubForm",
  components: { ProjectSelector },
  props: {
    getProjects: {
      type: Function,
      required: true
    },
    addDataSet: {
      type: Function,
      required: true
    },
    getRepos: {
      type: Function,
      required: true
    },
    getToken: {
      type: Function,
      required: true
    },
    addToken: {
      type: Function,
      required: true
    }
  },
  data() {
    return {
      mode: "single",
      repositories: [
        {
          url: "",
          selected: ["commit", "pr", "issue"]
        }
      ],
      projects: [],
      owner: "",
      token: null,
      newToken: "",
      tokenName: ""
    };
  },
  computed: {
    disableSelector() {
      return !this.repositories.some(
        repo => repo.url.length > 0 && repo.selected.length > 0
      );
    },
    repositoriesByCategory() {
      return this.repositories.reduce((list, current) => {
        current.selected.forEach(category => {
          if (current.url.length > 0) {
            list.push({
              category: category,
              url: current.url
            });
          }
        });
        return list;
      }, []);
    }
  },
  methods: {
    addFieldset() {
      this.repositories.push({
        url: "",
        selected: ["commit", "pr", "issue"]
      });
    },
    removeFieldset(index) {
      this.repositories.splice(index, 1);
    },
    async addDatasets(project) {
      let added = [];
      try {
        for (let repo of this.repositoriesByCategory) {
          const mutation = await this.addDataSet(
            repo.category,
            "GitHub",
            repo.url,
            project.id
          );
          added.push(
            Object.assign(mutation, {
              project: project.id
            })
          );
        }
      } catch (error) {
        this.$store.commit("setSnackbar", {
          isOpen: true,
          text: error,
          color: "error"
        });
      }
      if (added.length !== 0) {
        this.$store.commit("setSnackbar", {
          isOpen: true,
          text: `Added ${added.length} datasets to ${project.title}`,
          color: "success"
        });
        this.$router.push({
          name: "project",
          params: {
            name: project.name,
            ecosystemId: project.ecosystem.id
          }
        });
      }
    },
    async addCredential() {
      this.error = null;
      try {
        const response = await this.addToken("GitHub", this.newToken, this.tokenName);
        if (response.data.addCredential.credential.id) {
          this.newToken = "";
          this.tokenName = "";
          this.$store.commit("setSnackbar", {
            isOpen: true,
            text: `Token added successfully.`,
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
  async mounted() {
    const response = await this.getToken("GitHub");
    if (response.data.credentials.entities.length > 0) {
      this.token = response.data.credentials.entities.[0].token;
    }
  }
};
</script>

<style lang="scss" scoped>
@import "../styles/_buttons";
@import "../styles/_transitions";
@import "../styles/_variables";

::v-deep .v-input--selection-controls__input + .v-label {
  font-size: 0.875rem;
  font-weight: 500;
}

fieldset {
  border: 0;

  &:not(:last-of-type) {
    border-bottom: thin solid $border-color;
  }
}
</style>
