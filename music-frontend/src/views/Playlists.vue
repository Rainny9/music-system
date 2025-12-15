<template>
  <div class="playlists-page">
    <div class="page-header">
      <h2>我的歌单</h2>
      <button class="btn-create" @click="showCreateModal = true">
        <svg viewBox="0 0 24 24" width="16" height="16">
          <path fill="currentColor" d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
        </svg>
        创建歌单
      </button>
    </div>

    <div v-if="loading" class="loading">加载中...</div>

    <div v-else-if="playlists.length === 0" class="empty-state">
      <svg viewBox="0 0 24 24" width="64" height="64">
        <path fill="#ccc" d="M15 6H3v2h12V6zm0 4H3v2h12v-2zM3 16h8v-2H3v2zM17 6v8.18c-.31-.11-.65-.18-1-.18-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3V8h3V6h-5z"/>
      </svg>
      <p>还没有创建歌单</p>
      <button class="btn-primary" @click="showCreateModal = true">创建第一个歌单</button>
    </div>

    <div v-else class="playlists-grid">
      <div v-for="playlist in playlists" :key="playlist.id" class="playlist-card" @click="viewPlaylist(playlist)">
        <div class="playlist-cover">
          <img v-if="playlist.cover_url" :src="playlist.cover_url" alt="封面" />
          <div v-else class="cover-placeholder">
            <svg viewBox="0 0 24 24" width="48" height="48">
              <path fill="#fff" d="M15 6H3v2h12V6zm0 4H3v2h12v-2zM3 16h8v-2H3v2zM17 6v8.18c-.31-.11-.65-.18-1-.18-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3V8h3V6h-5z"/>
            </svg>
          </div>
          <div class="playlist-overlay">
            <button class="btn-play" @click.stop="playPlaylist(playlist)">
              <svg viewBox="0 0 24 24" width="24" height="24">
                <path fill="#fff" d="M8 5v14l11-7z"/>
              </svg>
            </button>
          </div>
        </div>
        <div class="playlist-info">
          <div class="playlist-name">{{ playlist.name }}</div>
          <div class="playlist-count">{{ playlist.song_count }} 首歌曲</div>
        </div>
        <div class="playlist-actions" @click.stop>
          <button class="icon-btn" @click="editPlaylist(playlist)" title="编辑">
            <svg viewBox="0 0 24 24" width="16" height="16">
              <path fill="currentColor" d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/>
            </svg>
          </button>
          <button class="icon-btn danger" @click="deletePlaylist(playlist)" title="删除">
            <svg viewBox="0 0 24 24" width="16" height="16">
              <path fill="currentColor" d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- 创建/编辑歌单弹窗 -->
    <div v-if="showCreateModal || showEditModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal">
        <div class="modal-header">
          <h3>{{ showEditModal ? '编辑歌单' : '创建歌单' }}</h3>
          <button class="close-btn" @click="closeModal">×</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>歌单名称 <span class="required">*</span></label>
            <input v-model="form.name" placeholder="请输入歌单名称" maxlength="50" />
          </div>
          <div class="form-group">
            <label>简介</label>
            <textarea v-model="form.description" placeholder="请输入歌单简介" rows="4"></textarea>
          </div>
          <div class="form-group">
            <label class="checkbox-label">
              <input type="checkbox" v-model="form.is_public" />
              <span>公开歌单</span>
            </label>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn" @click="closeModal">取消</button>
          <button class="btn primary" @click="savePlaylist">{{ showEditModal ? '保存' : '创建' }}</button>
        </div>
      </div>
    </div>

    <!-- Toast -->
    <div v-if="toast.show" class="toast" :class="toast.type">{{ toast.message }}</div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import api from '../api';

const router = useRouter();
const playlists = ref([]);
const loading = ref(true);
const userId = ref(null);
const showCreateModal = ref(false);
const showEditModal = ref(false);
const form = ref({ id: null, name: '', description: '', is_public: true });
const toast = ref({ show: false, message: '', type: 'success' });

const showToast = (message, type = 'success') => {
  toast.value = { show: true, message, type };
  setTimeout(() => { toast.value.show = false; }, 3000);
};

const loadPlaylists = async () => {
  loading.value = true;
  try {
    const res = await api.get(`/playlists?user_id=${userId.value}`);
    playlists.value = res.data;
  } catch (e) {
    showToast('加载歌单失败', 'error');
  } finally {
    loading.value = false;
  }
};

const viewPlaylist = (playlist) => {
  router.push(`/playlists/${playlist.id}`);
};

const playPlaylist = async (playlist) => {
  // TODO: 播放歌单中的所有歌曲
  showToast('播放功能开发中');
};

const editPlaylist = (playlist) => {
  form.value = {
    id: playlist.id,
    name: playlist.name,
    description: playlist.description || '',
    is_public: playlist.is_public !== false
  };
  showEditModal.value = true;
};

const deletePlaylist = async (playlist) => {
  if (!confirm(`确定删除歌单「${playlist.name}」吗？`)) return;
  try {
    await api.delete(`/playlists/${playlist.id}`, {
      data: { user_id: userId.value }
    });
    showToast('歌单已删除');
    loadPlaylists();
  } catch (e) {
    showToast('删除失败', 'error');
  }
};

const savePlaylist = async () => {
  if (!form.value.name.trim()) {
    showToast('请输入歌单名称', 'error');
    return;
  }

  try {
    if (showEditModal.value) {
      await api.put(`/playlists/${form.value.id}`, {
        ...form.value,
        user_id: userId.value
      });
      showToast('歌单已更新');
    } else {
      await api.post('/playlists', {
        ...form.value,
        user_id: userId.value
      });
      showToast('歌单已创建');
    }
    closeModal();
    loadPlaylists();
  } catch (e) {
    const data = e.response?.data;
    if (data?.reason) {
      showToast(`${data.msg}：${data.reason}`, 'error');
    } else {
      showToast(data?.msg || '操作失败', 'error');
    }
  }
};

const closeModal = () => {
  showCreateModal.value = false;
  showEditModal.value = false;
  form.value = { id: null, name: '', description: '', is_public: true };
};

onMounted(() => {
  userId.value = localStorage.getItem('user_id');
  if (!userId.value) {
    alert('请先登录');
    router.push('/login');
    return;
  }
  loadPlaylists();
});
</script>

<style scoped>
/* 歌单页 - 中华风 */
.playlists-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  min-height: calc(100vh - 140px);
  background: rgba(255, 254, 249, 0.85);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 28px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(212, 168, 75, 0.2);
}

.page-header h2 {
  font-size: 24px;
  font-weight: 600;
  color: #1a1a1a;
  letter-spacing: 2px;
  position: relative;
  padding-left: 14px;
}

.page-header h2::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 24px;
  background: linear-gradient(180deg, #2d5a5a, #d4a84b);
  border-radius: 2px;
}

.btn-create {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 20px;
  background: rgba(255, 255, 255, 0.9);
  color: #2d5a5a;
  border: 1px solid #d4a84b;
  border-radius: 20px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
  letter-spacing: 1px;
}

.btn-create:hover {
  background: #fff;
  box-shadow: 0 2px 8px rgba(212, 168, 75, 0.3);
}

.loading {
  text-align: center;
  padding: 60px 20px;
  color: #999;
}

.empty-state {
  text-align: center;
  padding: 80px 20px;
  background: #fffef9;
  border-radius: 12px;
  border: 1px dashed rgba(212, 168, 75, 0.3);
}

.empty-state svg path {
  fill: rgba(212, 168, 75, 0.5);
}

.empty-state p {
  margin: 16px 0 24px;
  color: #999;
  font-size: 16px;
}

.btn-primary {
  padding: 12px 32px;
  background: rgba(255, 255, 255, 0.9);
  color: #2d5a5a;
  border: 1px solid #d4a84b;
  border-radius: 20px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-primary:hover {
  background: #fff;
  box-shadow: 0 2px 8px rgba(212, 168, 75, 0.3);
}

.playlists-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
}

.playlist-card {
  background: linear-gradient(180deg, #fffef9 0%, #E6F4EA 100%);
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s;
  border: 1px solid rgba(212, 168, 75, 0.15);
}

.playlist-card:hover {
  box-shadow: 0 8px 25px rgba(45, 90, 90, 0.12);
  transform: translateY(-4px);
  border-color: rgba(212, 168, 75, 0.3);
}

.playlist-cover {
  position: relative;
  width: 100%;
  padding-top: 100%;
  overflow: hidden;
}

.playlist-cover img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cover-placeholder {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, rgba(255,255,255,0.4) 0%, #8BA8A8 50%, #7a9999 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}

.playlist-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(26, 26, 26, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s;
}

.playlist-card:hover .playlist-overlay {
  opacity: 1;
}

.btn-play {
  width: 56px;
  height: 56px;
  border: 2px solid #d4a84b;
  background: rgba(45, 90, 90, 0.9);
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
}

.btn-play:hover {
  background: #2d5a5a;
  transform: scale(1.1);
  box-shadow: 0 4px 15px rgba(45, 90, 90, 0.4);
}

.playlist-info {
  padding: 12px;
  background: linear-gradient(180deg, transparent, rgba(212, 168, 75, 0.05));
}

.playlist-name {
  font-size: 15px;
  font-weight: 500;
  color: #1a1a1a;
  margin-bottom: 6px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.playlist-count {
  font-size: 13px;
  color: #999;
}

.playlist-actions {
  display: flex;
  gap: 8px;
  padding: 0 12px 12px;
}

.icon-btn {
  flex: 1;
  height: 32px;
  border: none;
  background: rgba(212, 168, 75, 0.1);
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
  transition: all 0.3s;
}

.icon-btn:hover {
  background: rgba(212, 168, 75, 0.2);
  color: #d4a84b;
}

.icon-btn.danger:hover {
  background: rgba(220, 53, 69, 0.1);
  color: #dc3545;
}

/* Modal - 中华风 */
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
  z-index: 1000;
}

.modal {
  background: #fffef9;
  border-radius: 8px;
  width: 480px;
  max-width: 90%;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(212, 168, 75, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid rgba(212, 168, 75, 0.2);
  background: linear-gradient(90deg, rgba(45, 90, 90, 0.05), transparent);
}

.modal-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: #1a1a1a;
  letter-spacing: 1px;
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
  transition: all 0.3s;
}

.close-btn:hover {
  background: rgba(45, 90, 90, 0.1);
  color: #2d5a5a;
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

.required {
  color: #dc3545;
}

.form-group input[type="text"],
.form-group input:not([type]),
.form-group textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid rgba(212, 168, 75, 0.3);
  border-radius: 4px;
  font-size: 14px;
  box-sizing: border-box;
  font-family: inherit;
  background: #fff;
  transition: all 0.3s;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #d4a84b;
  box-shadow: 0 0 0 2px rgba(212, 168, 75, 0.1);
}

.form-group textarea {
  resize: vertical;
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

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 16px 20px;
  border-top: 1px solid rgba(212, 168, 75, 0.2);
}

.btn {
  padding: 8px 20px;
  border: 1px solid rgba(212, 168, 75, 0.3);
  border-radius: 4px;
  background: #fff;
  color: #666;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn:hover {
  border-color: #d4a84b;
  color: #d4a84b;
}

.btn.primary {
  background: rgba(255, 255, 255, 0.9);
  border-color: #d4a84b;
  color: #2d5a5a;
  border-radius: 20px;
}

.btn.primary:hover {
  background: #fff;
  box-shadow: 0 2px 8px rgba(212, 168, 75, 0.3);
}

/* Toast - 中华风 */
.toast {
  position: fixed;
  top: 80px;
  left: 50%;
  transform: translateX(-50%);
  padding: 12px 24px;
  border-radius: 4px;
  font-size: 14px;
  z-index: 2000;
  animation: slideDown 0.3s ease;
  border: 1px solid;
}

.toast.success {
  background: linear-gradient(135deg, rgba(212, 168, 75, 0.1), rgba(212, 168, 75, 0.05));
  color: #8b7355;
  border-color: rgba(212, 168, 75, 0.3);
}

.toast.error {
  background: linear-gradient(135deg, rgba(220, 53, 69, 0.1), rgba(220, 53, 69, 0.05));
  color: #dc3545;
  border-color: rgba(220, 53, 69, 0.3);
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
