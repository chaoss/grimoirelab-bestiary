<template>
  <v-dialog v-model="isOpen" :max-width="width">
    <v-card>
      <v-card-title class="headline">{{ title }}</v-card-title>
      <v-card-text>{{ text }}</v-card-text>
      <v-card-text>
        <v-alert
          v-if="warning"
          type="warning"
          icon="mdi-alert-outline"
          dense
          text
          border="left"
        >
          {{ warning }}
        </v-alert>
        <slot></slot>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="grey darken-2" text @click="$store.commit('clearDialog')">
          Cancel
        </v-btn>
        <v-btn v-if="action" color="primary" text @click.stop="action">
          Continue
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
<script>
export default {
  name: "SimpleDialog",
  props: {
    isOpen: {
      type: Boolean,
      required: true
    },
    title: {
      type: String,
      required: false
    },
    text: {
      type: String,
      required: false
    },
    action: {
      type: Function,
      required: false
    },
    warning: {
      type: String,
      required: false
    },
    width: {
      type: [String, Number],
      required: false,
      default: 400
    }
  }
};
</script>
