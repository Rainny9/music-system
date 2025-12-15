<template>
  <div class="admin-announcements">
    <div class="page-header">
      <h2>公告管理</h2>
      <button class="btn primary" @click="openAddModal">
        <svg viewBox="0 0 24 24" width="16" height="16">
          <path fill="currentColor" d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
        </svg>
        发布公告
      </button>
    </div>

    <!-- 公告列表 -->
    <div class="table-wrapper">
      <table class="ann-table">
        <thead>
          <tr>
            <th style="width: 60px">ID</th>
            <th style="width: 180px">标题</th>
            <th>内容</th>
            <th style="width: 80px">状态</th>
            <th style="width: 140px">过期时间</th>
            <th style="width: 140px">发布时间</th>
            <th style="width: 120px">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="ann in announcements" :key="ann.id" :class="{ expired: ann.is_expired }">
            <td>{{ ann.id }}</td>
            <td class="title-cell">{{ ann.title }}</td>
            <td class="content-cell">{{ ann.content }}</td>
            <td>
              <span class="status-badge" :class="getStatusClass(ann)">
                {{ getStatusText(ann) }}
              </span>
            </td>
            <td>{{ ann.expire_at ? formatDate(ann.expire_at) : '永不过期' }}</td>
            <td>{{ formatDate(ann.created_at) }}</td>
            <td>
              <div class="action-btns">
                <button class="icon-btn" @click="toggleStatus(ann)" :title="ann.is_active ? '隐藏' : '显示'">
                  <svg v-if="ann.is_active" viewBox="0 0 24 24" width="16" height="16">
                    <path fill="currentColor" d="M12 7c2.76 0 5 2.24 5 5 0 .65-.13 1.26-.36 1.83l2.92 2.92c1.51-1.26 2.7-2.89 3.43-4.75-1.73-4.39-6-7.5-11-7.5-1.4 0-2.74.25-3.98.7l2.16 2.16C10.74 7.13 11.35 7 12 7zM2 4.27l2.28 2.28.46.46C3.08 8.3 1.78 10.02 1 12c1.73 4.39 6 7.5 11 7.5 1.55 0 3.03-.3 4.38-.84l.42.42L19.73 22 21 20.73 3.27 3 2 4.27zM7.53 9.8l1.55 1.55c-.05.21-.08.43-.08.65 0 1.66 1.34 3 3 3 .22 0 .44-.03.65-.08l1.55 1.55c-.67.33-1.41.53-2.2.53-2.76 0-5-2.24-5-5 0-.79.2-1.53.53-2.2zm4.31-.78l3.15 3.15.02-.16c0-1.66-1.34-3-3-3l-.17.01z"/>
                  </svg>
                  <svg v-else viewBox="0 0 24 24" width="16" height="16">
                    <path fill="currentColor" d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"/>
                  </svg>
                </button>
                <button class="icon-btn" @click="openEditModal(ann)" title="编辑">
                  <svg viewBox="0 0 24 24" width="16" height="16">
                    <path fill="currentColor" d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/>
                  </svg>
                </button>
                <button class="icon-btn danger" @click="confirmDelete(ann)" title="删除">
                  <svg viewBox="0 0 24 24" width="16" height="16">
                    <path fill="currentColor" d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
                  </svg>
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="announcements.length === 0">
            <td colspan="7" class="empty-row">暂无公告</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 添加/编辑公告弹窗 -->
    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal">
        <div class="modal-header">
          <h3>{{ isEdit ? '编辑公告' : '发布公告' }}</h3>
          <button class="close-btn" @click="showModal = false">×</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>公告标题 <span class="required">*</span></label>
            <input v-model="form.title" placeholder="请输入公告标题" />
          </div>
          <div class="form-group">
            <label>公告内容 <span class="required">*</span></label>
            <textarea v-model="form.content" placeholder="请输入公告内容" rows="6"></textarea>
          </div>
          <div class="form-group">
            <label>过期时间（留空表示永不过期）</label>
            <input type="datetime-local" v-model="form.expire_at" />
          </div>
          <div class="form-group">
            <label class="checkbox-label">
              <input type="checkbox" v-model="form.is_active" />
              <span>立即发布</span>
            </label>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn" @click="showModal = false">取消</button>
          <button class="btn primary" @click="saveAnnouncement">{{ isEdit ? '保存修改' : '发布' }}</button>
        </div>
      </div>
    </div>

    <!-- Toast -->
    <div v-if="toast.show" class="toast" :class="toast.type">{{ toast.message }}</div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '../../api';

const announcements = ref([]);
const showModal = ref(false);
const isEdit = ref(false);
const form = ref({ id: null, title: '', content: '', is_active: true, expire_at: '' });
const toast = ref({ show: false, message: '', type: 'success' });

const showToast = (message, type = 'success') => {
  toast.value = { show: true, message, type };
  setTimeout(() => { toast.value.show = false; }, 3000);
};

const formatDate = (dateStr) => {
  if (!dateStr) return '-';
  return new Date(dateStr).toLocaleDateString('zh-CN', {
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit'
  });
};

// 格式化为 datetime-local 输入框格式
const formatDateTimeLocal = (dateStr) => {
  if (!dateStr) return '';
  const date = new Date(dateStr);
  return date.toISOString().slice(0, 16);
};

const getStatusClass = (ann) => {
  if (ann.is_expired) return 'expired';
  if (ann.is_active) return 'active';
  return '';
};

const getStatusText = (ann) => {
  if (ann.is_expired) return '已过期';
  if (ann.is_active) return '已发布';
  return '已隐藏';
};

const loadAnnouncements = async () => {
  try {
    const adminId = localStorage.getItem('user_id');
    const res = await api.get(`/admin/announcements?admin_user_id=${adminId}`);
    announcements.value = res.data;
  } catch (e) {
    showToast(e.response?.data?.msg || '加载公告失败', 'error');
  }
};

const openAddModal = () => {
  isEdit.value = false;
  form.value = { id: null, title: '', content: '', is_active: true, expire_at: '' };
  showModal.value = true;
};

const openEditModal = (ann) => {
  isEdit.value = true;
  form.value = { 
    id: ann.id, 
    title: ann.title, 
    content: ann.content, 
    is_active: ann.is_active,
    expire_at: formatDateTimeLocal(ann.expire_at)
  };
  showModal.value = true;
};

const saveAnnouncement = async () => {
  if (!form.value.title || !form.value.content) {
    showToast('请填写标题和内容', 'error');
    return;
  }
  try {
    const adminId = localStorage.getItem('user_id');
    if (isEdit.value) {
      await api.put(`/admin/announcements/${form.value.id}?admin_user_id=${adminId}`, form.value);
      showToast('公告已更新');
    } else {
      await api.post(`/admin/announcements?admin_user_id=${adminId}`, form.value);
      showToast('公告已发布');
    }
    showModal.value = false;
    loadAnnouncements();
  } catch (e) {
    showToast(e.response?.data?.msg || '操作失败', 'error');
  }
};

const toggleStatus = async (ann) => {
  try {
    const adminId = localStorage.getItem('user_id');
    await api.put(`/admin/announcements/${ann.id}?admin_user_id=${adminId}`, { is_active: !ann.is_active });
    showToast(ann.is_active ? '公告已隐藏' : '公告已发布');
    loadAnnouncements();
  } catch (e) {
    showToast('操作失败', 'error');
  }
};

const confirmDelete = async (ann) => {
  if (!confirm(`确定要删除公告 "${ann.title}" 吗？`)) return;
  try {
    const adminId = localStorage.getItem('user_id');
    await api.delete(`/admin/announcements/${ann.id}?admin_user_id=${adminId}`);
    showToast('公告已删除');
    loadAnnouncements();
  } catch (e) {
    showToast('删除失败', 'error');
  }
};

onMounted(() => { loadAnnouncements(); });
</script>

<style scoped>
/* 中华文化主题 - 公告管理 */
.admin-announcements {
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

.btn:hover { border-color: #2d5a5a; color: #2d5a5a; }
.btn.primary {
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid #d4a84b;
  color: #2d5a5a;
  border-radius: 20px;
}
.btn.primary:hover {
  background: #fff;
  box-shadow: 0 2px 8px rgba(212, 168, 75, 0.3);
}

.table-wrapper {
  background: linear-gradient(180deg, #fffef9 0%, #E6F4EA 100%);
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(212, 168, 75, 0.1);
  border: 1px solid rgba(212, 168, 75, 0.2);
  overflow: hidden;
}

.ann-table { width: 100%; border-collapse: collapse; }
.ann-table th, .ann-table td {
  padding: 14px 16px;
  text-align: left;
  border-bottom: 1px solid rgba(212, 168, 75, 0.1);
}

.ann-table th {
  background: linear-gradient(135deg, rgba(212, 168, 75, 0.1), rgba(212, 168, 75, 0.05));
  font-weight: 600;
  color: #8b7355;
  font-size: 13px;
  letter-spacing: 1px;
}
.ann-table td { font-size: 14px; color: #333; }
.ann-table tr:hover { background: rgba(45, 90, 90, 0.02); }

.title-cell { font-weight: 500; }
.content-cell {
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: #666;
}

.status-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  background: rgba(212, 168, 75, 0.1);
  color: #8b7355;
}

.status-badge.active { background: rgba(45, 90, 90, 0.1); color: #2d5a5a; }
.status-badge.expired { background: rgba(153, 153, 153, 0.1); color: #999; }

tr.expired { background: rgba(0, 0, 0, 0.02); opacity: 0.7; }

.action-btns { display: flex; gap: 8px; }

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

.icon-btn:hover { background: rgba(212, 168, 75, 0.2); color: #d4a84b; }
.icon-btn.danger:hover { background: rgba(220, 53, 69, 0.1); color: #dc3545; }

.empty-row { text-align: center; color: #999; padding: 40px !important; }

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(26, 26, 26, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.modal {
  background: #fffef9;
  border-radius: 12px;
  width: 520px;
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

.modal-header h3 { font-size: 17px; font-weight: 600; color: #1a1a1a; letter-spacing: 1px; margin: 0; }

.close-btn {
  width: 32px; height: 32px;
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

.close-btn:hover { background: rgba(45, 90, 90, 0.1); color: #2d5a5a; }

.modal-body { padding: 24px; }

.form-group { margin-bottom: 18px; }
.form-group label { display: block; font-size: 14px; color: #1a1a1a; margin-bottom: 8px; font-weight: 500; }
.required { color: #dc3545; }

.form-group input[type="text"],
.form-group input[type="datetime-local"],
.form-group input:not([type]),
.form-group textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid rgba(212, 168, 75, 0.3);
  border-radius: 6px;
  font-size: 14px;
  box-sizing: border-box;
  font-family: inherit;
  background: #fff;
  transition: all 0.3s;
}

.form-group input:focus,
.form-group textarea:focus { outline: none; border-color: #d4a84b; box-shadow: 0 0 0 3px rgba(212, 168, 75, 0.1); }

.form-group textarea { resize: vertical; min-height: 120px; }

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.checkbox-label input[type="checkbox"] { width: 16px; height: 16px; cursor: pointer; accent-color: #2d5a5a; }
.checkbox-label span { font-size: 14px; color: #333; }

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

.toast.success { background: rgba(46, 125, 50, 0.1); color: #2e7d32; border-color: rgba(46, 125, 50, 0.2); }
.toast.error { background: rgba(220, 53, 69, 0.1); color: #dc3545; border-color: rgba(220, 53, 69, 0.2); }

@keyframes slideDown {
  from { opacity: 0; transform: translateX(-50%) translateY(-20px); }
  to { opacity: 1; transform: translateX(-50%) translateY(0); }
}
</style>
