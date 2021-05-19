import { mount, createLocalVue } from "@vue/test-utils";
import Vue from "vue";
import Vuetify from "vuetify";
import VueRouter from 'vue-router';
import EcosystemTree from "@/components/EcosystemTree";
import router from "@/router";

Vue.use(Vuetify)
const localVue = createLocalVue();
localVue.use(Vuetify);
localVue.use(VueRouter)

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
        subprojects: [{
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
        }]
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
        deleteProject: () => {}
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

    const projectLink = wrapper.vm.getLink(
      wrapper.vm.ecosystem.subprojects[0]
    );
    expect(projectLink).toBe("/ecosystem/0/project/child");

    const subprojectLink = wrapper.vm.getLink(
      wrapper.vm.ecosystem.subprojects[0].subprojects[0]
    );
    expect(subprojectLink).toBe("/ecosystem/0/project/grandchild");
  })
});
