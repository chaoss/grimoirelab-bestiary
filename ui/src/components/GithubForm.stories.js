import GithubForm from "./GithubForm.vue";

export default {
  title: "GithubForm",
  excludeStories: /.*Data$/
};

const template = `
  <github-form
    :get-projects="getProjects"
    :add-data-set="addDataSet"
    :get-repos="addDataSet"
  />
`;

export const Default = () => ({
  components: { GithubForm },
  template: template,
  data() {
    return {
      projects: [
        { name: "project-1" },
        {
          name: "subproject",
          parentProject: {
            name: "project-1"
          }
        },
        { name: "project-2" }
      ]
    };
  },
  methods: {
    getProjects(filters) {
      return this.projects.filter(project =>
        filters.term ? project.name.includes(filters.term) : true
      );
    },
    addDataSet() {
      return;
    }
  }
});
