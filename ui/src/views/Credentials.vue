<template>
  <section>
    <credentials-table
      :fetch-credentials="getCredentials"
      :delete-credential="removeCredential"
    />
  </section>
</template>

<script>
import { getUserCredentials } from "../apollo/queries";
import { deleteCredential } from "../apollo/mutations";
import CredentialsTable from "../components/CredentialsTable";

export default {
  name: "Credentials",
  components: { CredentialsTable },
  methods: {
    async getCredentials(page = this.page, pageSize = this.pageSize) {
      const response = await getUserCredentials(this.$apollo, page, pageSize);
      return response;
    },
    async removeCredential(id) {
      const response = await deleteCredential(this.$apollo, id);
      return response;
    }
  }
};
</script>
