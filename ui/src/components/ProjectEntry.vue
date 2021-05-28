<template>
  <router-link :to="route" custom v-slot="{ href, route, navigate }">
    <v-list-item :href="href" @click="navigate">
      <v-list-item-content>
        <v-list-item-title v-html="highlightName(path)" />
        <v-list-item-subtitle>{{ title }}</v-list-item-subtitle>
      </v-list-item-content>
    </v-list-item>
  </router-link>
</template>

<script>
export default {
  name: "ProjectEntry",
  props: {
    title: {
      type: String,
      required: true
    },
    path: {
      type: String,
      required: true
    },
    route: {
      type: String,
      required: true
    }
  },
  methods: {
    highlightName(route) {
      let names = route.split("/");
      if (names.length === 1) {
        return `<span>${route}</span>`;
      } else {
        const last = names.pop();
        return `${[...names].join(" / ")} / <span>${last}</span>`;
      }
    }
  }
};
</script>

<style lang="scss" scoped>
::v-deep .v-list-item__title span {
  font-weight: 500;
}
.v-list-item--link::before {
  background-color: #003756;
}
</style>
