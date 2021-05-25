import { mount } from "@vue/test-utils";
import Vue from "vue";
import Vuetify from "vuetify";
import Search from "@/components/Search";

Vue.use(Vuetify);

describe("Search", () => {
  const vuetify = new Vuetify();
  const mountFunction = options => {
    return mount(Search, {
      vuetify,
      ...options
    });
  };

  test.each([
    ["test", { term: "test" }],
    [`"test"`, { term: "test" }],
    ["term:test", { term: "test" }],
    [`term:"test"`, { term: "test" }],
    ["test name:value", { term: "test", name: "value" }]
  ])("Gets filters from input value", async (value, expected) => {
    const wrapper = mountFunction({
      data: () => ({ inputValue: value })
    });

    const button = wrapper.find("button.mdi-magnify");
    await button.trigger("click");

    expect(wrapper.vm.filters).toMatchObject(expected);
  });

  test("Shows selected filter on the search box", async () => {
      const wrapper = mountFunction({
        propsData: {
          filterSelector: true,
          validFilters: [
            { filter: "testFilter" }
          ]
        }
      });

      const el = document.createElement("div");
      el.setAttribute("data-app", true);
      document.body.appendChild(el);

      const button = wrapper.find(".btn--focusable");
      await button.trigger("click");
      const filter = wrapper.find(".v-list-item");
      await filter.trigger("click");

      expect(wrapper.vm.inputValue).toContain(`testFilter:"search value"`);
    }
  );

  test("Validates filters", async () => {
    const wrapper = mountFunction({
      propsData: {
        validFilters: [
          { filter: "testFilter" }
        ]
      },
      data: () => ({ inputValue: "invalidFilter:test" })
    });

    const button = wrapper.find("button.mdi-magnify");
    await button.trigger("click");
    const errorMessage = wrapper.find(".v-messages__message");

    expect(errorMessage.exists()).toBe(true);
    expect(errorMessage.text()).toContain("Invalid filter");
  })
})
