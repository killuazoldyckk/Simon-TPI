// frontend/src/api.js

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
export const apiFetch = async (url, options = {}) => {
  const token = localStorage.getItem('token');
  
  const headers = {
    'Accept': 'application/json',
    ...options.headers,
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  const response = await fetch(`${API_BASE_URL}${url}`, { ...options, headers });

  // --- INI ADALAH PERBAIKAN UTAMA ---
  // Jika respons TIDAK 'ok' (seperti 404, 500, dll.)
  if (!response.ok) {
    let errorMessage = `Error: ${response.status} ${response.statusText}`;
    
    try {
      // Coba baca detail error dari server
      const errorData = await response.json();
      
      // Cek jika detailnya ada dan berupa string atau objek
      if (errorData.detail) {
        // Jika detailnya adalah objek, ubah jadi string agar bisa dibaca
        if (typeof errorData.detail === 'object') {
          errorMessage = JSON.stringify(errorData.detail);
        } else {
          errorMessage = errorData.detail;
        }
      }
    } catch (e) {
      // Biarkan pesan error default jika body tidak bisa dibaca
    }

    // Lemparkan error dengan pesan yang sudah pasti berupa string
    throw new Error(errorMessage); // <-- Baris 38 sekarang akan selalu melempar string
  }

  // Untuk respons berhasil tanpa konten (DELETE), langsung kembalikan responsnya.
  if (response.status === 204) {
    return response;
  }
  
  // Untuk semua respons berhasil lainnya (GET, POST), kembalikan respons utuh.
  return response;
};