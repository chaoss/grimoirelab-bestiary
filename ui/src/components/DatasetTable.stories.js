import DatasetTable from "./DatasetTable";

export default {
  title: "DatasetTable",
  excludeStories: /.*Data$/
};

const template = '<dataset-table :datasets="datasets" />';

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
          category: "commit"
        },
        {
          datasource: {
            type: {
              name: "GitHub"
            },
            uri: "https://github.com/organization/repository-1"
          },
          category: "prs"
        },
        {
          datasource: {
            type: {
              name: "GitHub"
            },
            uri: "https://github.com/organization/repository-1"
          },
          category: "issue",
          filters: { tags: ["python", "bug"], from_date: "2021-01-01" }
        }
      ]
    };
  }
});
