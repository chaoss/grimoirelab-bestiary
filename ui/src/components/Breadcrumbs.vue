<template>
  <v-breadcrumbs :items="items" class="pb-9 pl-0" />
</template>

<script>
export default {
  name: "Breadcrumbs",
  props: {
    items: {
      type: Array,
      required: true
    }
  }
};
</script>

<style lang="scss" scoped>
.theme--light.v-breadcrumbs ::v-deep .v-breadcrumbs__item {
  font-size: 1rem;
  font-weight: 300;
  color: rgba(0, 0, 0, 0.87);
  letter-spacing: 0.03em;

  &:hover {
    text-decoration: underline;
  }

  &--disabled {
    font-weight: 700;
    color: rgba(0, 0, 0, 0.87);
  }
}
</style>
