import Router from "vue-router";

const router = new Router({
  mode: "history",
  routes: [
    {
      name: "project-new",
      path: "/ecosystem/:id/new",
      component: () => import("../views/NewProject"),
      props: true
    },
    {
      name: "project",
      path: "/ecosystem/:ecosystemId/project/:name",
      component: () => import("../views/Project"),
      props: true
    },
    {
      name: "search",
      path: "/search",
      component: () => import("../views/SearchResults")
    }
  ]
});

export default router;
