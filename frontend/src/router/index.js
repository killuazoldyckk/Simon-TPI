import { createRouter, createWebHistory } from "vue-router";
import DashboardLayout from "../layouts/DashboardLayout.vue";

const routes = [
  {
    path: "/",
    name: "Login",
    component: () => import("../pages/Login.vue"),  
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
        component: () => import("../pages/DashboardOverview.vue"),
      },
      {
        path: "upload",
        name: "Upload Manifest",
        component: () => import("../pages/Upload.vue"),
      },
      {
        path: "manifests",
        name: "Daftar Manifest",
        component: () => import("../pages/Manifests.vue"),
      },
      {
        path: "manifests/:id",
        name: "Detail Manifest",
        component: () => import("../pages/ManifestDetail.vue"),
        props: true,
      },
      {
        path: "survey",
        name: "Survey Kepuasan",
        component: () => import("../pages/Survey.vue"),
      },
      {
        path: "feedback",
        name: "Lihat Feedback",
        component: () => import("../pages/FeedbackList.vue"),
        meta: { requiresAdmin: true } 
      },
      {
        path: "users",
        name: "Daftar Pengguna",
        component: () => import("../pages/UserList.vue"),
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
  const loggedIn = localStorage.getItem('token');

  // Jika rute memerlukan login dan pengguna belum login
  if (to.matched.some(record => record.meta.requiresAuth) && !loggedIn) {
    // Arahkan ke halaman login
    next('/');
  } else {
    // Lanjutkan navigasi
    next();
  }
});



export default router;