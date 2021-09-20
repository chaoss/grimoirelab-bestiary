import DatasetTable from "./DatasetTable";

export default {
  title: "DatasetTable",
  excludeStories: /.*Data$/
};

const template = `
  <dataset-table
    :datasets="datasets"
    :delete-dataset="mockFunction"
    :archive-dataset="mockFunction"
    :unarchive-dataset="mockFunction"
  />`;

export const Default = () => ({
  components: { DatasetTable },
  template: template,
  data() {
    return {
      datasets: [
        {
          datasource: {
            type: {
              name: "Git"
            },
            uri: "https://github.com/organization/repository-1"
          },
          filters: { branches: ["branch_1", "branch_2"] },
          category: "commit",
          isArchived: false
        },
        {
          datasource: {
            type: {
              name: "GitHub"
            },
            uri: "https://github.com/organization/repository-1"
          },
          category: "prs",
          isArchived: false
        },
        {
          datasource: {
            type: {
              name: "GitHub"
            },
            uri: "https://github.com/organization/repository-1"
          },
          category: "issue",
          filters: { tags: ["python", "bug"], from_date: "2021-01-01" },
          isArchived: false
        }
      ]
    };
  },
  methods: {
    mockFunction() {}
  }
});

export const Archived = () => ({
  components: { DatasetTable },
  template: template,
  data() {
    return {
      datasets: [
        {
          datasource: {
            type: {
              name: "Git"
            },
            uri: "https://github.com/organization/repository-1"
          },
          filters: { branches: ["branch_1", "branch_2"] },
          category: "commit",
          isArchived: true,
          archivedAt: "2021-09-20T00:00:00.806933+00:00"
        },
        {
          datasource: {
            type: {
              name: "GitHub"
            },
            uri: "https://github.com/organization/repository-1"
          },
          category: "prs",
          isArchived: true,
          archivedAt: "2021-09-20T00:00:00.806933+00:00"
        },
        {
          datasource: {
            type: {
              name: "GitHub"
            },
            uri: "https://github.com/organization/repository-1"
          },
          category: "issue",
          filters: { tags: ["python", "bug"], from_date: "2021-01-01" },
          isArchived: true,
          archivedAt: "2021-09-20T00:00:00.806933+00:00"
        }
      ]
    };
  },
  methods: {
    mockFunction() {}
  }
});
