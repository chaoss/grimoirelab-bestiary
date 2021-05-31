import Breadcrumbs from "./Breadcrumbs";

export default {
  title: "Breadcrumbs",
  excludeStories: /.*Data$/
};

const template = '<breadcrumbs :items="items" />';

export const Default = () => ({
  components: { Breadcrumbs },
  template: template,
  data() {
    return {
      items: [
        { text: "ecosystem", to: "/ecosystem/test" },
        { text: "project", to: "/ecosystem/test/project/test" },
        { text: "New project", disabled: true }
      ]
    };
  }
});
