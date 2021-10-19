import RepositoryTable from "./RepositoryTable.vue";

export default {
  title: "RepositoryTable",
  excludeStories: /.*Data$/
};

const template = `
  <repository-table
    :items="items"
    :get-projects="getProjects"
    :add-data-set="addDataSet"
    :show-loader="showLoader"
  />
`;

export const Default = () => ({
  components: { RepositoryTable },
  template: template,
  data() {
    return {
      items: [
        {
          url: "https://github.com/organization/repository-1",
          fork: false,
          hasIssues: true
        },
        {
          url: "https://github.com/organization/repository-2",
          fork: false,
          hasIssues: true
        },
        {
          url: "https://github.com/organization/repository-3",
          fork: true,
          hasIssues: false
        },
        {
          url: "https://github.com/organization/repository-4",
          fork: false,
          hasIssues: true
        }
      ],
      projects: [
        { name: "project-1" },
        {
          name: "subproject",
          parentProject: {
            name: "project-1"
          }
        },
        { name: "project-2" }
      ],
      showLoader: false
    };
  },
  methods: {
    getProjects() {
      return this.projects;
    },
    async addDataSet() {
      await this.mockLoading();

      return {};
    },
    mockLoading() {
      return new Promise(resolve => setTimeout(resolve, 200));
    }
  }
});

export const Loading = () => ({
  components: { RepositoryTable },
  template: template,
  data() {
    return {
      items: [],
      projects: [],
      showLoader: true
    };
  },
  methods: {
    getProjects() {
      return this.projects;
    },
    async addDataSet() {
      await this.mockLoading();

      return {};
    },
    mockLoading() {
      return new Promise(resolve => setTimeout(resolve, 200));
    }
  }
});

export const NoResults = () => ({
  components: { RepositoryTable },
  template: template,
  data() {
    return {
      items: [],
      projects: [],
      showLoader: false
    };
  },
  methods: {
    getProjects() {
      return this.projects;
    },
    async addDataSet() {
      await this.mockLoading();

      return {};
    },
    mockLoading() {
      return new Promise(resolve => setTimeout(resolve, 200));
    }
  }
});
