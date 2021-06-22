<template>
  <v-app>
    <v-main class="align-center">
      <v-container>
        <v-card class="mx-auto pa-7 elevation-0" max-width="500">
          <v-card-title class="display-1 mb-2">Welcome</v-card-title>
          <v-card-subtitle class="mb-3"
            >Please log in to continue</v-card-subtitle
          >
          <v-card-text>
            <v-form ref="form">
              <v-text-field
                v-model="username"
                label="Username"
                outlined
                dense
              />
              <v-text-field
                v-model="password"
                label="Password"
                :append-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
                :type="showPassword ? 'text' : 'password'"
                outlined
                dense
                @click:append="showPassword = !showPassword"
              />
              <v-alert v-if="errorMessage" text type="error">
                {{ errorMessage }}
              </v-alert>
              <v-btn
                depressed
                block
                color="primary"
                :disabled="disableSubmit"
                @click.prevent="submit"
              >
                Log in
              </v-btn>
            </v-form>
          </v-card-text>
        </v-card>
      </v-container>
    </v-main>
  </v-app>
</template>

<script>
import { mapActions } from "vuex";

export default {
  name: "Login",
  data() {
    return {
      username: "",
      password: "",
      showPassword: false,
      errorMessage: ""
    };
  },
  computed: {
    disableSubmit() {
      return this.username.length < 2 || this.password.length < 2;
    }
  },
  methods: {
    ...mapActions(["login"]),
    async submit() {
      try {
        const authDetails = {
          apollo: this.$apollo,
          username: this.username,
          password: this.password
        };
        const response = await this.login(authDetails);
        if (response) {
          this.$router.push("/");
        }
      } catch (error) {
        this.errorMessage = error;
      }
    }
  }
};
</script>

<style lang="scss" scoped>
.v-main {
  background-color: #f5f7f8;
}
</style>
