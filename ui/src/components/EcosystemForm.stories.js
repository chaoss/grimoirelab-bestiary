import EcosystemForm from "./EcosystemForm.vue";

export default {
  title: "EcosystemForm",
  excludeStories: /.*Data$/
};

const template = `<ecosystem-form :save-function="mockAction" />`;

export const Default = () => ({
  components: { EcosystemForm },
  template: template,
  methods: {
    mockAction() {
      return true;
    }
  }
});
