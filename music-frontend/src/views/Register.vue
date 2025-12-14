<template>
  <div class="register-page">
    <div class="register-container">
      <!-- 左侧装饰区 -->
      <div class="register-left">
        <div class="brand">
          <div class="brand-icon">♪</div>
          <h1>音乐分类检索系统</h1>
          <p>加入我们，开启音乐之旅</p>
        </div>
        <div class="decoration">
          <div class="circle c1"></div>
          <div class="circle c2"></div>
          <div class="circle c3"></div>
        </div>
      </div>

      <!-- 右侧注册表单 -->
      <div class="register-right">
        <div class="register-form-wrapper">
          <h2 class="form-title">创建账号</h2>
          <p class="form-subtitle">注册成为会员，享受更多功能</p>

          <el-form :model="form" class="register-form">
            <!-- 头像上传 -->
            <div class="avatar-upload">
              <div class="avatar-preview" @click="triggerUpload">
                <img v-if="avatarPreview" :src="avatarPreview" alt="头像" />
                <div v-else class="avatar-placeholder">
                  <svg viewBox="0 0 24 24" width="40" height="40">
                    <path fill="#ccc" d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
                  </svg>
                </div>
                <div class="avatar-overlay">
                  <svg viewBox="0 0 24 24" width="20" height="20">
                    <path fill="#fff" d="M3 4V1h2v3h3v2H5v3H3V6H0V4h3zm3 6V7h3V4h7l1.83 2H21c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H5c-1.1 0-2-.9-2-2V10h3zm7 9c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-3.2-5c0 1.77 1.43 3.2 3.2 3.2s3.2-1.43 3.2-3.2-1.43-3.2-3.2-3.2-3.2 1.43-3.2 3.2z"/>
                  </svg>
                </div>
              </div>
              <input 
                ref="fileInput" 
                type="file" 
                accept="image/*" 
                @change="handleAvatarChange" 
                style="display: none"
              />
              <span class="avatar-tip">点击上传头像</span>
            </div>

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

            <div class="input-group">
              <div class="input-icon">
                <svg viewBox="0 0 24 24" width="20" height="20">
                  <path fill="#999" d="M18 8h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2zm-6 9c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zm3.1-9H8.9V6c0-1.71 1.39-3.1 3.1-3.1 1.71 0 3.1 1.39 3.1 3.1v2z"/>
                </svg>
              </div>
              <el-input
                v-model="form.confirmPassword"
                type="password"
                show-password
                placeholder="请确认密码"
                size="large"
              />
            </div>

            <el-button 
              type="primary" 
              class="register-btn" 
              @click="handleRegister" 
              :loading="loading"
              size="large"
            >
              注 册
            </el-button>

            <div class="form-footer">
              <span>已有账号？</span>
              <a @click="backToLogin" class="link">立即登录</a>
            </div>
          </el-form>

          <div class="register-msg" v-if="msg">
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
const fileInput = ref(null);

const form = ref({
  username: "",
  password: "",
  confirmPassword: "",
});

const avatarFile = ref(null);
const avatarPreview = ref("");
const msg = ref("");
const msgType = ref("info");
const loading = ref(false);

const triggerUpload = () => {
  fileInput.value?.click();
};

const handleAvatarChange = (e) => {
  const file = e.target.files[0];
  if (file) {
    if (file.size > 5 * 1024 * 1024) {
      ElMessage.warning("图片大小不能超过5MB");
      return;
    }
    avatarFile.value = file;
    const reader = new FileReader();
    reader.onload = (e) => {
      avatarPreview.value = e.target.result;
    };
    reader.readAsDataURL(file);
  }
};

const handleRegister = async () => {
  if (!form.value.username || !form.value.password) {
    msg.value = "用户名和密码不能为空";
    msgType.value = "warning";
    return;
  }
  if (form.value.password !== form.value.confirmPassword) {
    msg.value = "两次输入的密码不一致";
    msgType.value = "warning";
    return;
  }
  if (form.value.password.length < 6) {
    msg.value = "密码长度至少6位";
    msgType.value = "warning";
    return;
  }

  loading.value = true;
  try {
    // 注册用户
    const res = await api.post("/register", {
      username: form.value.username,
      password: form.value.password,
    });
    
    const userId = res.data.user_id;
    
    // 如果有头像，上传头像
    if (avatarFile.value && userId) {
      const formData = new FormData();
      formData.append("avatar", avatarFile.value);
      await api.post(`/users/${userId}/avatar`, formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });
    }

    msg.value = "注册成功，请返回登录";
    msgType.value = "success";
    ElMessage.success("注册成功，请使用该账号登录");
    
    // 2秒后跳转到登录页
    setTimeout(() => {
      router.push("/login");
    }, 2000);
  } catch (e) {
    msg.value = e.response?.data?.msg || "注册失败";
    msgType.value = "error";
  } finally {
    loading.value = false;
  }
};

const backToLogin = () => {
  router.push("/login");
};
</script>

<style scoped>
/* 注册页 - 水墨丹青风 */
.register-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #fffef9;
  /* 水墨竹石淡纹背景 */
  background-image: 
    url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 200 800'%3E%3Cg fill='none' stroke='%232d5a5a' stroke-width='0.5' opacity='0.1'%3E%3Cpath d='M30 800 Q35 600 30 400 Q25 200 35 0'/%3E%3Cpath d='M35 350 Q60 320 45 280'/%3E%3Cpath d='M28 450 Q5 420 15 380'/%3E%3Cpath d='M32 550 Q55 530 48 490'/%3E%3Cpath d='M25 650 Q0 620 12 580'/%3E%3Cpath d='M38 250 Q58 230 52 200'/%3E%3Cpath d='M33 150 Q10 130 18 100'/%3E%3Cellipse cx='80' cy='750' rx='35' ry='20'/%3E%3Cellipse cx='90' cy='730' rx='25' ry='15'/%3E%3Cellipse cx='70' cy='770' rx='20' ry='12'/%3E%3C/g%3E%3C/svg%3E"),
    url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 200 800'%3E%3Cg fill='none' stroke='%232d5a5a' stroke-width='0.5' opacity='0.1'%3E%3Cpath d='M170 800 Q165 600 170 400 Q175 200 165 0'/%3E%3Cpath d='M165 350 Q140 320 155 280'/%3E%3Cpath d='M172 450 Q195 420 185 380'/%3E%3Cpath d='M168 550 Q145 530 152 490'/%3E%3Cpath d='M175 650 Q200 620 188 580'/%3E%3Cpath d='M162 250 Q142 230 148 200'/%3E%3Cpath d='M167 150 Q190 130 182 100'/%3E%3Cellipse cx='120' cy='750' rx='35' ry='20'/%3E%3Cellipse cx='110' cy='730' rx='25' ry='15'/%3E%3Cellipse cx='130' cy='770' rx='20' ry='12'/%3E%3C/g%3E%3C/svg%3E"),
    linear-gradient(135deg, #E6F4EA 0%, #fffef9 50%, #E6F4EA 100%);
  background-position: left top, right top, center;
  background-repeat: repeat-y, repeat-y, no-repeat;
  background-size: 200px auto, 200px auto, 100% 100%;
  padding: 20px;
}

.register-container {
  display: flex;
  width: 900px;
  max-width: 100%;
  background: #ffffff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 25px 60px rgba(45, 90, 90, 0.15);
  border: 1px solid rgba(212, 168, 75, 0.3);
}

.register-left {
  flex: 1;
  background: linear-gradient(135deg, #1e3d3d 0%, #2d5a5a 50%, #1e3d3d 100%);
  padding: 60px 40px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  position: relative;
  overflow: hidden;
}

/* 水墨山水背景 */
.register-left::before {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 40%;
  background: linear-gradient(to top, rgba(45, 90, 90, 0.3), transparent);
  opacity: 0.5;
}

.register-left::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 400 200'%3E%3Cpath fill='%232d5a5a' fill-opacity='0.15' d='M0 200L50 160L100 180L150 140L200 170L250 120L300 150L350 100L400 130V200H0Z'/%3E%3Cpath fill='%232d5a5a' fill-opacity='0.1' d='M0 200L80 170L160 190L240 150L320 180L400 140V200H0Z'/%3E%3C/svg%3E");
  background-size: cover;
  background-position: bottom;
}

.brand {
  text-align: center;
  color: #e8c478;
  z-index: 1;
}

.brand-icon {
  width: 90px;
  height: 90px;
  background: linear-gradient(135deg, #2d5a5a, #1e3d3d);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 44px;
  margin: 0 auto 24px;
  border: 3px solid #d4a84b;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
}

.brand h1 {
  font-size: 32px;
  margin-bottom: 12px;
  font-weight: 600;
  letter-spacing: 6px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  color: #fff;
}

.brand p {
  font-size: 14px;
  opacity: 0.7;
  letter-spacing: 2px;
  color: #d4a84b;
}

.decoration {
  position: absolute;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
  z-index: 0;
}

.circle {
  position: absolute;
  border-radius: 50%;
  border: 1px solid rgba(212, 168, 75, 0.15);
}

.c1 { width: 200px; height: 200px; top: -50px; left: -50px; }
.c2 { width: 150px; height: 150px; bottom: -30px; right: -30px; }
.c3 { width: 80px; height: 80px; top: 30%; right: 20%; background: rgba(45, 90, 90, 0.1); }

.register-right {
  flex: 1;
  padding: 40px 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(180deg, #ffffff 0%, #E6F4EA 100%);
}

.register-form-wrapper {
  width: 100%;
  max-width: 320px;
}

.form-title {
  font-size: 26px;
  color: #1a1a1a;
  margin-bottom: 8px;
  font-weight: 600;
  letter-spacing: 2px;
}

.form-subtitle {
  font-size: 14px;
  color: #888;
  margin-bottom: 24px;
}

.avatar-upload {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 24px;
}

.avatar-preview {
  width: 90px;
  height: 90px;
  border-radius: 50%;
  background: #f5f5f5;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  border: 3px solid #e0e0e0;
  transition: all 0.3s;
}

.avatar-preview:hover {
  border-color: #d4a84b;
}

.avatar-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-placeholder svg path {
  fill: #2d5a5a;
}

.avatar-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 30px;
  background: rgba(212, 168, 75, 0.85);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s;
}

.avatar-preview:hover .avatar-overlay {
  opacity: 1;
}

.avatar-tip {
  font-size: 12px;
  color: #888;
  margin-top: 8px;
}

.input-group {
  position: relative;
  margin-bottom: 16px;
}

.input-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  z-index: 1;
}

.input-icon svg path {
  fill: #2d5a5a;
}

.input-group :deep(.el-input__wrapper) {
  padding-left: 40px;
  border-radius: 6px;
  box-shadow: none;
  border: 1px solid #c8e6cf;
  background: #fffef9;
}

.input-group :deep(.el-input__wrapper:hover) {
  border-color: #d4a84b;
  background: #fff;
}

.input-group :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 2px rgba(212, 168, 75, 0.2);
  border-color: #d4a84b;
  background: #fff;
}

.register-btn {
  width: 100%;
  height: 48px;
  border-radius: 6px;
  font-size: 16px;
  font-weight: 500;
  background: linear-gradient(135deg, #d4a84b 0%, #b8923d 100%);
  border: none;
  margin-top: 10px;
  letter-spacing: 4px;
  color: #fff;
  transition: all 0.3s;
}

.register-btn:hover {
  background: linear-gradient(135deg, #e8c478 0%, #d4a84b 100%);
  box-shadow: 0 4px 16px rgba(212, 168, 75, 0.4);
  transform: translateY(-1px);
}

.form-footer {
  text-align: center;
  margin-top: 20px;
  font-size: 14px;
  color: #888;
}

.link {
  color: #d4a84b;
  cursor: pointer;
  margin-left: 4px;
  font-weight: 500;
}

.link:hover {
  color: #b8923d;
  text-decoration: underline;
}

.register-msg {
  margin-top: 16px;
}

@media (max-width: 768px) {
  .register-left { display: none; }
  .register-container { width: 100%; }
  .register-right { padding: 30px 20px; }
}
</style>
