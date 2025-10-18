<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { apiFetch } from '../api.js';
import { Line, Bar } from 'vue-chartjs';
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale, PointElement, LineElement } from 'chart.js';

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale, PointElement, LineElement);

// --- State Management ---
const dashboardData = ref(null);
const recentManifests = ref([]);
const isLoading = ref(true);
const error = ref(null);
const router = useRouter();

// --- Lifecycle Hook ---
onMounted(async () => {
  try {
    const [dashboardResponse, recentResponse] = await Promise.all([
      apiFetch('/api/dashboard/combined'), // Panggil endpoint gabungan yang baru
      apiFetch('/api/manifests/recent')
    ]);

    if (!dashboardResponse.ok) throw new Error('Gagal memuat data dasbor.');
    dashboardData.value = await dashboardResponse.json();

    if (!recentResponse.ok) throw new Error('Gagal memuat manifest terbaru.');
    recentManifests.value = await recentResponse.json();

  } catch (err) {
    error.value = err.message;
    console.error(err);
  } finally {
    isLoading.value = false;
  }
});

// --- Computed Properties untuk Chart ---
const operationalChartData = computed(() => {
  if (!dashboardData.value?.operational_stats?.passenger_trend) return null;
  const trend = dashboardData.value.operational_stats.passenger_trend;
  return {
    labels: trend.map(d => new Date(d.date).toLocaleDateString('id-ID', { weekday: 'short' })),
    datasets: [
      { label: 'Kedatangan', data: trend.map(d => d.arrivals), backgroundColor: '#3b82f6' },
      { label: 'Keberangkatan', data: trend.map(d => d.departures), backgroundColor: '#10b981' },
    ],
  };
});

const analyticalChartData = computed(() => {
  if (!dashboardData.value?.analytical_stats) return null;
  const analytical = dashboardData.value.analytical_stats;
  return {
    routeComparison: {
      labels: analytical.route_comparison.map(r => r.route),
      datasets: [{ label: 'Volume Penumpang', data: analytical.route_comparison.map(r => r.passenger_count), backgroundColor: '#8b5cf6' }],
    },
    ageGender: {
      labels: analytical.age_gender_distribution.map(ag => ag.age_group),
      datasets: [
        { label: 'Laki-laki', data: analytical.age_gender_distribution.map(ag => ag.male_count), backgroundColor: '#3b82f6' },
        { label: 'Perempuan', data: analytical.age_gender_distribution.map(ag => ag.female_count), backgroundColor: '#ec4899' },
      ],
    },
  };
});


const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { position: 'top' } },
  scales: { x: { stacked: true }, y: { stacked: true } }
};

// --- Helper Functions ---
const goToDetail = (id) => router.push(`/dashboard/manifests/${id}`);
const formatDate = (dateString) => dateString ? new Date(dateString).toLocaleDateString('id-ID', { day: '2-digit', month: 'long' }) : 'N/A';
</script>

<template>
  <div class="p-6 bg-gray-50 min-h-screen">
    <div v-if="isLoading" class="text-center text-gray-500 py-10">Memuat data...</div>
    <div v-else-if="error" class="bg-red-100 text-red-700 p-4 rounded-lg">{{ error }}</div>

    <div v-else-if="dashboardData">
      <h2 class="text-2xl font-semibold text-gray-700 mb-4 border-b pb-2">Status Operasional Hari Ini</h2>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        <div class="bg-white p-6 rounded-lg shadow-md text-center">
          <h3 class="text-lg font-semibold text-gray-500">Kedatangan Hari Ini</h3>
          <p class="text-4xl font-bold text-blue-600 mt-2">{{ dashboardData.operational_stats.arrivals_today }} Kapal</p>
        </div>
        <div class="bg-white p-6 rounded-lg shadow-md text-center">
          <h3 class="text-lg font-semibold text-gray-500">Keberangkatan Hari Ini</h3>
          <p class="text-4xl font-bold text-green-600 mt-2">{{ dashboardData.operational_stats.departures_today }} Kapal</p>
        </div>
        <div class="bg-white p-6 rounded-lg shadow-md text-center">
          <h3 class="text-lg font-semibold text-gray-500">Total Penumpang Hari Ini</h3>
          <p class="text-4xl font-bold text-gray-800 mt-2">{{ dashboardData.operational_stats.total_passengers_today }} Orang</p>
        </div>
      </div>
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <div class="lg:col-span-2 grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="bg-white p-6 rounded-lg shadow-md">
                <h3 class="text-lg font-semibold text-gray-700 mb-3">🚢 Kedatangan Berikutnya</h3>
                <p class="text-2xl font-bold text-blue-700 truncate">{{ dashboardData.operational_stats.next_arrival.ship_name }}</p>
                <p class="text-md text-gray-600">Dari: {{ dashboardData.operational_stats.next_arrival.port }}</p>
                <p class="text-md font-medium text-gray-800 mt-2">{{ formatDate(dashboardData.operational_stats.next_arrival.time) }}</p>
            </div>
            <div class="bg-white p-6 rounded-lg shadow-md">
                <h3 class="text-lg font-semibold text-gray-700 mb-3">➡️ Keberangkatan Berikutnya</h3>
                <p class="text-2xl font-bold text-green-700 truncate">{{ dashboardData.operational_stats.next_departure.ship_name }}</p>
                <p class="text-md text-gray-600">Tujuan: {{ dashboardData.operational_stats.next_departure.port }}</p>
                <p class="text-md font-medium text-gray-800 mt-2">{{ formatDate(dashboardData.operational_stats.next_departure.time) }}</p>
            </div>
        </div>
        <div class="bg-white p-6 rounded-lg shadow-md">
            <h3 class="text-lg font-semibold text-gray-700 mb-4">Aktivitas Unggah Terbaru</h3>
            <ul v-if="recentManifests.length" class="space-y-3">
                <li v-for="m in recentManifests" :key="m.id" @click="goToDetail(m.id)" class="cursor-pointer hover:bg-gray-100 p-2 rounded-md">
                    <p class="font-bold text-blue-600 truncate">{{ m.ship_name }}</p>
                    <p class="text-xs text-gray-500">{{ m.origin }} → {{ m.destination }}</p>
                </li>
            </ul>
        </div>
      </div>

      <h2 class="text-2xl font-semibold text-gray-700 mb-4 mt-10 border-b pb-2">Analisis & Tren</h2>
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div class="bg-white p-6 rounded-lg shadow-md">
            <h3 class="text-lg font-semibold text-gray-700 mb-4">Tren Penumpang (7 Hari Terakhir)</h3>
            <div class="h-64"><Bar v-if="operationalChartData" :data="operationalChartData" :options="chartOptions" /></div>
        </div>
        <div class="bg-white p-6 rounded-lg shadow-md">
            <h3 class="text-lg font-semibold text-gray-700 mb-4">Perbandingan Volume Penumpang per Rute</h3>
            <div class="h-64"><Bar v-if="analyticalChartData" :data="analyticalChartData.routeComparison" :options="{ ...chartOptions, scales: {} }" /></div>
        </div>
        <div class="bg-white p-6 rounded-lg shadow-md lg:col-span-2">
            <h3 class="text-lg font-semibold text-gray-700 mb-4">Distribusi Usia & Gender Penumpang</h3>
            <div class="h-64"><Bar v-if="analyticalChartData" :data="analyticalChartData.ageGender" :options="chartOptions" /></div>
        </div>
      </div>
    </div>
  </div>
</template>