import DatasourceList from "./DatasourceList";

export default {
  title: "DatasourceList",
  excludeStories: /.*Data$/
};

const template = '<datasource-list :items="items" project-id="1" />';

export const Default = () => ({
  components: { DatasourceList },
  template: template,
  data() {
    return {
      items: [
        {
          datasource: {
            type: {
              name: "github"
            },
            uri: "https://github.com/organization/repository-1"
          },
          category: "issue"
        },
        {
          datasource: {
            type: {
              name: "github"
            },
            uri: "https://github.com/organization/repository-1"
          },
          category: "prs"
        },
        {
          datasource: {
            type: {
              name: "github"
            },
            uri: "https://github.com/organization/repository-2"
          },
          filters: { tags: ["python", "bug"], from_date: "2021-01-01" },
          category: "issue"
        },
        {
          datasource: {
            type: {
              name: "git"
            },
            uri: "https://github.com/organization/repository-1"
          },
          category: "commit"
        },
        {
          datasource: {
            type: {
              name: "git"
            },
            uri: "https://github.com/organization/repository-2"
          },
          filters: { branches: ["branch_1", "branch_2"] },
          category: "commit"
        },
        {
          datasource: {
            type: {
              name: "jira"
            },
            uri: "https://jira.organization.com"
          },
          filters: {},
          category: "issue"
        },
        {
          datasource: {
            type: {
              name: "twitter"
            },
            uri: "@organization"
          },
          filters: {},
          category: "tweet"
        }
      ]
    };
  }
});
