<template>
  <div>
    <h1>音乐系统</h1>
    <nav>
      <router-link to="/">首页</router-link> |
      <router-link to="/login">登录/注册</router-link> |
      <router-link to="/favorites">我的收藏</router-link>
      <span v-if="isAdmin"> | <router-link to="/admin/songs">后台管理</router-link></span>
    </nav>
    <hr />
    <router-view />
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";

const isAdmin = ref(false);

onMounted(() => {
  // TODO: 这里逻辑简单直接，从 localStorage 取；以后可以改为从 token 判断
  const flag = localStorage.getItem("is_admin");
  isAdmin.value = flag === "1" || flag === "true";
});
</script>

<style>
nav a {
  margin-right: 8px;
}
</style>