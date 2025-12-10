<template>
  <div>
    <h2>登录 / 注册</h2>
    <el-input v-model="username" placeholder="用户名" />
    <el-input v-model="password" type="password" placeholder="密码" />
    <el-button type="primary" @click="login">登录</el-button>
    <el-button type="primary" @click="register">注册</el-button>
    <p>{{ msg }}</p>
  </div>
</template>

<script setup>
import { ref } from "vue";
import api from "../api";
import { useRouter } from "vue-router";

const router = useRouter();
const username = ref("");
const password = ref("");
const msg = ref("");

const login = async () => {
  try {
    const res = await api.post("/login", {
      username: username.value,
      password: password.value,
    });
    msg.value = "登录成功";
    // TODO: 实际项目中请使用更安全的存储方式（如 token）
    localStorage.setItem("user_id", res.data.user_id);
localStorage.setItem("is_admin", res.data.is_admin ? "1" : "0"); // TODO: 以后换成更安全方案
    router.push("/");
  } catch (e) {
    msg.value = e.response?.data?.msg || "登录失败";
  }
};

const register = async () => {
  try {
    const res = await api.post("/register", {
      username: username.value,
      password: password.value,
    });
    msg.value = res.data.msg;
  } catch (e) {
    msg.value = e.response?.data?.msg || "注册失败";
  }
};
</script>