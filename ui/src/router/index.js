import Router from "vue-router";

const router = new Router({
  mode: "history",
  routes: [
    {
      name: "project-new",
      path: "/ecosystem/:id/new",
      component: () => import("../views/NewProject"),
      props: true
    }
  ]
});

export default router;
