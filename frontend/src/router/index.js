import { createRouter, createWebHistory } from "vue-router";
import DashboardLayout from "../layouts/DashboardLayout.vue";

// Import all your views
import Login from "../pages/Login.vue";
import DashboardOverview from "../pages/DashboardOverview.vue";
import Upload from "../pages/Upload.vue";
import Manifests from "../pages/Manifests.vue";
import ManifestDetail from "../pages/ManifestDetail.vue";

const routes = [
  {
    path: "/",
    name: "Login",
    component: Login,
  },
  {
    path: "/dashboard",
    component: DashboardLayout,
    meta: { requiresAuth: true }, // Semua rute anak akan memerlukan login
    children: [
      {
        path: "overview",
        name: "Dashboard",
        component: DashboardOverview,
        // --- Tambahkan Meta Roles ---
        meta: { roles: ['agen', 'pelabuhan'] }
      },
      {
        path: "upload",
        name: "Upload Manifest",
        component: Upload,
        // --- Tambahkan Meta Roles ---
        meta: { roles: ['agen'] } 
      },
      {
        path: "manifests",
        name: "Daftar Manifest",
        component: Manifests,
        // --- Tambahkan Meta Roles ---
        meta: { roles: ['agen', 'imigrasi', 'pelabuhan'] }
      },
      {
        path: "manifests/:id",
        name: "Detail Manifest",
        component: ManifestDetail,
        props: true,
        // --- Tambahkan Meta Roles ---
        meta: { roles: ['agen', 'imigrasi'] }
      },
      // Redirect default dashboard ke overview
      {
        path: '',
        redirect: '/dashboard/overview',
      }
    ],
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// --- PERBARUI NAVIGATION GUARD ---
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem("token");
  const userRole = localStorage.getItem("role");

  if (to.meta.requiresAuth) {
    if (!token) {
      // 1. Jika rute butuh login tapi tidak ada token, redirect ke Login
      next("/"); 
    } else {
      // 2. Jika ada token, cek role
      const requiredRoles = to.meta.roles;
      
      if (requiredRoles && requiredRoles.length > 0) {
        if (requiredRoles.includes(userRole)) {
          // 3. Jika role sesuai, izinkan akses
          next();
        } else {
          // 4. Jika role tidak sesuai, redirect ke halaman utama (atau tampilkan error)
          alert("Anda tidak memiliki hak akses untuk halaman ini.");
          // Redirect ke halaman dashboard utama yang pasti bisa diakses role tersebut
          // (Ini asumsi, idealnya redirect ke halaman 'default' berdasarkan role)
          next(from.path); // Tetap di halaman sebelumnya
        }
      } else {
        // 5. Rute butuh login, tapi tidak ada role spesifik (cth: halaman profil)
        next();
      }
    }
  } else {
    // 6. Rute tidak butuh login (seperti halaman Login itu sendiri)
    next();
  }
});

export default router;