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
    const res = await fetch("/api/manifests");
    this.manifests = await res.json();
  },
};
</script>
