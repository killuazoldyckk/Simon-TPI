<template>
  <div>
    <h1>Upload Manifest</h1>
    
    <input type="file" @change="handleFile">
    <button @click="uploadFile" :disabled="!file">Upload</button>
  </div>
</template>


<script>
export default {
  data() {
    return { file: null };
  },
  methods: {
    handleFile(e) {
      this.file = e.target.files[0];
    },
    async uploadFile() {
      // Your existing logic is correct.
      const token = localStorage.getItem("token");
      if (!token) {
        alert("Anda harus login");
        this.$router.push("/");
        return;
      }

      // Check if a file was actually selected
      if (!this.file) {
        alert("Please select a file first.");
        return;
      }

      const formData = new FormData();
      formData.append("file", this.file);

      // Make sure the token includes "Bearer "
      const authToken = token.startsWith("Bearer ") ? token : "Bearer " + token;

      try {
        const response = await fetch("/api/manifests/upload", {
          method: "POST",
          headers: { 
            // Note: Don't set Content-Type on FormData, browser does it automatically
            Authorization: authToken 
          },
          body: formData,
        });

        if (!response.ok) {
          // Handle HTTP errors from the backend
          const errorData = await response.json();
          alert("Upload failed: " + (errorData.detail || response.statusText));
          return;
        }

        // Only redirect if the upload was successful
        this.$router.push("/manifests");

      } catch (error) {
        console.error("Upload error:", error);
        alert("An error occurred during upload.");
      }
    },
  },
};
</script>