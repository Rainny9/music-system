<template>
  <div class="admin-users">
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
/* 中华文化主题 - 用户管理 */
.admin-users {
  padding: 20px;
  padding-bottom: 100px;
  max-width: 1200px;
  margin: 0 auto;
  background: rgba(255, 254, 249, 0.85);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 2px solid rgba(212, 168, 75, 0.3);
}

.page-header h2 {
  font-size: 22px;
  font-weight: 600;
  color: #1a1a1a;
  letter-spacing: 2px;
  position: relative;
  padding-left: 14px;
  margin: 0;
}

.page-header h2::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 22px;
  background: linear-gradient(180deg, #2d5a5a, #d4a84b);
  border-radius: 2px;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 10px 20px;
  border: 1px solid rgba(212, 168, 75, 0.3);
  border-radius: 6px;
  background: #fffef9;
  color: #8b7355;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn:hover {
  border-color: #2d5a5a;
  color: #2d5a5a;
}

.btn.primary {
  background: linear-gradient(135deg, rgba(255,255,255,0.4) 0%, #8BA8A8 50%, #7a9999 100%);
  border: 1px solid #d4a84b;
  color: #d4a84b;
}

.btn.primary:hover {
  background: linear-gradient(135deg, rgba(255,255,255,0.5) 0%, #9ab8b8 50%, #8BA8A8 100%);
  box-shadow: 0 4px 12px rgba(139, 168, 168, 0.4);
}

.table-wrapper {
  background: linear-gradient(180deg, #fffef9 0%, #E6F4EA 100%);
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(212, 168, 75, 0.1);
  border: 1px solid rgba(212, 168, 75, 0.2);
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
  border-bottom: 1px solid rgba(212, 168, 75, 0.1);
}

.user-table th {
  background: linear-gradient(135deg, rgba(212, 168, 75, 0.1), rgba(212, 168, 75, 0.05));
  font-weight: 600;
  color: #8b7355;
  font-size: 13px;
  letter-spacing: 1px;
}

.user-table td {
  font-size: 14px;
  color: #333;
}

.user-table tr:hover {
  background: rgba(45, 90, 90, 0.02);
}

.username {
  font-weight: 500;
}

.role-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  background: rgba(212, 168, 75, 0.1);
  color: #8b7355;
}

.role-badge.admin {
  background: rgba(45, 90, 90, 0.1);
  color: #2d5a5a;
}

.action-btns {
  display: flex;
  gap: 8px;
}

.icon-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: rgba(212, 168, 75, 0.1);
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #8b7355;
  transition: all 0.2s;
}

.icon-btn:hover {
  background: rgba(212, 168, 75, 0.2);
  color: #d4a84b;
}

.icon-btn.danger:hover {
  background: rgba(220, 53, 69, 0.1);
  color: #dc3545;
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
  background: rgba(26, 26, 26, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.modal {
  background: #fffef9;
  border-radius: 12px;
  width: 420px;
  max-width: 90%;
  box-shadow: 0 10px 40px rgba(45, 90, 90, 0.15);
  border: 1px solid rgba(212, 168, 75, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 18px 24px;
  border-bottom: 1px solid rgba(212, 168, 75, 0.2);
  background: linear-gradient(135deg, rgba(212, 168, 75, 0.05), transparent);
}

.modal-header h3 {
  font-size: 17px;
  font-weight: 600;
  color: #1a1a1a;
  letter-spacing: 1px;
  margin: 0;
}

.close-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: rgba(212, 168, 75, 0.1);
  border-radius: 50%;
  font-size: 20px;
  color: #8b7355;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.close-btn:hover {
  background: rgba(45, 90, 90, 0.1);
  color: #2d5a5a;
}

.modal-body {
  padding: 24px;
}

.form-group {
  margin-bottom: 18px;
}

.form-group label {
  display: block;
  font-size: 14px;
  color: #1a1a1a;
  margin-bottom: 8px;
  font-weight: 500;
}

.form-group input[type="text"],
.form-group input[type="password"] {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid rgba(212, 168, 75, 0.3);
  border-radius: 6px;
  font-size: 14px;
  box-sizing: border-box;
  background: #fff;
  transition: all 0.3s;
}

.form-group input:focus {
  outline: none;
  border-color: #d4a84b;
  box-shadow: 0 0 0 3px rgba(212, 168, 75, 0.1);
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
  accent-color: #2d5a5a;
}

.checkbox-label span {
  font-size: 14px;
  color: #333;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid rgba(212, 168, 75, 0.2);
  background: rgba(212, 168, 75, 0.03);
}

.modal-footer .btn {
  padding: 10px 24px;
}

.modal-footer .btn:not(.primary) {
  background: #fffef9;
  color: #8b7355;
  border: 1px solid rgba(212, 168, 75, 0.3);
}

.modal-footer .btn:not(.primary):hover {
  border-color: #d4a84b;
  color: #d4a84b;
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
  border: 1px solid;
}

.toast.success {
  background: rgba(46, 125, 50, 0.1);
  color: #2e7d32;
  border-color: rgba(46, 125, 50, 0.2);
}

.toast.error {
  background: rgba(220, 53, 69, 0.1);
  color: #dc3545;
  border-color: rgba(220, 53, 69, 0.2);
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
