import { shallowMount } from "@vue/test-utils";
import Vue from "vue";
import Vuetify from "vuetify";
import * as Mutations from "@/apollo/mutations";
import ProjectForm from "@/components/ProjectForm";

Vue.use(Vuetify);

describe("ProjectsForm mutations", () => {
  const mountFunction = options => {
    return shallowMount(ProjectForm, {
      Vue,
      Vuetify,
      propsData: {
        ecosystemId: 1,
        getProjects: () => {},
        saveFunction: () => {}
      },
      ...options
    });
  };

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

  const updateProjectResponse = {
    data: {
      updateProject: {
        project: {
          id: "39",
          name: "test",
          __typename: "ProjectType"
        },
        __typename: "UpdateProject"
      }
    }
  };

  test("Mock mutation for addProject", async () => {
    const mutate = jest.fn(() => Promise.resolve(addProjectResponse));
    const wrapper = mountFunction({
      mocks: {
        $apollo: {
          mutate
        }
      },
      data() {
        return {
          form: {
            name: "New Project",
            title: "new-project"
          }
        };
      }
    });
    await wrapper.setProps({ saveFunction: mutate });
    await Mutations.addProject(wrapper.vm.$apollo, {
      name: wrapper.vm.form.name,
      title: wrapper.vm.form.title,
      ecosystemId: wrapper.vm.ecosystemId
    });

    expect(mutate).toBeCalled();
    expect(wrapper.element).toMatchSnapshot();
  });

  test("Mock mutation for updateProject", async () => {
    const mutate = jest.fn(() => Promise.resolve(updateProjectResponse));
    const wrapper = mountFunction({
      mocks: {
        $apollo: {
          mutate
        },
        $router: {
          push: () => {}
        }
      },
      data() {
        return {
          form: {
            name: "test",
            title: "Test Title",
            parentId: 2
          }
        };
      }
    });
    await wrapper.setProps({ saveFunction: mutate });

    //Mock Vuetify form validation
    wrapper.vm.$refs.form.validate = () => {
      return true;
    };

    await wrapper.vm.save();

    expect(mutate).toBeCalledWith({
      ecosystemId: 1,
      name: "test",
      parentId: 2,
      title: "Test Title"
    });
    expect(wrapper.element).toMatchSnapshot();
  });
});
