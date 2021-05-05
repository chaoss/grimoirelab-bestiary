import { mount, createLocalVue } from "@vue/test-utils";
import Vue from "vue";
import Vuetify from "vuetify";
import VueRouter from 'vue-router';
import EcosystemTree from "@/components/EcosystemTree";

Vue.use(Vuetify)
const localVue = createLocalVue();
localVue.use(Vuetify);
localVue.use(VueRouter)

describe("EcosystemTree", () => {
  const router = new VueRouter();
  const vuetify = new Vuetify();
  const mountFunction = options => {
    return mount(EcosystemTree, {
      localVue,
      vuetify,
      router,
      ...options
    });
  };

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
          name: "root"
        },
        subprojects: [{
          id: 2,
          name: "grandchild",
          title: "grandchild",
          parentProject: {
            name: "child"
          },
          ecosystem: {
            name: "root"
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
          name: "root"
        }
      }
    ]
  };

  test("Filters subprojects at projectSet level", () => {
    const wrapper = mountFunction({
      propsData: {
        ecosystem: threeLevels
      }
    });

    const children = wrapper.vm.items[0].subprojects;
    expect(children.length).toBe(1);
  });

  test("Generates links", () => {
    const wrapper = mountFunction({
      propsData: {
        ecosystem: threeLevels
      }
    });

    const ecosystemLink = wrapper.vm.getLink(wrapper.vm.ecosystem);
    expect(ecosystemLink).toBe("/ecosystem/root");

    const projectLink = wrapper.vm.getLink(
      wrapper.vm.ecosystem.subprojects[0]
    );
    expect(projectLink).toBe("/ecosystem/root/project/child");

    const subprojectLink = wrapper.vm.getLink(
      wrapper.vm.ecosystem.subprojects[0].subprojects[0]
    );
    expect(subprojectLink).toBe("/ecosystem/root/project/grandchild");
  })
});
