<template>
  <div class="pa-5">
    <breadcrumbs :items="[{ text: 'New ecosystem', disabled: true }]" />
    <ecosystem-form :save-function="save" />
  </div>
</template>

<script>
import Breadcrumbs from "../components/Breadcrumbs";
import EcosystemForm from "../components/EcosystemForm";
import { addEcosystem } from "../apollo/mutations";

export default {
  name: "NewEcosystem",
  components: {
    Breadcrumbs,
    EcosystemForm
  },
  methods: {
    async save(data) {
      const response = await addEcosystem(this.$apollo, data);
      if (response) {
        this.$emit("updateSidebar");
        return response.data.addEcosystem.ecosystem;
      }
    }
  }
};
</script>
