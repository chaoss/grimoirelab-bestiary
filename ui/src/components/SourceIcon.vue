<template>
  <v-icon v-text="getIcon(source)" :color="color" :small="small" />
</template>
<script>
export default {
  name: "SourceIcon",
  props: {
    source: {
      type: String,
      required: true
    },
    color: {
      type: String,
      required: false
    },
    small: {
      type: Boolean,
      required: false,
      default: false
    }
  },
  methods: {
    getIcon(source) {
      const icons = [
        { source: "git", icon: "mdi-git" },
        { source: "github", icon: "mdi-github" },
        { source: "gitlab", icon: "mdi-gitlab" },
        { source: "dockerhub", icon: "mdi-docker" },
        { source: "jira", icon: "mdi-jira" },
        { source: "rss", icon: "mdi-rss" },
        { source: "slack", icon: "mdi-slack" },
        { source: "stackexchange", icon: "mdi-stack-exchange" },
        { source: "telegram", icon: "mdi-telegram" },
        { source: "twitter", icon: "mdi-twitter" }
      ];

      const sourceIcon = icons.find(
        icon => icon.source === source.toLowerCase()
      );

      if (sourceIcon) {
        return sourceIcon.icon;
      } else {
        return "";
      }
    }
  }
};
</script>
