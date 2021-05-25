import Search from "./Search.vue";

export default {
  title: "Search",
  excludeStories: /.*Data$/
};

const searchTemplate = `
  <v-col cols="5">
    <search
      :valid-filters='validFilters'
      :filter-selector='filterSelector'
      :filled='filled'
    />
  </v-col>
`;

export const Default = () => ({
  components: { Search },
  template: searchTemplate,
  data() {
    return {
      filterSelector: false,
      validFilters: [],
      filled: false
    };
  }
});

export const Filled = () => ({
  components: { Search },
  template: searchTemplate,
  data() {
    return {
      filterSelector: false,
      validFilters: [],
      filled: true
    };
  }
});

export const filterSelector = () => ({
  components: { Search },
  template: searchTemplate,
  data() {
    return {
      filterSelector: true,
      validFilters: [
        {
          filter: "filter1",
          type: "string"
        },
        {
          filter: "filter2",
          type: "string"
        }
      ],
      filled: false
    };
  }
});
