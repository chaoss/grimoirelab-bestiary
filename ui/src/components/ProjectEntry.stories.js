import ProjectEntry from "./ProjectEntry.vue";

export default {
  title: "ProjectEntry",
  excludeStories: /.*Data$/
};

const template = `
  <v-list two-line>
    <project-entry :title='title' :route='route' :path='path' />
  </v-list>
`;

export const Default = () => ({
  components: { ProjectEntry },
  template: template,
  data() {
    return {
      title: "Project Title",
      route: "/ecosystem/0/project/name",
      path: "ecosystem / name"
    };
  }
});
