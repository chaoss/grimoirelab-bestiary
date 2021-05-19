import SimpleDialog from "./SimpleDialog.vue";

export default {
  title: "SimpleDialog",
  excludeStories: /.*Data$/
};

const SimpleDialogTemplate = `
  <simple-dialog
    :is-open="isOpen"
    :title="title"
    :text="text"
    :action="action"
    :warning="warning"
  />
`;

const SlotDialogTemplate = `
  <simple-dialog
    :is-open="isOpen"
    :title="title"
    :action="action"
    :cancel-action="action"
  >
  <v-icon color="secondary" left>mdi-unicorn</v-icon>
  <kbd>Custom content inside the slot</kbd>
  </simple-dialog>
`;

export const Default = () => ({
  components: { SimpleDialog },
  template: SimpleDialogTemplate,
  data() {
    return {
      isOpen: true,
      warning: null,
      title: "Dialog title",
      text: `Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do
        eiusmod tempor incididunt ut labore et dolore magna aliqua.`
    };
  },
  methods: {
    action() {
      this.isOpen = false;
    }
  }
});

export const Warning = () => ({
  components: { SimpleDialog },
  template: SimpleDialogTemplate,
  data() {
    return {
      isOpen: true,
      title: "Dialog title",
      text: null,
      warning: "Lorem ipsum dolor sit amet"
    };
  },
  methods: {
    action() {
      this.isOpen = false;
    }
  }
});

export const Slot = () => ({
  components: { SimpleDialog },
  template: SlotDialogTemplate,
  data() {
    return {
      isOpen: true,
      title: "Dialog title"
    };
  },
  methods: {
    action() {
      this.isOpen = false;
    }
  }
});
