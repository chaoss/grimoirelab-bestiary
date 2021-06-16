import { shallowMount } from "@vue/test-utils";
import Vue from "vue";
import Vuetify from "vuetify";
import EditProject from "@/views/EditProject";

Vue.use(Vuetify);

describe("EditProject", () => {
  const vuetify = new Vuetify();
  const mountFunction = options => {
    return shallowMount(EditProject, {
      vuetify,
      ...options
    });
  };
  const parentProjects = [
    {
      id: 1,
      name: "root1",
      subprojects: [
        {
          id: 3,
          name: "child",
          parentProject: {
            id: 1,
            name: "root1"
          }
        }
      ]
    },
    {
      id: 2,
      name: "root2"
    },
    {
      id: 3,
      name: "child",
      parentProject: {
        id: 1,
        name: "root1"
      }
    }
  ];

  test("Filters out the project's descendants", async () => {
    const wrapper = mountFunction({
      mocks: {
        $route: {
          params: {
            id: 1,
            name: "root1"
          }
        }
      },
      data() {
        return {
          project: {
            id: 1,
            name: "root1",
            subprojects: [
              {
                id: 3,
                name: "child",
                parentProject: {
                  id: 1,
                  name: "root1"
                }
              }
            ],
            ecosystem: { name: "ecosystem" }
          }
        };
      }
    });

    const validParents = wrapper.vm.validateParentProjects(parentProjects);
    expect(validParents.length).toBe(1);
    expect(validParents[0].name).toBe("root2");
  });
});
