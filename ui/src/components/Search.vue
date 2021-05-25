<template>
  <v-text-field
    v-model.trim="inputValue"
    label="Search projects"
    prepend-inner-icon="mdi-magnify"
    clear-icon="mdi-close-circle-outline"
    ref="searchInput"
    :error-messages="errorMessage"
    :outlined="!filled"
    :solo="filled"
    :flat="filled"
    clearable
    dense
    single-line
    @click:prepend-inner="search"
    @keyup.enter="search"
    @click:clear="clearInput"
  >
    <template v-slot:append-outer v-if="filterSelector">
      <v-menu offset-y>
        <template v-slot:activator="{ on, attrs }">
          <v-btn
            class="btn--focusable text-body-1"
            outlined
            height="40"
            v-bind="attrs"
            v-on="on"
          >
            Filters
            <v-icon small right>mdi-chevron-down</v-icon>
          </v-btn>
        </template>
        <v-list dense class="mt-1">
          <v-list-item
            v-for="(item, i) in validFilters.filter(o => o.filter !== 'term')"
            :key="i"
            @click="setFilter(item)"
          >
            <v-list-item-title>
              {{ item.filter }}
            </v-list-item-title>
          </v-list-item>
        </v-list>
      </v-menu>
    </template>
  </v-text-field>
</template>

<script>
export default {
  name: "Search",
  props: {
    filled: {
      type: Boolean,
      required: false
    },
    setValue: {
      type: String,
      required: false
    },
    filterSelector: {
      type: Boolean,
      required: false,
      default: false
    },
    validFilters: {
      type: Array,
      required: false,
      default: () => [
        {
          filter: "term",
          type: "string"
        },
        {
          filter: "name",
          type: "string"
        },
        {
          filter: "title",
          type: "string"
        }
      ]
    }
  },
  data() {
    return {
      inputValue: this.setValue,
      filters: {},
      errorMessage: null
    };
  },
  methods: {
    async search() {
      await this.parseFilters();
      if (this.errorMessage) return;
      this.$refs.searchInput.focus(false);
      this.$emit("search", this.filters);
    },
    parseFilters() {
      const terms = [];
      this.filters = {};
      this.errorMessage = null;

      if (!this.inputValue) return this.filters;

      const input = this.parseQuotes(this.inputValue);
      input.split(" ").forEach(value => {
        if (value.includes(":")) {
          const [filter, text] = value.split(":");
          if (!this.validFilters.find(vfilter => vfilter.filter === filter)) {
            this.errorMessage = `Invalid filter "${filter}"`;
          } else {
            this.filters[filter] = text;
          }
        } else if (value.trim()) {
          terms.push(value.replace(/"/g, ""));
        }
      });
      if (terms.length !== 0) {
        this.filters.term = terms.join(" ").trim();
      }
    },
    parseQuotes(input) {
      const regexp = /(\w*):"(.*?)"/gm;
      const matches = [...input.matchAll(regexp)];

      matches.forEach(match => {
        const filter = match[1];
        const value = match[2];
        if (this.validFilters.find(vfilter => vfilter.filter === filter)) {
          this.filters[filter] = value;
          input = input.replace(match[0], "");
        } else {
          this.errorMessage = `Invalid filter "${filter}"`;
        }
      });

      return input;
    },
    clearInput() {
      this.inputValue = null;
      this.filters = {};
      this.errorMessage = null;
    },
    setFilter(item) {
      this.inputValue = this.inputValue || "";
      this.inputValue += ` ${item.filter}:"search value" `;
    }
  },
  watch: {
    setValue(value) {
      this.inputValue = value;
    }
  },
  mounted() {
    if (this.inputValue) {
      this.search();
    }
  }
};
</script>

<style lang="scss" scoped>
@import "../styles/_buttons";
.v-text-field--enclosed.v-input--dense:not(.v-text-field--solo).v-text-field--outlined
  ::v-deep
  .v-input__append-outer {
  margin-top: 0;

  .v-btn__content {
    text-transform: none;
    letter-spacing: normal;
  }
}

.v-text-field--solo-flat {
  font-size: 0.875rem;

  ::v-deep .v-label {
    font-size: 0.875rem;
  }

  ::v-deep .v-icon {
    font-size: 1.1rem;
  }

  &.v-text-field--enclosed:not(.v-text-field--rounded)
    > ::v-deep
    .v-input__control
    > .v-input__slot {
    padding: 0 4px;
  }
}
</style>
