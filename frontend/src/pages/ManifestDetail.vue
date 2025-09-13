<template>
  <div class="p-4">
    <h1>Detail Manifest</h1>
    <div v-if="manifest">
      <p><b>Kapal:</b> {{ manifest.ship_name }}</p>
      <p><b>Tiba:</b> {{ manifest.arrival_date }}</p>
      <p><b>Asal:</b> {{ manifest.origin }}</p>
      <p><b>Tujuan:</b> {{ manifest.destination }}</p>
      <h2>Penumpang</h2>
      <ul>
        <li v-for="p in manifest.passengers" :key="p.id">
          {{ p.name }} - {{ p.passport_no }} - {{ p.nationality }}
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return { manifest: null };
  },
  async mounted() {
    const token = localStorage.getItem("token");
    if (!token) {
      alert("Sesi tidak valid, silahkan login kembali.");
      this.$router.push('/');
      return;
    }

    const res = await fetch(`/api/manifests/${this.$route.params.id}`, {
      headers: {
        "Authorization": "Bearer " + token
      }
    });

    if (!res.ok) {
      alert("Gagal mengambil data detail. Sesi mungkin berakhir.");
      this.$router.push('/manifests'); // Go back to the list page
      return;
    }

    this.manifest = await res.json();
  },
};
</script>
