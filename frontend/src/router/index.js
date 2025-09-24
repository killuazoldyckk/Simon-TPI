import { createRouter, createWebHistory } from "vue-router";
import DashboardLayout from "../layouts/DashboardLayout.vue";

// Import all your views
import Login from "../pages/Login.vue";
import DashboardOverview from "../pages/DashboardOverview.vue";
import Upload from "../pages/Upload.vue";
import Manifests from "../pages/Manifests.vue";
import ManifestDetail from "../pages/ManifestDetail.vue";
import Survey from "../pages/Survey.vue";
import FeedbackList from "../pages/FeedbackList.vue";
import AddUser from "../pages/AddUser.vue";
import UserList from "../pages/UserList.vue";

const routes = [
  {
    path: "/",
    name: "Login",
    component: Login,
  },
  {
    path: "/dashboard",
    component: DashboardLayout, // The parent layout
    meta: { requiresAuth: true },
    children: [
      // Child routes will be rendered inside DashboardLayout's <router-view>
      {
        path: "overview",
        name: "Dashboard",
        component: DashboardOverview,
      },
      {
        path: "upload",
        name: "Upload Manifest",
        component: Upload,
      },
      {
        path: "manifests",
        name: "Daftar Manifest",
        component: Manifests,
      },
      {
        path: "manifests/:id",
        name: "Detail Manifest",
        component: ManifestDetail,
        props: true,
      },
      {
        path: "survey",
        name: "Survey Kepuasan",
        component: Survey,
      },
      {
        path: "feedback",
        name: "Lihat Feedback",
        component: FeedbackList,
        meta: { requiresAdmin: true } 
      },
      {
        path: "add-user",
        name: "Tambah Pengguna",
        component: AddUser,
        meta: { requiresAdmin: true }
      },
      {
        path: "users",
        name: "Daftar Pengguna",
        component: UserList,
        meta: { requiresAdmin: true }
      },
    ],
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Navigation guard (from your src/router.js file)
router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth && !localStorage.getItem("token")) {
    next("/"); // Redirect to login if not authenticated
  } else {
    next();
  }
});

export default router;