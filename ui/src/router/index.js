import Router from "vue-router";

const router = new Router({
  mode: "history",
  routes: [
    {
      name: "ecosystem",
      path: "/ecosystem/:id",
      component: () => import("../views/Ecosystem")
    },
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
      name: "project-edit",
      path: "/ecosystem/:id/project/:name/edit",
      component: () => import("../views/EditProject"),
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
