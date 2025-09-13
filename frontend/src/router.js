import { createRouter, createWebHistory } from "vue-router";
import Login from "./pages/Login.vue";
import Upload from "./pages/Upload.vue";
import Manifests from "./pages/Manifests.vue";
import ManifestDetail from "./pages/ManifestDetail.vue";

const routes = [
  { path: "/", component: Login },
  { path: "/upload", component: Upload, meta: { requiresAuth: true } },
  { path: "/manifests", component: Manifests, meta: { requiresAuth: true } },
  { path: "/manifests/:id", component: ManifestDetail, props: true, meta: { requiresAuth: true } },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth && !localStorage.getItem("token")) {
    next("/");
  } else {
    next();
  }
});

export default router;
