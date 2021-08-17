<template>
  <section>
    <div class="d-flex justify-space-between mb-3">
      <h3 class="text-h6 d-flex align-center">
        Data sets
        <v-chip small pill class="ml-2 info--text" color="info--background">
          {{ datasets.length }}
        </v-chip>
      </h3>
    </div>
    <v-simple-table>
      <template v-slot:default>
        <thead>
          <tr>
            <th class="text-left">
              Source
            </th>
            <th class="text-left">
              Category
            </th>
            <th class="text-left">
              Filters
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(item, i) in datasets" :key="i" class="table-row">
            <td class="text-start">
              <source-icon
                :source="item.datasource.type.name"
                color="rgba(0, 0, 0, 0.87)"
                class="mr-2"
                small
              />
              {{ item.datasource.type.name }}
            </td>

            <td>{{ item.category }}</td>

            <td class="text-start pt-1 pb-1">
              <p v-for="(value, key) in item.filters" :key="key" class="filter">
                <span class="mr-1 font-weight-medium">{{ key }}:</span>
                <v-chip
                  v-if="typeof value === 'string'"
                  label
                  class="ma-0 mr-1"
                  small
                >
                  <span>{{ value }}</span>
                </v-chip>
                <span v-else-if="typeof value === 'object'">
                  <v-chip
                    v-for="(val, index) in value"
                    :key="index"
                    label
                    class="ma-0 mr-1"
                    small
                  >
                    <span>{{ val.toString().replace("[]", "") }}</span>
                  </v-chip>
                </span>
              </p>
            </td>
          </tr>
        </tbody>
      </template>
    </v-simple-table>
  </section>
</template>

<script>
import SourceIcon from "./SourceIcon";

export default {
  name: "DatasetTable",
  components: { SourceIcon },
  props: {
    datasets: {
      type: Array,
      required: true
    }
  }
};
</script>

<style lang="scss" scoped>
.theme--light.v-data-table
  > .v-data-table__wrapper
  > table
  > tbody
  > .table-row:hover:not(.v-data-table__empty-wrapper) {
  background: #f6fbff;
}

.filter:last-of-type {
  margin-bottom: 0;
}
</style>
