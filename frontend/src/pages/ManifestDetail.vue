<template>
  <div class="min-h-screen bg-gray-100 p-8 printable-area">
    <div class="max-w-6xl mx-auto">
      
      <div class="mb-4 flex justify-between items-center no-print">
        <router-link
          to="/dashboard/manifests"
          class="inline-flex items-center text-sm font-medium text-blue-600 hover:text-blue-800"
        >
          <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path></svg>
          Kembali ke Daftar Manifest
        </router-link>

        <button @click="printPage" class="bg-blue-600 text-white px-4 py-2 rounded-lg shadow hover:bg-blue-700 transition-colors inline-flex items-center space-x-2">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z"></path></svg>
          <span>Cetak / Simpan PDF</span>
        </button>
      </div>

    
      <div v-if="!manifest" class="bg-white p-8 rounded-lg shadow text-center text-gray-500">
        Loading manifest details...
      </div>

      <div v-else id="manifest-content">
        <div class="print-header mb-6 text-center">
          <img src="../assets/logo_indomal.png" alt="Logo Agen" style="width: 150px; margin: 0 auto 1rem;">
        </div>

        <div class="bg-white rounded-lg shadow overflow-hidden mb-6">
          <div class="p-5 border-b border-gray-200">
            <h1 class="text-2xl font-bold text-gray-800">Detail Manifest: {{ manifest.ship_name }}</h1>
             <p class="text-gray-600">
              Bendera: {{ manifest.flag }} | Nahkoda: {{ manifest.skipper_name }}
            </p>
          </div>
           <div class="p-5 grid grid-cols-2 md:grid-cols-4 gap-6 bg-gray-50">
            <div>
              <div class="text-xs font-semibold text-gray-500 uppercase tracking-wider">Pelabuhan Asal</div>
              <div class="text-lg font-medium text-gray-800">{{ manifest.origin }}</div>
            </div>
             <div>
              <div class="text-xs font-semibold text-gray-500 uppercase tracking-wider">Tanggal Berangkat</div>
              <div class="text-lg font-medium text-gray-800">{{ manifest.departure_date }}</div>
            </div>
            <div>
              <div class="text-xs font-semibold text-gray-500 uppercase tracking-wider">Total Penumpang</div>
              <div class="text-lg font-medium text-gray-800">{{ manifest.passengers.length }} Orang</div>
            </div>
            <div>
              <div class="text-xs font-semibold text-gray-500 uppercase tracking-wider">Pelabuhan Tujuan</div>
              <div class="text-lg font-medium text-gray-800">{{ manifest.destination }}</div>
            </div>
            <div>
              <div class="text-xs font-semibold text-gray-500 uppercase tracking-wider">Tanggal Tiba</div>
              <div class="text-lg font-medium text-gray-800">{{ manifest.arrival_date }}</div>
            </div>
            <div>
              <div class="text-xs font-semibold text-gray-500 uppercase tracking-wider">Total Awak Kapal</div>
              <div class="text-lg font-medium text-gray-800">{{ manifest.crews.length }} Orang</div>
            </div>
            </div>
        </div>

        <div class="bg-white rounded-lg shadow overflow-hidden">
          <h2 class="text-xl font-semibold text-gray-800 p-5">Daftar Penumpang</h2>
          
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">No</th>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Nama</th>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Sex</th>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tgl. Lahir</th>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Negara</th>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">No. Paspor</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-if="manifest.passengers.length === 0">
                  <td colspan="6" class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 text-center">Data penumpang kosong.</td>
                </tr>
                <tr v-for="(p, index) in manifest.passengers" :key="p.id" class="hover:bg-gray-50">
                  <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{{ index + 1 }}</td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{{ p.name }}</td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ p.sex }}</td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ p.dob }}</td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ p.nationality }}</td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ p.passport_no }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow overflow-hidden mt-6">
          <h2 class="text-xl font-semibold text-gray-800 p-5">Daftar Awak Kapal (Crew)</h2>
          
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">No</th>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Nama</th>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tgl. Lahir</th>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">No. Buku Pelaut</th>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tgl. Berakhir Buku Pelaut</th>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Jabatan</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-if="!manifest.crews || manifest.crews.length === 0">
                  <td colspan="6" class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 text-center">Data awak kapal kosong.</td>
                </tr>
                <tr v-for="(c, index) in manifest.crews" :key="c.id" class="hover:bg-gray-50">
                  <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{{ index + 1 }}</td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{{ c.name }}</td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ c.dob }}</td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ c.seaman_book_no }}</td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ c.seaman_book_expiry }}</td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ c.rank }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';

const manifest = ref(null);
const route = useRoute();
const router = useRouter();

// Fungsi untuk memicu dialog cetak browser
const printPage = () => {
  window.print();
};

onMounted(async () => {
  const token = localStorage.getItem("token");
  if (!token) {
    alert("Sesi tidak valid, silahkan login kembali.");
    router.push('/');
    return;
  }

  try {
    const manifestId = route.params.id;
    const res = await fetch(`/api/manifests/${manifestId}`, {
      headers: {
        "Authorization": "Bearer " + token
      }
    });

    if (!res.ok) {
       if (res.status === 401) {
         alert("Sesi Anda telah berakhir. Silahkan login kembali.");
         router.push('/');
       } else {
         alert("Gagal mengambil data detail. Sesi mungkin berakhir.");
         router.push('/manifests'); // Go back to the list page
       }
       return;
    }

    manifest.value = await res.json();
  } catch (err) {
    alert("Terjadi kesalahan jaringan.");
    console.error(err);
    router.push('/manifests');
  }
});
</script>