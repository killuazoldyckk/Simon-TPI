<template>
  <div>
    <div v-if="isLoading" class="text-center text-gray-500 py-10">
      Memuat data analitik...
    </div>

    <div v-else-if="error" class="bg-red-100 border-l-4 border-red-500 text-red-700 p-4">
      <p class="font-bold">Error</p>
      <p>{{ error }}</p>
    </div>

    <div v-else-if="chartData" class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      
      <div class="bg-white p-6 rounded-lg shadow-md">
        <h3 class="text-lg font-semibold text-gray-700 mb-4">Perbandingan Volume Penumpang per Rute</h3>
        <div class="h-64">
          <Bar v-if="chartData.routeComparison.datasets.length" :data="chartData.routeComparison" :options="chartOptions" />
          <div v-else class="text-center text-gray-500 py-8">Tidak ada data rute.</div>
        </div>
      </div>

      <div class="bg-white p-6 rounded-lg shadow-md">
        <h3 class="text-lg font-semibold text-gray-700 mb-4">Distribusi Usia & Gender</h3>
        <div class="h-64">
          <Bar v-if="chartData.ageGender.datasets.length" :data="chartData.ageGender" :options="chartOptions" />
          <div v-else class="text-center text-gray-500 py-8">Tidak ada data demografi.</div>
        </div>    
      </div>

      <div class="bg-white p-6 rounded-lg shadow-md lg:col-span-2">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-semibold text-gray-700">Tren Lalu Lintas Harian (30 Hari Terakhir)</h3>
        </div>
        <div class="h-64">
          <Line v-if="chartData.dailyTraffic.datasets.length" :data="chartData.dailyTraffic" :options="chartOptions" />
          <div v-else class="text-center text-gray-500 py-8">Tidak ada data lalu lintas harian.</div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { Bar, Line } from 'vue-chartjs';
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale, PointElement, LineElement } from 'chart.js';

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale, PointElement, LineElement);

const analyticsData = ref(null);
const isLoading = ref(true);
const error = ref(null);
const router = useRouter();

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'top',
    },
  },
};

const chartData = computed(() => {
  if (!analyticsData.value) {
    return null;
  }
  
  // Data untuk Perbandingan Rute
  const routeComparison = {
    labels: analyticsData.value.route_comparison.map(d => d.route),
    datasets: [{
      label: 'Total Penumpang',
      backgroundColor: '#3B82F6',
      data: analyticsData.value.route_comparison.map(d => d.passenger_count),
    }]
  };

  // Data untuk Distribusi Usia & Gender
  const ageGender = {
    labels: analyticsData.value.age_gender_distribution.map(d => d.age_group),
    datasets: [
      {
        label: 'Laki-laki',
        backgroundColor: '#2563EB',
        data: analyticsData.value.age_gender_distribution.map(d => d.male_count),
      },
      {
        label: 'Perempuan',
        backgroundColor: '#EC4899',
        data: analyticsData.value.age_gender_distribution.map(d => d.female_count),
      }
    ]
  };

  // Data untuk Tren Lalu Lintas Harian
  const dailyTraffic = {
    labels: analyticsData.value.daily_traffic.map(d => new Date(d.date).toLocaleDateString('id-ID', { day: 'numeric', month: 'short' })),
    datasets: [
      {
        label: 'Jumlah Penumpang',
        borderColor: '#10B981',
        backgroundColor: '#10B981',
        data: analyticsData.value.daily_traffic.map(d => d.passenger_count),
        tension: 0.1
      }
    ]
  };

  return { routeComparison, ageGender, dailyTraffic };
});

onMounted(async () => {
  const token = localStorage.getItem("token");
  if (!token) {
    router.push('/');
    return;
  }
  
  try {
    const res = await fetch("/api/analytics/enhanced_dashboard", {
      headers: { "Authorization": `Bearer ${token}` }
    });
    if (!res.ok) throw new Error("Gagal mengambil data analitik.");
    analyticsData.value = await res.json();
  } catch (err) {
    error.value = err.message;
  } finally {
    isLoading.value = false;
  }
});
</script>