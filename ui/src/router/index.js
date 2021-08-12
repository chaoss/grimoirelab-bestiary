import Router from "vue-router";
import store from "../store";

const router = new Router({
  mode: "history",
  routes: [
    {
      name: "private",
      path: "/",
      component: () => import("../views/Sidebar"),
      meta: { requiresAuth: true },
      children: [
        {
          name: "ecosystem-new",
          path: "/ecosystem/new",
          component: () => import("../views/NewEcosystem"),
          meta: { requiresAuth: true }
        },
        {
          name: "ecosystem",
          path: "/ecosystem/:id",
          component: () => import("../views/Ecosystem"),
          meta: { requiresAuth: true }
        },
        {
          name: "ecosystem-edit",
          path: "/ecosystem/:id/edit",
          component: () => import("../views/EditEcosystem"),
          meta: { requiresAuth: true }
        },
        {
          name: "project-new",
          path: "/ecosystem/:id/new",
          component: () => import("../views/NewProject"),
          meta: { requiresAuth: true },
          props: true
        },
        {
          name: "project",
          path: "/ecosystem/:ecosystemId/project/:name",
          component: () => import("../views/Project"),
          meta: { requiresAuth: true },
          props: true
        },
        {
          name: "project-edit",
          path: "/ecosystem/:id/project/:name/edit",
          component: () => import("../views/EditProject"),
          meta: { requiresAuth: true },
          props: true
        },
        {
          name: "search",
          path: "/search",
          component: () => import("../views/SearchResults"),
          meta: { requiresAuth: true }
        },
        {
          name: "datasource",
          path: "/project/:id/datasource/:uri",
          component: () => import("../views/Datasource"),
          meta: { requiresAuth: true }
        }
      ]
    },
    {
      path: "/login",
      name: "Login",
      component: () => import("../views/Login")
    }
  ]
});

router.beforeEach((to, from, next) => {
  const isAuthenticated = store.getters.isAuthenticated;
  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!isAuthenticated) {
      next({ path: "/login" });
    } else {
      next();
    }
  } else {
    next();
  }
});

export default router;
