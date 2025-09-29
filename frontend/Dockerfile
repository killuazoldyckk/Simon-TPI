# Gunakan image Node berbasis Alpine (lebih ringan). Jika butuh glibc, bisa pakai node:20-slim
FROM node:20-alpine

# Tentukan working directory
WORKDIR /app

# Salin hanya file dependency dulu agar cache layer bisa optimal
COPY package*.json ./

# Install dependencies secara bersih
RUN npm install --legacy-peer-deps

# Salin seluruh source code
COPY . .

# Expose port dev server
EXPOSE 5173

# Jalankan Vite dev server
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
