import ProjectSelector from "./ProjectSelector.vue";

export default {
  title: "ProjectSelector",
  excludeStories: /.*Data$/
};

const template = `
  <div>
    <project-selector :get-projects="getProjects" />
  </div>
  `;

export const Default = () => ({
  components: { ProjectSelector },
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
        {
          name: "sub-subproject",
          parentProject: {
            name: "subproject",
            parentProject: {
              name: "project-1"
            }
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
    }
  }
});
