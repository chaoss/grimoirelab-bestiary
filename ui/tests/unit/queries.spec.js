import { shallowMount } from "@vue/test-utils";
import Vue from "vue";
import Vuetify from "vuetify";
import * as Queries from "@/apollo/queries";
import ProjectForm from "@/components/ProjectForm";
import Ecosystem from "@/views/Ecosystem";

Vue.use(Vuetify);

describe("ProjectsForm queries", () => {
  const getProjectsResponse = {
    data: {
      projects: {
        entities: [{ id: "2", title: "Test", __typename: "ProjectType" }]
      }
    }
  };

  test("Mock query for getProjects", async () => {
    const querySpy = spyOn(Queries, "getProjects");
    const query = jest.fn(() => Promise.resolve(getProjectsResponse));
    const wrapper = shallowMount(ProjectForm, {
      Vue,
      mocks: {
        $apollo: {
          query
        }
      },
      propsData: {
        ecosystemId: 1,
        getProjects: Queries.getProjects,
        saveFunction: () => {}
      }
    });
    await wrapper.vm.loadParentProjects();

    expect(querySpy).toHaveBeenCalledWith(1);
    expect(wrapper.element).toMatchSnapshot();
  });
});

describe("Ecosystem queries", () => {
  const response = {
    data: {
      ecosystems: {
        entities: [
          {
            name: "test",
            title: "Test",
            description: "Projects and repositories monitored",
            projectSet: [
              {
                id: "72",
                name: "test-project",
                title: "Test Project",
                ecosystem: {
                  id: 1,
                  name: "test"
                },
                parentProject: null,
                subprojects: []
              }
            ]
          }
        ]
      }
    }
  };

  test("Mock query for getEcosystemByID", async () => {
    const querySpy = spyOn(Queries, "getEcosystemByID");
    const query = jest.fn(() => Promise.resolve(response));
    const wrapper = shallowMount(Ecosystem, {
      Vue,
      mocks: {
        $apollo: {
          query
        },
        $route: {
          params: {
            id: 1
          }
        }
      }
    });
    await wrapper.vm.getEcosystemData();

    expect(querySpy).toBeCalled();
    expect(wrapper.element).toMatchSnapshot();
  });
});
