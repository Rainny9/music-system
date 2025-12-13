<template>
  <div class="login-page">
    <div class="login-container">
      <!-- 左侧装饰区 -->
      <div class="login-left">
        <div class="brand">
          <div class="brand-icon">♪</div>
          <h1>音乐馆</h1>
          <p>发现音乐，分享快乐</p>
        </div>
        <div class="decoration">
          <div class="circle c1"></div>
          <div class="circle c2"></div>
          <div class="circle c3"></div>
        </div>
      </div>

      <!-- 右侧登录表单 -->
      <div class="login-right">
        <div class="login-form-wrapper">
          <h2 class="form-title">欢迎回来</h2>
          <p class="form-subtitle">登录您的账号继续探索音乐世界</p>

          <el-form :model="form" class="login-form">
            <div class="input-group">
              <div class="input-icon">
                <svg viewBox="0 0 24 24" width="20" height="20">
                  <path fill="#999" d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
                </svg>
              </div>
              <el-input
                v-model="form.username"
                placeholder="请输入用户名"
                clearable
                size="large"
              />
            </div>

            <div class="input-group">
              <div class="input-icon">
                <svg viewBox="0 0 24 24" width="20" height="20">
                  <path fill="#999" d="M18 8h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2zm-6 9c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zm3.1-9H8.9V6c0-1.71 1.39-3.1 3.1-3.1 1.71 0 3.1 1.39 3.1 3.1v2z"/>
                </svg>
              </div>
              <el-input
                v-model="form.password"
                type="password"
                show-password
                placeholder="请输入密码"
                size="large"
              />
            </div>

            <el-button 
              type="primary" 
              class="login-btn" 
              @click="handleLogin" 
              :loading="loading"
              size="large"
            >
              登 录
            </el-button>

            <div class="form-footer">
              <span>还没有账号？</span>
              <a @click="goRegister" class="link">立即注册</a>
            </div>
          </el-form>

          <div class="login-msg" v-if="msg">
            <el-alert :title="msg" :type="msgType" show-icon :closable="false" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import api from "../api";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";

const router = useRouter();

const form = ref({
  username: "",
  password: "",
});

const msg = ref("");
const msgType = ref("info");
const loading = ref(false);

const handleLogin = async () => {
  if (!form.value.username || !form.value.password) {
    msg.value = "用户名和密码不能为空";
    msgType.value = "warning";
    return;
  }
  loading.value = true;
  try {
    const res = await api.post("/login", {
      username: form.value.username,
      password: form.value.password,
    });
    msg.value = "登录成功";
    msgType.value = "success";

    localStorage.setItem("user_id", res.data.user_id);
    localStorage.setItem("is_admin", res.data.is_admin ? "1" : "0");
    localStorage.setItem("username", res.data.username || "");
    if (res.data.avatar_url) {
      localStorage.setItem("avatar_url", res.data.avatar_url);
    }

    ElMessage.success("登录成功");
    router.push("/");
  } catch (e) {
    msg.value = e.response?.data?.msg || "登录失败";
    msgType.value = "error";
  } finally {
    loading.value = false;
  }
};

const goRegister = () => {
  router.push("/register");
};
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
  padding: 20px;
}

.login-container {
  display: flex;
  width: 900px;
  max-width: 100%;
  background: #fff;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.25);
}

.login-left {
  flex: 1;
  background: linear-gradient(135deg, #31c27c 0%, #16a085 100%);
  padding: 60px 40px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  position: relative;
  overflow: hidden;
}

.brand {
  text-align: center;
  color: #fff;
  z-index: 1;
}

.brand-icon {
  width: 80px;
  height: 80px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 40px;
  margin: 0 auto 20px;
  backdrop-filter: blur(10px);
}

.brand h1 {
  font-size: 32px;
  margin-bottom: 10px;
  font-weight: 600;
}

.brand p {
  font-size: 16px;
  opacity: 0.9;
}

.decoration {
  position: absolute;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
}

.circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
}

.c1 {
  width: 200px;
  height: 200px;
  top: -50px;
  left: -50px;
}

.c2 {
  width: 150px;
  height: 150px;
  bottom: -30px;
  right: -30px;
}

.c3 {
  width: 100px;
  height: 100px;
  bottom: 50%;
  left: 10%;
}

.login-right {
  flex: 1;
  padding: 60px 50px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.login-form-wrapper {
  width: 100%;
  max-width: 320px;
}

.form-title {
  font-size: 28px;
  color: #333;
  margin-bottom: 8px;
  font-weight: 600;
}

.form-subtitle {
  font-size: 14px;
  color: #999;
  margin-bottom: 30px;
}

.input-group {
  position: relative;
  margin-bottom: 20px;
}

.input-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  z-index: 1;
}

.input-group :deep(.el-input__wrapper) {
  padding-left: 40px;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.input-group :deep(.el-input__wrapper:hover) {
  box-shadow: 0 2px 12px rgba(49, 194, 124, 0.2);
}

.input-group :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 2px rgba(49, 194, 124, 0.3);
}

.login-btn {
  width: 100%;
  height: 48px;
  border-radius: 10px;
  font-size: 16px;
  font-weight: 500;
  background: linear-gradient(135deg, #31c27c 0%, #16a085 100%);
  border: none;
  margin-top: 10px;
}

.login-btn:hover {
  background: linear-gradient(135deg, #28a86d 0%, #138a72 100%);
}

.form-footer {
  text-align: center;
  margin-top: 24px;
  font-size: 14px;
  color: #999;
}

.link {
  color: #31c27c;
  cursor: pointer;
  margin-left: 4px;
}

.link:hover {
  text-decoration: underline;
}

.login-msg {
  margin-top: 20px;
}

@media (max-width: 768px) {
  .login-left {
    display: none;
  }
  
  .login-container {
    width: 100%;
  }
  
  .login-right {
    padding: 40px 30px;
  }
}
</style>
