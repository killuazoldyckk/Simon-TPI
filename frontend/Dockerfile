# Gunakan image Node berbasis Alpine (lebih ringan)
FROM node:20-alpine

# --- TAMBAHKAN BARIS INI ---
# Install 'curl' untuk healthcheck di docker-compose
RUN apk add --no-cache curl

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