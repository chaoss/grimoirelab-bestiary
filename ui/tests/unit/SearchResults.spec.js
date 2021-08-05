import { shallowMount } from "@vue/test-utils";
import Vue from "vue";
import Vuetify from "vuetify";
import SearchResults from "@/views/SearchResults";

Vue.use(Vuetify);

describe("SearchResults", () => {
  const vuetify = new Vuetify();
  const mountFunction = options => {
    return shallowMount(SearchResults, {
      vuetify,
      ...options
    });
  };

  test("Gets filters from route", () => {
    const wrapper = mountFunction({
      mocks: {
        $route: {
          query: {
            filter1: "value",
            filter2: "filter 2 value"
          }
        }
      }
    });

    expect(wrapper.vm.setValue).toBe(
      `filter1:"value" filter2:"filter 2 value"`
    );
  });

  test("Gets project path from parents", () => {
    const wrapper = mountFunction({
      mocks: {
        $route: {
          query: {}
        }
      }
    });
    const project = {
      name: "sub-subproject",
      ecosystem: { name: "ecosystem" },
      parentProject: {
        name: "subproject",
        parentProject: {
          name: "project",
          parentProject: null
        }
      }
    };
    const path = wrapper.vm.getPath(project);

    expect(path).toBe("ecosystem / project / subproject / sub-subproject");
  });
});
