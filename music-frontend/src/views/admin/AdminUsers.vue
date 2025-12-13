<template>
  <div class="admin-users">
    <!-- 后台导航标签 -->
    <div class="admin-tabs">
      <router-link to="/admin/songs" class="tab-item" :class="{ active: $route.path === '/admin/songs' }">
        <svg viewBox="0 0 24 24" width="18" height="18">
          <path fill="currentColor" d="M12 3v10.55c-.59-.34-1.27-.55-2-.55-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4V7h4V3h-6z"/>
        </svg>
        歌曲管理
      </router-link>
      <router-link to="/admin/users" class="tab-item" :class="{ active: $route.path === '/admin/users' }">
        <svg viewBox="0 0 24 24" width="18" height="18">
          <path fill="currentColor" d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"/>
        </svg>
        用户管理
      </router-link>
      <router-link to="/admin/announcements" class="tab-item" :class="{ active: $route.path === '/admin/announcements' }">
        <svg viewBox="0 0 24 24" width="18" height="18">
          <path fill="currentColor" d="M20 2H4c-1.1 0-1.99.9-1.99 2L2 22l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-7 9h-2V5h2v6zm0 4h-2v-2h2v2z"/>
        </svg>
        公告管理
      </router-link>
    </div>

    <div class="page-header">
      <h2>用户管理</h2>
      <button class="btn primary" @click="showAddModal = true">
        <svg viewBox="0 0 24 24" width="16" height="16">
          <path fill="currentColor" d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
        </svg>
        添加用户
      </button>
    </div>

    <!-- 用户列表 -->
    <div class="table-wrapper">
      <table class="user-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>用户名</th>
            <th>角色</th>
            <th>注册时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.id">
            <td>{{ user.id }}</td>
            <td>
              <span class="username">{{ user.username }}</span>
            </td>
            <td>
              <span class="role-badge" :class="{ admin: user.is_admin }">
                {{ user.is_admin ? '管理员' : '普通用户' }}
              </span>
            </td>
            <td>{{ formatDate(user.created_at) }}</td>
            <td>
              <div class="action-btns">
                <button class="icon-btn" @click="openEditModal(user)" title="编辑">
                  <svg viewBox="0 0 24 24" width="16" height="16">
                    <path fill="currentColor" d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/>
                  </svg>
                </button>
                <button 
                  class="icon-btn danger" 
                  @click="confirmDelete(user)" 
                  title="删除"
                  :disabled="user.id === currentUserId"
                >
                  <svg viewBox="0 0 24 24" width="16" height="16">
                    <path fill="currentColor" d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
                  </svg>
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 添加用户弹窗 -->
    <div v-if="showAddModal" class="modal-overlay" @click.self="showAddModal = false">
      <div class="modal">
        <div class="modal-header">
          <h3>添加用户</h3>
          <button class="close-btn" @click="showAddModal = false">×</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>用户名</label>
            <input v-model="newUser.username" placeholder="请输入用户名" />
          </div>
          <div class="form-group">
            <label>密码</label>
            <input v-model="newUser.password" type="password" placeholder="请输入密码" />
          </div>
          <div class="form-group">
            <label class="checkbox-label">
              <input type="checkbox" v-model="newUser.is_admin" />
              <span>设为管理员</span>
            </label>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn" @click="showAddModal = false">取消</button>
          <button class="btn primary" @click="addUser">确认添加</button>
        </div>
      </div>
    </div>

    <!-- 编辑用户弹窗 -->
    <div v-if="showEditModal" class="modal-overlay" @click.self="showEditModal = false">
      <div class="modal">
        <div class="modal-header">
          <h3>编辑用户</h3>
          <button class="close-btn" @click="showEditModal = false">×</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>用户名</label>
            <input v-model="editUser.username" placeholder="请输入用户名" />
          </div>
          <div class="form-group">
            <label>新密码（留空则不修改）</label>
            <input v-model="editUser.password" type="password" placeholder="请输入新密码" />
          </div>
          <div class="form-group">
            <label class="checkbox-label">
              <input type="checkbox" v-model="editUser.is_admin" />
              <span>设为管理员</span>
            </label>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn" @click="showEditModal = false">取消</button>
          <button class="btn primary" @click="updateUser">保存修改</button>
        </div>
      </div>
    </div>

    <!-- Toast 提示 -->
    <div v-if="toast.show" class="toast" :class="toast.type">
      {{ toast.message }}
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '../../api';

const users = ref([]);
const showAddModal = ref(false);
const showEditModal = ref(false);
const currentUserId = ref(null);

const newUser = ref({
  username: '',
  password: '',
  is_admin: false
});

const editUser = ref({
  id: null,
  username: '',
  password: '',
  is_admin: false
});

const toast = ref({
  show: false,
  message: '',
  type: 'success'
});

const showToast = (message, type = 'success') => {
  toast.value = { show: true, message, type };
  setTimeout(() => {
    toast.value.show = false;
  }, 3000);
};

const formatDate = (dateStr) => {
  if (!dateStr) return '-';
  const date = new Date(dateStr);
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  });
};

const loadUsers = async () => {
  try {
    const adminId = localStorage.getItem('user_id');
    const res = await api.get(`/admin/users?admin_user_id=${adminId}`);
    users.value = res.data;
  } catch (e) {
    showToast(e.response?.data?.msg || '加载用户列表失败', 'error');
  }
};

const addUser = async () => {
  if (!newUser.value.username || !newUser.value.password) {
    showToast('请填写用户名和密码', 'error');
    return;
  }
  try {
    const adminId = localStorage.getItem('user_id');
    await api.post(`/admin/users?admin_user_id=${adminId}`, newUser.value);
    showToast('用户添加成功');
    showAddModal.value = false;
    newUser.value = { username: '', password: '', is_admin: false };
    loadUsers();
  } catch (e) {
    showToast(e.response?.data?.msg || '添加失败', 'error');
  }
};

const openEditModal = (user) => {
  editUser.value = {
    id: user.id,
    username: user.username,
    password: '',
    is_admin: user.is_admin
  };
  showEditModal.value = true;
};

const updateUser = async () => {
  if (!editUser.value.username) {
    showToast('用户名不能为空', 'error');
    return;
  }
  try {
    const adminId = localStorage.getItem('user_id');
    await api.put(`/admin/users/${editUser.value.id}?admin_user_id=${adminId}`, {
      username: editUser.value.username,
      password: editUser.value.password || undefined,
      is_admin: editUser.value.is_admin
    });
    showToast('用户信息已更新');
    showEditModal.value = false;
    loadUsers();
  } catch (e) {
    showToast(e.response?.data?.msg || '更新失败', 'error');
  }
};

const confirmDelete = async (user) => {
  if (user.id === currentUserId.value) {
    showToast('不能删除自己', 'error');
    return;
  }
  if (!confirm(`确定要删除用户 "${user.username}" 吗？该操作将同时删除该用户的所有收藏和评论。`)) {
    return;
  }
  try {
    const adminId = localStorage.getItem('user_id');
    await api.delete(`/admin/users/${user.id}?admin_user_id=${adminId}`);
    showToast('用户已删除');
    loadUsers();
  } catch (e) {
    showToast(e.response?.data?.msg || '删除失败', 'error');
  }
};

onMounted(() => {
  currentUserId.value = Number(localStorage.getItem('user_id'));
  loadUsers();
});
</script>

<style scoped>
.admin-users {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.admin-tabs {
  display: flex;
  gap: 4px;
  margin-bottom: 20px;
  background: #fff;
  padding: 6px;
  border-radius: 10px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
}

.tab-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 14px;
  color: #666;
  text-decoration: none;
  transition: all 0.2s;
}

.tab-item:hover {
  background: #f5f5f5;
  color: #333;
}

.tab-item.active {
  background: #31c27c;
  color: #fff;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  font-size: 20px;
  font-weight: 600;
  color: #333;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  background: #fff;
  color: #606266;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn:hover {
  border-color: #31c27c;
  color: #31c27c;
}

.btn.primary {
  background: #31c27c;
  border-color: #31c27c;
  color: #fff;
}

.btn.primary:hover {
  background: #28a86d;
}

.table-wrapper {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
  overflow: hidden;
}

.user-table {
  width: 100%;
  border-collapse: collapse;
}

.user-table th,
.user-table td {
  padding: 14px 16px;
  text-align: left;
  border-bottom: 1px solid #f0f0f0;
}

.user-table th {
  background: #fafafa;
  font-weight: 500;
  color: #666;
  font-size: 13px;
}

.user-table td {
  font-size: 14px;
  color: #333;
}

.username {
  font-weight: 500;
}

.role-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  background: #f0f0f0;
  color: #666;
}

.role-badge.admin {
  background: #e8f5e9;
  color: #2e7d32;
}

.action-btns {
  display: flex;
  gap: 8px;
}

.icon-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: #f5f5f5;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
  transition: all 0.2s;
}

.icon-btn:hover {
  background: #e8f5e9;
  color: #31c27c;
}

.icon-btn.danger:hover {
  background: #ffebee;
  color: #f44336;
}

.icon-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

/* 弹窗样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: #fff;
  border-radius: 12px;
  width: 420px;
  max-width: 90%;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #f0f0f0;
}

.modal-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.close-btn {
  width: 28px;
  height: 28px;
  border: none;
  background: none;
  font-size: 20px;
  color: #999;
  cursor: pointer;
  border-radius: 4px;
}

.close-btn:hover {
  background: #f5f5f5;
  color: #666;
}

.modal-body {
  padding: 20px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  font-size: 13px;
  color: #666;
  margin-bottom: 6px;
}

.form-group input[type="text"],
.form-group input[type="password"] {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  font-size: 14px;
  box-sizing: border-box;
}

.form-group input:focus {
  outline: none;
  border-color: #31c27c;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.checkbox-label input[type="checkbox"] {
  width: 16px;
  height: 16px;
  cursor: pointer;
}

.checkbox-label span {
  font-size: 14px;
  color: #333;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 16px 20px;
  border-top: 1px solid #f0f0f0;
}

/* Toast */
.toast {
  position: fixed;
  top: 80px;
  left: 50%;
  transform: translateX(-50%);
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 14px;
  z-index: 2000;
  animation: slideDown 0.3s ease;
}

.toast.success {
  background: #e8f5e9;
  color: #2e7d32;
}

.toast.error {
  background: #ffebee;
  color: #c62828;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateX(-50%) translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
}
</style>
