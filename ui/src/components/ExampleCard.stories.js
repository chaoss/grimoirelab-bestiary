import ExampleCard from "./ExampleCard.vue";

export default {
  title: "ExampleCard",
  excludeStories: /.*Data$/
};

const exampleCardTemplate =
  '<example-card :name="name" :description="description" :title="title" />';

export const Default = () => ({
  components: { ExampleCard },
  template: exampleCardTemplate,
  props: {
    name: {
      default: "Ecosystem name"
    },
    title: {
      default: "Ecosystem title"
    },
    description: {
      default: "Ecosystem description"
    }
  }
});
