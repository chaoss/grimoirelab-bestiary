<template>
  <v-card>
    <v-card-title class="headline">{{ name }}</v-card-title>
    <v-card-subtitle>{{ title }}</v-card-subtitle>
    <v-card-text>{{ description }}</v-card-text>
  </v-card>
</template>

<script>
export default {
  name: "ExampleCard",
  props: {
    name: String,
    title: String,
    description: String
  }
};
</script>
