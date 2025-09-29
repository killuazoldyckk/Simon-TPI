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
           <div class="p-5 grid grid-cols-1 md:grid-cols-3 gap-6 bg-gray-50">
              <div class="space-y-4">
                  <div>
                      <div class="text-xs font-semibold text-gray-500 uppercase tracking-wider">Pelabuhan Asal</div>
                      <div class="text-lg font-medium text-gray-800">{{ manifest.origin }}</div>
                  </div>
                  <div>
                      <div class="text-xs font-semibold text-gray-500 uppercase tracking-wider">Pelabuhan Tujuan</div>
                      <div class="text-lg font-medium text-gray-800">{{ manifest.destination }}</div>
                  </div>
              </div>

              <div class="space-y-4">
                  <div>
                      <div class="text-xs font-semibold text-gray-500 uppercase tracking-wider">Tanggal Berangkat</div>
                      <div class="text-lg font-medium text-gray-800">{{ manifest.departure_date }}</div>
                  </div>
                  <div>
                      <div class="text-xs font-semibold text-gray-500 uppercase tracking-wider">Tanggal Tiba</div>
                      <div class="text-lg font-medium text-gray-800">{{ manifest.arrival_date }}</div>
                  </div>
              </div>

              <div class="space-y-4">
                  <div>
                      <div class="text-xs font-semibold text-gray-500 uppercase tracking-wider">Total Penumpang</div>
                      <div class="text-lg font-medium text-gray-800">{{ manifest.passengers.length }} Orang</div>
                  </div>
                  <div>
                      <div class="text-xs font-semibold text-gray-500 uppercase tracking-wider">Total Awak Kapal</div>
                      <div class="text-lg font-medium text-gray-800">{{ manifest.crews.length }} Orang</div>
                  </div>
              </div>
          </div>
        </div>

        <div class="mb-4 border-b border-gray-200 no-print">
          <nav class="-mb-px flex space-x-8" aria-label="Tabs">
            <button @click="activeTab = 'passengers'" :class="[activeTab === 'passengers' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300', 'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm']">
              Penumpang ({{ manifest.passengers.length }})
            </button>
            <button @click="activeTab = 'crews'" :class="[activeTab === 'crews' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300', 'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm']">
              Awak Kapal ({{ manifest.crews.length }})
            </button>
          </nav>
        </div>

        <div class="bg-white rounded-lg shadow overflow-hidden">
          <div v-if="activeTab === 'passengers'">
            <div class="p-5 flex justify-between items-center">
              <h2 class="text-xl font-semibold text-gray-800">Daftar Penumpang</h2>
              <!-- <div class="relative w-1/3 no-print">
                    <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="h-5 w-5 text-gray-400">
                          <path stroke-linecap="round" stroke-linejoin="round" d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z" />
                        </svg>
                    </div>
                    <input type="text" v-model="crewSearch" placeholder="Cari nama atau buku pelaut..." class="block w-full rounded-md border-gray-300 pl-10 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm">
                </div> -->
              <input type="text" v-model="passengerSearch" placeholder="Cari nama atau paspor..." class="border p-2 rounded-md w-1/3 no-print">
            </div>
            <div class="overflow-x-auto">
              <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">No</th>
                    <th @click="sortBy('passengers', 'name')" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer">Nama &#8597;</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Sex</th>
                    <th @click="sortBy('passengers', 'dob')" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer">Tgl. Lahir &#8597;</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Negara</th>
                    <th @click="sortBy('passengers', 'passport_no')" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer">No. Paspor &#8597;</th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                  <tr v-if="paginatedPassengers.length === 0"><td colspan="6" class="p-4 text-center text-gray-500">Tidak ada data.</td></tr>
                  <tr v-for="(p, index) in paginatedPassengers" :key="p.id" class="hover:bg-gray-50">
                    <td class="px-6 py-4">{{ (passengerPage - 1) * itemsPerPage + index + 1 }}</td>
                    <td class="px-6 py-4 font-medium">{{ p.name }}</td>
                    <td class="px-6 py-4">{{ p.sex }}</td>
                    <td class="px-6 py-4">{{ p.dob }}</td>
                    <td class="px-6 py-4">{{ p.nationality }}</td>
                    <td class="px-6 py-4">{{ p.passport_no }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div v-if="filteredPassengers.length > itemsPerPage" class="p-4 flex justify-between items-center no-print">
              <button @click="passengerPage--" :disabled="passengerPage === 1" class="px-4 py-2 bg-gray-200 rounded disabled:opacity-50">Sebelumnya</button>
              <span>Halaman {{ passengerPage }} dari {{ totalPassengerPages }}</span>
              <button @click="passengerPage++" :disabled="passengerPage === totalPassengerPages" class="px-4 py-2 bg-gray-200 rounded disabled:opacity-50">Berikutnya</button>
            </div>
          </div>

          <div v-show="activeTab === 'crews'">
            <div class="p-5 flex justify-between items-center">
              <h2 class="text-xl font-semibold text-gray-800">Daftar Awak Kapal</h2>
              <input type="text" v-model="crewSearch" placeholder="Cari nama atau paspor..." class="border p-2 rounded-md w-1/3 no-print">
            </div>
            <div class="overflow-x-auto">
              <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-6 py-3 text-left text-xs font-medium uppercase">No</th>
                    <th class="px-6 py-3 text-left text-xs font-medium uppercase">Nama</th>
                    <th class="px-6 py-3 text-left text-xs font-medium uppercase">Tgl. Lahir</th>
                    <th class="px-6 py-3 text-left text-xs font-medium uppercase">No. Paspor</th>
                    <th class="px-6 py-3 text-left text-xs font-medium uppercase">Masa Berlaku</th>
                    <th class="px-6 py-3 text-left text-xs font-medium uppercase">No. Buku Pelaut</th>
                    <th class="px-6 py-3 text-left text-xs font-medium uppercase">Masa Berlaku</th>
                    <th class="px-6 py-3 text-left text-xs font-medium uppercase no-print">Aksi</th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y">
                  <tr v-if="paginatedCrews.length === 0"><td colspan="7" class="p-4 text-center text-gray-500">Tidak ada data.</td></tr>
                  <tr v-for="(crew, index) in paginatedCrews" :key="crew.id">
                    <td class="px-6 py-4">{{ (crewPage - 1) * itemsPerPage + index + 1 }}</td>
                    <td class="px-6 py-4 font-medium">{{ crew.name }}</td>
                    <td class="px-6 py-4">{{ crew.dob }}</td>
                    <template v-if="editingCrewId !== crew.id">
                      <td class="px-6 py-4">{{ crew.passport_no || '-' }}</td>
                      <td class="px-6 py-4">{{ crew.passport_expiry || '-' }}</td>
                    </template>
                    <template v-else>
                      <td class="px-6 py-4"><input type="text" v-model="editFormData.passport_no" class="border p-1 rounded w-full"></td>
                      <td class="px-6 py-4"><input type="date" v-model="editFormData.passport_expiry" class="border p-1 rounded w-full"></td>
                    </template>
                    <td class="px-6 py-4">{{ crew.seaman_book_no }}</td>
                    <td class="px-6 py-4">{{ crew.seaman_book_expiry }}</td>
                    <td class="px-6 py-4 text-sm font-medium no-print">
                      <div v-if="editingCrewId !== crew.id">
                        <button @click="startEditing(crew)" class="text-blue-600 hover:text-blue-900">Ubah</button>
                      </div>
                      <div v-else class="flex space-x-2">
                        <button @click="saveChanges(crew.id)" class="text-green-600 hover:text-green-900">Simpan</button>
                        <button @click="cancelEditing" class="text-red-600 hover:text-red-900">Batal</button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
              </div>
            </div>
          </div>
        </div>

        </div>
      </div>
  
</template>


<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';

const manifest = ref(null);
const isLoading = ref(true);
const activeTab = ref('passengers');

const editingCrewId = ref(null);
const editFormData = ref({ passport_no: '', passport_expiry: '' });

const passengerSearch = ref('');
const crewSearch = ref('');
const passengerPage = ref(1);
const crewPage = ref(1);
const itemsPerPage = ref(25);
const sortKey = ref({ passengers: 'name', crews: 'name' });
const sortOrder = ref({ passengers: 'asc', crews: 'asc' });

const route = useRoute();
const router = useRouter();

// Computed Properties for filtering, sorting, and pagination
const filteredPassengers = computed(() => {
  if (!manifest.value) return [];
  return manifest.value.passengers.filter(p => {
    const searchTerm = passengerSearch.value.toLowerCase();
    return p.name.toLowerCase().includes(searchTerm) || p.passport_no.toLowerCase().includes(searchTerm);
  }).sort((a, b) => {
    const key = sortKey.value.passengers;
    const order = sortOrder.value.passengers === 'asc' ? 1 : -1;
    if (a[key] < b[key]) return -1 * order;
    if (a[key] > b[key]) return 1 * order;
    return 0;
  });
});

const totalPassengerPages = computed(() => Math.ceil(filteredPassengers.value.length / itemsPerPage.value));
const paginatedPassengers = computed(() => {
  const start = (passengerPage.value - 1) * itemsPerPage.value;
  const end = start + itemsPerPage.value;
  return filteredPassengers.value.slice(start, end);
});

const filteredCrews = computed(() => {
  if (!manifest.value) return [];
  return manifest.value.crews.filter(c => {
    const searchTerm = crewSearch.value.toLowerCase();
    return c.name.toLowerCase().includes(searchTerm) || (c.seaman_book_no && c.seaman_book_no.toLowerCase().includes(searchTerm));
  }).sort((a, b) => {
    const key = sortKey.value.crews;
    const order = sortOrder.value.crews === 'asc' ? 1 : -1;
    if (a[key] < b[key]) return -1 * order;
    if (a[key] > b[key]) return 1 * order;
    return 0;
  });
});

const totalCrewPages = computed(() => Math.ceil(filteredCrews.value.length / itemsPerPage.value));
const paginatedCrews = computed(() => {
  const start = (crewPage.value - 1) * itemsPerPage.value;
  const end = start + itemsPerPage.value;
  return filteredCrews.value.slice(start, end);
});

// Fungsi untuk memicu dialog cetak browser
const printPage = () => {
  window.print();
};

const startEditing = (crew) => {
  editingCrewId.value = crew.id;
  editFormData.value.passport_no = crew.passport_no || '';
  editFormData.value.passport_expiry = crew.passport_expiry || '';
};

const cancelEditing = () => {
  editingCrewId.value = null;
};

const saveChanges = async (crewId) => {
  const token = localStorage.getItem("token");
  try {
    const res = await fetch(`/api/crews/${crewId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify(editFormData.value),
    });

    if (!res.ok) throw new Error("Gagal menyimpan perubahan.");
    
    const updatedCrew = await res.json();
    
    // Perbarui data di frontend secara lokal
    const index = manifest.value.crews.findIndex(c => c.id === crewId);
    if (index !== -1) {
      manifest.value.crews[index] = updatedCrew;
    }
    
    cancelEditing(); // Keluar dari mode edit

  } catch (err) {
    console.error(err);
    alert(err.message);
  }
};

const sortBy = (type, key) => {
  if (sortKey.value[type] === key) {
    sortOrder.value[type] = sortOrder.value[type] === 'asc' ? 'desc' : 'asc';
  } else {
    sortKey.value[type] = key;
    sortOrder.value[type] = 'asc';
  }
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