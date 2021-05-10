import { shallowMount } from "@vue/test-utils";
import Vue from "vue";
import Vuetify from "vuetify";
import * as Queries from "@/apollo/queries";
import ProjectForm from "@/components/ProjectForm";

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
        addProject: () => {}
      }
    });
    await wrapper.vm.loadParentProjects();

    expect(querySpy).toHaveBeenCalledWith(1);
    expect(wrapper.element).toMatchSnapshot();
  });
});
