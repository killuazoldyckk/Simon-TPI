<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { apiFetch } from '../api.js';
import { Line, Bar } from 'vue-chartjs'; // Impor komponen chart
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale, PointElement, LineElement } from 'chart.js';

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale, PointElement, LineElement);

// --- State Management ---
const analyticsData = ref(null);
const recentManifests = ref([]); // State untuk manifest terbaru
const isLoading = ref(true);
const loadingManifests = ref(true); // State loading terpisah
const error = ref(null);
const router = useRouter();

// --- Lifecycle Hook ---
onMounted(async () => {
  // Menggunakan Promise.all untuk mengambil kedua data secara bersamaan
  try {
    const [analyticsResponse, recentManifestsResponse] = await Promise.all([
      apiFetch('/api/analytics/enhanced_dashboard'),
      apiFetch('/api/manifests/recent')
    ]);

    // Proses data analitik untuk chart
    if (!analyticsResponse.ok) throw new Error('Gagal mengambil data analitik.');
    analyticsData.value = await analyticsResponse.json();
    isLoading.value = false;

    // Proses data manifest terbaru
    if (!recentManifestsResponse.ok) throw new Error('Gagal memuat manifest terbaru.');
    recentManifests.value = await recentManifestsResponse.json();
    loadingManifests.value = false;

  } catch (err) {
    error.value = err.message;
    console.error(err);
    isLoading.value = false;
    loadingManifests.value = false;
  }
});

// --- Chart Data & Options ---
const chartData = computed(() => {
  if (!analyticsData.value) return null;
  return {
    dailyTraffic: {
      labels: analyticsData.value.daily_traffic.map(d => new Date(d.date).toLocaleDateString('id-ID', { day: 'numeric', month: 'short' })),
      datasets: [
        {
          label: 'Jumlah Penumpang',
          data: analyticsData.value.daily_traffic.map(d => d.passenger_count),
          borderColor: '#3b82f6',
          tension: 0.1,
          fill: false,
        },
      ],
    },
    routeComparison: {
      labels: analyticsData.value.route_comparison.map(r => r.route),
      datasets: [
        {
          label: 'Volume Penumpang',
          data: analyticsData.value.route_comparison.map(r => r.passenger_count),
          backgroundColor: '#10b981',
        },
      ],
    },
    ageGender: {
      labels: analyticsData.value.age_gender_distribution.map(ag => ag.age_group),
      datasets: [
        {
          label: 'Laki-laki',
          data: analyticsData.value.age_gender_distribution.map(ag => ag.male_count),
          backgroundColor: '#3b82f6',
        },
        {
          label: 'Perempuan',
          data: analyticsData.value.age_gender_distribution.map(ag => ag.female_count),
          backgroundColor: '#ef4444',
        },
      ],
    },
  };
});

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { position: 'top' } },
};

// --- Navigation Function ---
const goToDetail = (manifestId) => {
  router.push(`/dashboard/manifests/${manifestId}`);
};
</script>

<template>
  <div class="p-6 bg-gray-50 min-h-screen">
    <h1 class="text-3xl font-bold text-gray-800 mb-6">Analitik</h1>

    <div v-if="isLoading" class="text-center text-gray-500 py-10">
      Memuat data analitik...
    </div>
    <div v-else-if="error" class="bg-red-100 border-l-4 border-red-500 text-red-700 p-4">
      <p class="font-bold">Error</p>
      <p>{{ error }}</p>
    </div>

    <div v-if="chartData" class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
      <div class="bg-white p-6 rounded-lg shadow-md">
        <h3 class="text-lg font-semibold text-gray-700 mb-4">Perbandingan Volume Penumpang per Rute</h3>
        <div class="h-64">
          <Bar v-if="chartData.routeComparison.datasets[0].data.length" :data="chartData.routeComparison" :options="chartOptions" />
          <div v-else class="text-center text-gray-500 py-8">Tidak ada data rute.</div>
        </div>
      </div>
      <div class="bg-white p-6 rounded-lg shadow-md">
        <h3 class="text-lg font-semibold text-gray-700 mb-4">Distribusi Usia & Gender</h3>
        <div class="h-64">
          <Bar v-if="chartData.ageGender.datasets[0].data.length || chartData.ageGender.datasets[1].data.length" :data="chartData.ageGender" :options="chartOptions" />
          <div v-else class="text-center text-gray-500 py-8">Tidak ada data demografi.</div>
        </div>
      </div>
      <div class="bg-white p-6 rounded-lg shadow-md lg:col-span-2">
        <h3 class="text-lg font-semibold text-gray-700 mb-4">Tren Lalu Lintas Harian (30 Hari Terakhir)</h3>
        <div class="h-64">
          <Line v-if="chartData.dailyTraffic.datasets[0].data.length" :data="chartData.dailyTraffic" :options="chartOptions" />
          <div v-else class="text-center text-gray-500 py-8">Tidak ada data lalu lintas harian.</div>
        </div>
      </div>
    </div>

    <div>
      <h2 class="text-2xl font-semibold text-gray-700 mb-4">Manifest Terbaru</h2>
      <div v-if="loadingManifests" class="text-center text-gray-500">Memuat manifest...</div>
      <div v-else-if="recentManifests.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-6">
        <div
          v-for="manifest in recentManifests"
          :key="manifest.id"
          @click="goToDetail(manifest.id)"
          class="bg-white p-5 rounded-lg shadow-md hover:shadow-xl hover:-translate-y-1 transition-all duration-300 cursor-pointer"
        >
          <h3 class="text-lg font-bold text-blue-600 truncate" :title="manifest.ship_name">{{ manifest.ship_name }}</h3>
          <p class="text-sm text-gray-500 mt-2">
            Tiba: {{ new Date(manifest.arrival_date).toLocaleDateString('id-ID', { day: '2-digit', month: 'short', year: 'numeric' }) }}
          </p>
          <div class="mt-3 text-sm text-gray-700 border-t pt-3">
            <p><span class="font-semibold">Penumpang:</span> {{ manifest.passengers.length }}</p>
            <p><span class="font-semibold">Kru:</span> {{ manifest.crews.length }}</p>
          </div>
        </div>
      </div>
      <div v-else class="text-center text-gray-500 bg-white p-8 rounded-lg shadow-md">
        Belum ada data manifest yang diunggah.
      </div>
    </div>

  </div>
</template>