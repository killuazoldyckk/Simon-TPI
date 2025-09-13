<template>
  <div class="p-4">
    <h1>Daftar Kapal</h1>
    <ul>
      <li v-for="m in manifests" :key="m.id">
        <router-link :to="'/manifests/' + m.id">
          {{ m.ship_name }} - {{ m.arrival_date }}
        </router-link>
      </li>
    </ul>
  </div>
</template>

<script>
export default {
  data() {
    return { manifests: [] };
  },
  async mounted() {
    const token = localStorage.getItem("token");
    if (!token) {
      alert("Sesi tidak valid, silahkan login kembali.");
      this.$router.push('/'); // Redirect to login if no token
      return;
    }

    const res = await fetch("/api/manifests", {
      headers: {
        "Authorization": "Bearer " + token
      }
    });

    if (!res.ok) {
      // Handle auth error (e.g., expired token)
      alert("Gagal mengambil data manifests. Sesi mungkin berakhir.");
      this.$router.push('/');
      return;
    }

    this.manifests = await res.json();
  },
};
</script>
