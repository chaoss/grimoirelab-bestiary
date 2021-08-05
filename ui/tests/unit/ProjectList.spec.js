import { mount, createLocalVue } from "@vue/test-utils";
import Vue from "vue";
import Vuetify from "vuetify";
import VueRouter from "vue-router";
import ProjectList from "@/components/ProjectList";
import router from "@/router";

Vue.use(Vuetify);
const localVue = createLocalVue();
localVue.use(Vuetify);
localVue.use(VueRouter);

describe("ProjectList", () => {
  const vuetify = new Vuetify();
  const mountFunction = options => {
    return mount(ProjectList, {
      localVue,
      vuetify,
      router,
      ...options
    });
  };

  const threeLevels = [
    {
      id: 1,
      name: "parent",
      title: "Parent",
      ecosystem: {
        id: 1
      },
      subprojects: [
        {
          id: 2,
          name: "child",
          title: "Child",
          ecosystem: {
            id: 1
          },
          subprojects: [
            {
              id: 3,
              name: "grandchild",
              title: "Grandchild",
              ecosystem: {
                id: 1
              },
              subprojects: []
            }
          ]
        }
      ]
    }
  ];

  test("Renders all projects and subprojects", async () => {
    const wrapper = mountFunction({
      propsData: {
        projects: threeLevels,
        ecosystemId: 1
      }
    });

    expect(wrapper.vm.list.length).toBe(3);
    await wrapper.vm.$nextTick();
    const listItems = wrapper.findAll(".v-list-item");
    expect(listItems.length).toBe(3);
  });

  test("Renders project links", async () => {
    const wrapper = mountFunction({
      propsData: {
        projects: threeLevels,
        ecosystemId: 1
      }
    });

    await wrapper.vm.$nextTick();
    const listItems = wrapper.findAll(".v-list-item");

    const parent = listItems.at(0);
    expect(parent.attributes().href).toContain("/ecosystem/1/project/parent");

    const child = listItems.at(1);
    expect(child.attributes().href).toContain("/ecosystem/1/project/child");

    const grandchild = listItems.at(2);
    expect(grandchild.attributes().href).toContain(
      "/ecosystem/1/project/grandchild"
    );
  });
});
