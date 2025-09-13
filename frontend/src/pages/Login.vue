<template>
  <div class="p-4">
    <h1>Login</h1>
    <form @submit.prevent="login">
      <input v-model="email" type="text" placeholder="Email" />
      <input v-model="password" type="password" placeholder="Password" />
      <button type="submit">Login</button>
    </form>
  </div>
</template>

<script>
export default {
  data() {
    return { email: "", password: "" };
  },
  methods: {
    async login() {
      const res = await fetch("/api/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: this.email, password: this.password }),
      });
      if (res.ok) {
        const data = await res.json();
        localStorage.setItem("token", data.token);
        this.$router.push("/upload");
      } else {
        alert("Login gagal");
      }
    },
  },
};
</script>
