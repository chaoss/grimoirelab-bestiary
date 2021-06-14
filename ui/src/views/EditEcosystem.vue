<template>
  <div v-if="ecosystem" class="pa-5">
    <breadcrumbs :items="breadcrumbs" />
    <ecosystem-form
      :save-function="save"
      :name="ecosystem.name"
      :title="ecosystem.title"
      :description="ecosystem.description"
    />
  </div>
</template>

<script>
import Breadcrumbs from "../components/Breadcrumbs";
import EcosystemForm from "../components/EcosystemForm";
import { getEcosystemByID } from "../apollo/queries";
import { updateEcosystem } from "../apollo/mutations";

export default {
  name: "EditEcosystem",
  components: { Breadcrumbs, EcosystemForm },
  computed: {
    id() {
      return this.$route.params.id;
    },
    breadcrumbs() {
      return [
        { to: `/ecosystem/${this.id}`, text: this.ecosystem.name, exact: true },
        { text: "Edit ecosystem", disabled: true }
      ];
    }
  },
  data() {
    return {
      ecosystem: null
    };
  },
  methods: {
    async getEcosystemMetadata(id = this.id) {
      try {
        const response = await getEcosystemByID(this.$apollo, id);
        if (response && response.data.ecosystems.entities[0]) {
          return response.data.ecosystems.entities[0];
        }
      } catch (error) {
        this.error = error;
      }
    },
    async save(data) {
      const response = await updateEcosystem(this.$apollo, data, this.id);
      if (response && !response.errors) {
        this.$emit("updateSidebar");
        return response.data.updateEcosystem.ecosystem;
      }
    }
  },
  async mounted() {
    this.ecosystem = await this.getEcosystemMetadata(this.id);
  }
};
</script>
