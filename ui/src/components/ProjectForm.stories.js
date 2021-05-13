import ProjectForm from "./ProjectForm.vue";

export default {
  title: "ProjectForm",
  excludeStories: /.*Data$/
};

const ProjectFormTemplate = `
  <project-form
    :ecosystemId="1"
    :get-projects="getProjects"
    :add-project="addProject"
  />
`;

export const Default = () => ({
  components: { ProjectForm },
  template: ProjectFormTemplate,
  data() {
    return {
      projects: [
        { id: 1, title: "Project 1" },
        { id: 2, title: "Project 2" }
      ]
    };
  },
  methods: {
    getProjects() {
      return this.projects;
    },
    addProject() {
      return;
    }
  }
});
