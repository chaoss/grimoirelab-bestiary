import SourceIcon from "./SourceIcon.vue";

export default {
  title: "SourceIcon",
  excludeStories: /.*Data$/
};

export const Default = () => ({
  components: { SourceIcon },
  template: "<source-icon source='git' />"
});

export const Color = () => ({
  components: { SourceIcon },
  template: "<source-icon source='git' color='primary' />"
});

export const Small = () => ({
  components: { SourceIcon },
  template: "<source-icon source='git' small />"
});
