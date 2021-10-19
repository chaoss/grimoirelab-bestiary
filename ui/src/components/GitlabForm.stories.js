import GitlabForm from "./GitlabForm.vue";

export default {
  title: "GitlabForm",
  excludeStories: /.*Data$/
};

const template = `
  <gitlab-form
    :get-projects="getProjects"
    :add-data-set="mockAction"
    :get-repos="mockAction"
    :get-token="getToken"
    :add-token="mockAction"
  />
`;

const projects = [
  { name: "project-1" },
  {
    name: "subproject",
    parentProject: {
      name: "project-1"
    }
  },
  { name: "project-2" }
];

export const Default = () => ({
  components: { GitlabForm },
  template: template,
  data() {
    return {
      projects: projects
    };
  },
  methods: {
    getProjects(filters) {
      return this.projects.filter(project =>
        filters.term ? project.name.includes(filters.term) : true
      );
    },
    mockAction() {
      return;
    },
    getToken() {
      return {
        data: {
          credentials: {
            entities: [{ token: "Example token" }]
          }
        }
      };
    }
  }
});

export const NoToken = () => ({
  components: { GitlabForm },
  template: template,
  data() {
    return {
      projects: projects
    };
  },
  methods: {
    getProjects(filters) {
      return this.projects.filter(project =>
        filters.term ? project.name.includes(filters.term) : true
      );
    },
    mockAction() {
      return;
    },
    getToken() {
      return {
        data: {
          credentials: {
            entities: []
          }
        }
      };
    }
  }
});
