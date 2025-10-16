import router from './router'; // Impor router untuk melakukan redirect

// Definisikan base URL backend Anda
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

export const apiFetch = async (url, options = {}) => {
  const token = localStorage.getItem('token');
  
  // Siapkan header default
  const headers = {
    'Accept': 'application/json',
    ...options.headers,
  };

  // Tambahkan header Authorization jika token ada
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  // Lakukan panggilan fetch dengan header yang sudah disiapkan
  const response = await fetch(`${API_BASE_URL}${url}`, { ...options, headers });

  // --- INI BAGIAN KUNCINYA ---
  // Jika respons adalah 401, bersihkan sesi dan redirect ke login
  if (response.status === 401) {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
    router.push('/'); // Asumsi halaman login ada di path '/'
    
    // Lemparkan error agar komponen tahu permintaannya gagal
    throw new Error("Sesi Anda telah berakhir. Silakan login kembali.");
  }

  return response;
};