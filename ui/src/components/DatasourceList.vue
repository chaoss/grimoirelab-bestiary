<template>
  <section>
    <div class="d-flex justify-space-between">
      <h3 class="text-h6 d-flex align-center">
        Data sources
        <v-chip small pill class="ml-2 info--text" color="info--background">
          {{ count }}
        </v-chip>
      </h3>
      <v-btn
        class="button--lowercase button--secondary"
        outlined
        :to="{ name: 'add-datasources' }"
      >
        <v-icon dense left>mdi-plus</v-icon>
        Add data source
      </v-btn>
    </div>

    <v-list>
      <router-link
        v-for="(value, uri) in list"
        :key="uri"
        :to="{
          name: 'datasource',
          params: {
            id: projectId,
            uri: uri
          }
        }"
        custom
        v-slot="{ href, route, navigate }"
      >
        <v-list-item class="v-list-item--link">
          <v-list-item-content :href="href" @click="navigate">
            <v-list-item-title>
              <span class="mr-4">{{ uri }}</span>
              <v-chip
                v-for="item in value"
                :key="item.category"
                class="mr-2"
                outlined
                small
              >
                <source-icon
                  :source="item.datasource.type.name"
                  class="mr-1"
                  small
                />
                {{ item.category }}
              </v-chip>
            </v-list-item-title>
          </v-list-item-content>
          <v-list-item-action>
            <v-btn icon color="text" @click.stop="confirmDelete(value, uri)">
              <v-icon small>
                mdi-trash-can-outline
              </v-icon>
            </v-btn>
          </v-list-item-action>
        </v-list-item>
      </router-link>
    </v-list>
  </section>
</template>

<script>
import SourceIcon from "./SourceIcon";

export default {
  name: "DatasourceList",
  components: { SourceIcon },
  props: {
    items: {
      type: Array,
      required: true
    },
    projectId: {
      type: [String, Number],
      required: true
    },
    deleteDataset: {
      type: Function,
      required: true
    }
  },
  data() {
    return {
      list: []
    };
  },
  computed: {
    count() {
      return Object.entries(this.list).length;
    }
  },
  methods: {
    groupByUri(sources) {
      return sources.reduce((acc, current) => {
        acc[current.datasource.uri] = acc[current.datasource.uri] || [];
        acc[current.datasource.uri].push(current);
        return acc;
      }, {});
    },
    confirmDelete(datasets, uri) {
      const dialog = {
        isOpen: true,
        title: `Remove all datasets for ${uri}?`,
        action: () => this.deleteDatasets(datasets)
      };
      this.$store.commit("setDialog", dialog);
    },
    async deleteDatasets(datasets) {
      try {
        for (let dataset of datasets) {
          await this.deleteDataset(dataset.id);
        }
        this.$store.commit("setSnackbar", {
          isOpen: true,
          text: "Data source removed successfully",
          color: "success"
        });
      } catch (error) {
        this.$store.commit("setSnackbar", {
          isOpen: true,
          text: error,
          color: "error"
        });
      } finally {
        this.$store.commit("clearDialog");
        this.$emit("updateDatasets");
      }
    }
  },
  mounted() {
    this.list = this.groupByUri(this.items);
  },
  watch: {
    items(items) {
      this.list = this.groupByUri(items);
    }
  }
};
</script>

<style lang="scss" scoped>
@import "../styles/_buttons";
@import "../styles/_lists";
</style>
