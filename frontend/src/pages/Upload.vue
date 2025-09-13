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
          let errorMsg = response.statusText; // Default error
          try {
            // Try to parse error as JSON, as expected from our API
            const errorData = await response.json();
            errorMsg = errorData.detail || errorMsg;
          } catch (e) {
            // Parsing failed (it was HTML or text), just use the default statusText
            console.error("Could not parse error response as JSON", e);
          }
          alert("Upload failed: " + errorMsg);
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