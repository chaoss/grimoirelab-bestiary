import { mount } from "@vue/test-utils";
import Vue from "vue";
import Vuetify from "vuetify";
import Breadcrumbs from "@/components/Breadcrumbs";
import * as Utils from "@/utils";

Vue.use(Vuetify);

describe("Breadcrumbs", () => {
  const vuetify = new Vuetify();
  const mountFunction = options => {
    return mount(Breadcrumbs, {
      stubs: ["router-link"],
      vuetify,
      ...options
    });
  };
  const project = {
    name: "grandchild",
    ecosystem: {
      id: 1,
      name: "ecosystem"
    },
    parentProject: {
      name: "child",
      parentProject: {
        name: "parent"
      }
    }
  };

  test("Gets simple breadcrumbs", () => {
    const items = Utils.getViewBreadCrumbs("View name");
    const wrapper = mountFunction({ propsData: { items: items } });
    const breadcrumbs = wrapper.find(".v-breadcrumbs__item");

    expect(breadcrumbs.text()).toBe("View name");
  });

  test("Gets breadcrumbs from project", () => {
    const items = Utils.getProjectBreadcrumbs(project);
    const wrapper = mountFunction({ propsData: { items: items } });
    const breadcrumbs = wrapper.findAll(".v-breadcrumbs__item");

    expect(wrapper.vm.items.length).toBe(4);

    const ecosystem = breadcrumbs.at(0);
    expect(ecosystem.text()).toBe("ecosystem");

    const parent = breadcrumbs.at(1);
    expect(parent.text()).toBe("parent");

    const child = breadcrumbs.at(2);
    expect(child.text()).toBe("child");

    const grandchild = breadcrumbs.at(3);
    expect(grandchild.text()).toBe("grandchild");
  });
});
