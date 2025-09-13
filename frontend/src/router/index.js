import { createRouter, createWebHistory } from "vue-router";
import Login from "./pages/Login.vue";
import Upload from "./pages/Upload.vue";
import Manifests from "./pages/Manifests.vue";
import ManifestDetail from "./pages/ManifestDetail.vue";

const routes = [
  { path: "/", component: Login },
  { path: "/upload", component: Upload },
  { path: "/manifests", component: Manifests },
  { path: "/manifests/:id", component: ManifestDetail, props: true }
];

export default createRouter({
  history: createWebHistory(),
  routes,
});
