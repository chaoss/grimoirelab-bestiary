import { mount, createLocalVue } from "@vue/test-utils";
import Vue from "vue";
import Vuetify from "vuetify";
import VueRouter from "vue-router";
import EcosystemTree from "@/components/EcosystemTree";
import router from "@/router";

Vue.use(Vuetify);
const localVue = createLocalVue();
localVue.use(Vuetify);
localVue.use(VueRouter);

describe("EcosystemTree", () => {
  const threeLevels = {
    id: 0,
    name: "root",
    title: "root",
    projectSet: [
      {
        id: 1,
        name: "child",
        title: "child",
        parentProject: null,
        ecosystem: {
          name: "root",
          id: 0
        },
        subprojects: [
          {
            id: 2,
            name: "grandchild",
            title: "grandchild",
            parentProject: {
              name: "child"
            },
            ecosystem: {
              name: "root",
              id: 0
            }
          }
        ]
      },
      {
        id: 2,
        name: "grandchild",
        title: "grandchild",
        parentProject: {
          name: "child"
        },
        ecosystem: {
          name: "root",
          id: 0
        }
      }
    ]
  };
  const vuetify = new Vuetify();
  const mountFunction = options => {
    return mount(EcosystemTree, {
      localVue,
      vuetify,
      router,
      propsData: {
        ecosystem: threeLevels,
        deleteProject: () => {},
        moveProject: () => {},
        deleteEcosystem: () => {}
      },
      ...options
    });
  };

  test("Filters subprojects at projectSet level", async () => {
    const wrapper = mountFunction();

    const children = wrapper.vm.items[0].subprojects;
    expect(children.length).toBe(1);
  });

  test("Generates links", async () => {
    const wrapper = mountFunction();

    const ecosystemLink = wrapper.vm.getLink(wrapper.vm.ecosystem);
    expect(ecosystemLink).toBe("/ecosystem/0");

    const projectLink = wrapper.vm.getLink(wrapper.vm.ecosystem.subprojects[0]);
    expect(projectLink).toBe("/ecosystem/0/project/child");

    const subprojectLink = wrapper.vm.getLink(
      wrapper.vm.ecosystem.subprojects[0].subprojects[0]
    );
    expect(subprojectLink).toBe("/ecosystem/0/project/grandchild");
  });

  test("Allows moving projects in the same ecosystem", async () => {
    const wrapper = mountFunction({
      data() {
        return {
          dragged: {
            id: 1,
            name: "project1",
            ecosystem: {
              id: 0
            }
          }
        }
      }
    });
    const projectTo = {
      id: 2,
      name: "project2",
      ecosystem: {
        id: 0
      }
    };
    const isAllowed = wrapper.vm.allowDrag(projectTo);
    expect(isAllowed).toBe(true);
  });

  test("Does not allow moving projects in different ecosystems", async () => {
    const wrapper = mountFunction({
      data() {
        return {
          dragged: {
            id: 1,
            name: "project1",
            ecosystem: {
              id: 0
            }
          }
        }
      }
    });
    const projectTo = {
      id: 2,
      name: "project2",
      ecosystem: {
        id: 100
      }
    };
    const isAllowed = wrapper.vm.allowDrag(projectTo);
    expect(isAllowed).toBe(false);
  });

  test("Allows moving project to one with the same root", async () => {
    const wrapper = mountFunction({
      data() {
        return {
          dragged: {
            id: 1,
            name: "project1",
            parentProject: {
              name: "root"
            },
            ecosystem: {
              id: 0
            }
          }
        }
      }
    });
    const projectTo = {
      id: 2,
      name: "project2",
      parentProject: {
        name: "root"
      },
      ecosystem: {
        id: 0
      }
    };
    const isAllowed = wrapper.vm.allowDrag(projectTo);
    expect(isAllowed).toBe(true);
  });

  test("Does not allow moving project to a different root project", async () => {
    const wrapper = mountFunction({
      data() {
        return {
          dragged: {
            id: 1,
            name: "project1",
            parentProject: { name: "root1" },
            ecosystem: {
              id: 0
            }
          }
        }
      }
    });
    const projectTo = {
      id: 2,
      name: "project2",
      parentProject: { name: "root2" },
      ecosystem: {
        id: 0
      }
    };
    const isAllowed = wrapper.vm.allowDrag(projectTo);
    expect(isAllowed).toBe(false);
  });

  test("Does not allow moving project to its parent", async () => {
    const wrapper = mountFunction({
      data() {
        return {
          dragged: {
            id: 1,
            name: "child",
            parentProject: { name: "parent" },
            ecosystem: {
              id: 0
            }
          }
        }
      }
    });
    const projectTo = {
      id: 2,
      name: "parent",
      subprojects: [{ id: 1 }],
      ecosystem: {
        id: 0
      }
    };
    const isAllowed = wrapper.vm.allowDrag(projectTo);
    expect(isAllowed).toBe(false);
  });

  test("Does not allow moving project to a descendant", async () => {
    const wrapper = mountFunction({
      data() {
        return {
          dragged: {
            id: 1,
            name: "parent",
            subprojects: [{ id: 2 }],
            ecosystem: {
              id: 0
            }
          }
        }
      }
    });
    const projectTo = {
      id: 2,
      name: "child",
      parentProject: { id: 1 },
      ecosystem: {
        id: 0
      }
    };
    const isAllowed = wrapper.vm.allowDrag(projectTo);
    expect(isAllowed).toBe(false);
  });
});
