import { shallowMount } from "@vue/test-utils";
import Vue from "vue";
import Vuetify from "vuetify";
import * as Mutations from "@/apollo/mutations";
import ProjectForm from "@/components/ProjectForm";
import EcosystemForm from "@/components/EcosystemForm";
import EcosystemTree from "@/components/EcosystemTree";

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

describe("Ecosystem mutations", () => {
  const response = {
    data: {
      addEcosystem: {
        ecosystem: {
          id: "1"
        }
      }
    }
  };

  test("Mock mutation for addEcosystem", async () => {
    const mutate = jest.fn(() => Promise.resolve(response));
    const wrapper = shallowMount(EcosystemForm, {
       Vue,
       mocks: {
         $apollo: {
           mutate
         }
       },
       propsData: {
         saveFunction: mutate
       },
       data() {
        return {
          form: {
            name: "test",
            title: "Test",
            description: "Lorem ipsum"
          }
        };
       }
    });

    await Mutations.addEcosystem(wrapper.vm.$apollo, {
      name: wrapper.vm.form.name,
      title: wrapper.vm.form.title,
      description: wrapper.vm.form.description
    });

    expect(mutate).toBeCalled();
    expect(wrapper.element).toMatchSnapshot();
  });

  test("Mock mutation for updateEcosystem", async () => {
    const mutate = jest.fn(() => Promise.resolve(response));
    const wrapper = shallowMount(EcosystemForm, {
       Vue,
       mocks: {
         $apollo: {
           mutate
         }
       },
       propsData: {
         saveFunction: mutate,
         name: "test",
         title: "Test",
         description: "Lorem ipsum"
       }
    });

    await Mutations.updateEcosystem(wrapper.vm.$apollo, {
      name: wrapper.vm.form.name,
      title: wrapper.vm.form.title,
      description: wrapper.vm.form.description
    });

    expect(mutate).toBeCalled();
    expect(wrapper.element).toMatchSnapshot();
  });

  test("Mock mutation for deleteEcosystem", async () => {
    const mutate = jest.fn(() => Promise.resolve(response));
    const wrapper = shallowMount(EcosystemTree, {
       Vue,
       mocks: {
         $apollo: {
           mutate
         }
       },
       propsData: {
         ecosystem: {
           id: 1,
           title: "Test"
         },
         deleteEcosystem: mutate,
         deleteProject: () => {},
         moveProject: () => {}
       }
    });

    await Mutations.deleteEcosystem(
      wrapper.vm.$apollo,
      wrapper.vm.ecosystem.id
    );

    expect(mutate).toBeCalled();
    expect(wrapper.element).toMatchSnapshot();
  });
});
