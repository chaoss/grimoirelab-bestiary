import { mount } from "@vue/test-utils";
import Vue from "vue";
import Vuetify from "vuetify";
import ProjectSelector from "@/components/ProjectSelector";

Vue.use(Vuetify);

describe("ProjectSelector", () => {
  const vuetify = new Vuetify();

  test("Adds 'path' property to a list of projects", async () => {
    const wrapper = mount(ProjectSelector, {
      vuetify,
      propsData: {
        getProjects: () => {
          return [
            {
              id: 1,
              name: "project-1",
              title: "Project 1",
              parentProject: null
            },
            {
              id: 2,
              name: "project-2",
              title: "Project 2",
              parentProject: {
                id: 1,
                name: "project-1",
                title: "Project 1",
                parentProject: null
              }
            },
            {
              id: 3,
              name: "project-3",
              title: "Project 3",
              parentProject: {
                id: 2,
                name: "project-2",
                title: "Project 2",
                parentProject: {
                  id: 1,
                  name: "project-1",
                  title: "Project 1",
                  parentProject: null
                }
              }
            }
          ];
        }
      }
    });
    const el = document.createElement("div");
    el.setAttribute("data-app", true);
    document.body.appendChild(el);

    const button = wrapper.find("button");
    await button.trigger("click");

    const project1 = wrapper.vm.projects[0];
    expect(project1.path).toBe("project-1");

    const project2 = wrapper.vm.projects[1];
    expect(project2.path).toBe("project-1 / project-2");

    const project3 = wrapper.vm.projects[2];
    expect(project3.path).toBe("project-1 / project-2 / project-3");
  });
});
