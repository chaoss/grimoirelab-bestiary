import { shallowMount } from "@vue/test-utils";
import Vue from "vue";
import Vuetify from "vuetify";
import * as Mutations from "@/apollo/mutations";
import ProjectForm from "@/components/ProjectForm";

Vue.use(Vuetify);

describe("ProjectsForm queries", () => {
  const addProjectResponse = {
    data: {
      addProject: {
        project: {
          id: "1",
          name: "new-project",
          __typename: "ProjectType"
        },
        __typename: "AddProject"
      }
    }
  };

  test("Mock query for getProjects", async () => {
    const mutate = jest.fn(() => Promise.resolve(addProjectResponse));
    const wrapper = shallowMount(ProjectForm, {
      Vue,
      mocks: {
        $apollo: {
          mutate
        }
      },
      propsData: {
        ecosystemId: 1,
        getProjects: () => {},
        addProject: mutate
      },
      data() {
        return {
          name: "New Project",
          title: "new-project"
        };
      }
    });
    await Mutations.addProject(wrapper.vm.$apollo, {
      name: wrapper.vm.name,
      title: wrapper.vm.title,
      ecosystemId: wrapper.vm.ecosystemId
    });

    expect(mutate).toBeCalled();
    expect(wrapper.element).toMatchSnapshot();
  });
});
