<template>
  <div class="admin-artists-container">
    <div class="page-header">
      <h2>🎤 歌手管理</h2>
      <button class="add-btn" @click="openAddModal">+ 添加歌手</button>
    </div>

    <div class="artists-table">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>头像</th>
            <th>歌手名</th>
            <th>歌曲数</th>
            <th>粉丝数</th>
            <th>简介</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="artist in artists" :key="artist.id">
            <td>{{ artist.id }}</td>
            <td>
              <div class="avatar-cell">
                <img v-if="artist.avatar_url" :src="artist.avatar_url" alt="" />
                <span v-else class="avatar-placeholder">{{ artist.name?.charAt(0) }}</span>
              </div>
            </td>
            <td>{{ artist.name }}</td>
            <td>{{ artist.song_count || 0 }}</td>
            <td>{{ artist.follower_count || 0 }}</td>
            <td class="desc-cell">{{ artist.description || '-' }}</td>
            <td>
              <div class="action-btns">
                <button class="btn-edit" @click="openEditModal(artist)">编辑</button>
                <button class="btn-avatar" @click="openAvatarModal(artist)">上传头像</button>
                <button class="btn-delete" @click="deleteArtist(artist)">删除</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-if="artists.length === 0" class="empty-state">暂无歌手数据</div>
    </div>

    <!-- 添加/编辑弹窗 -->
    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal-content">
        <div class="modal-header">
          <h3>{{ isEdit ? '编辑歌手' : '添加歌手' }}</h3>
          <button class="close-btn" @click="showModal = false">×</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>歌手名称 *</label>
            <input v-model="form.name" placeholder="请输入歌手名称" />
          </div>
          <div class="form-group">
            <label>简介</label>
            <textarea v-model="form.description" placeholder="请输入歌手简介" rows="4"></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-cancel" @click="showModal = false">取消</button>
          <button class="btn-submit" @click="submitForm">{{ isEdit ? '保存' : '添加' }}</button>
        </div>
      </div>
    </div>

    <!-- 上传头像弹窗 -->
    <div v-if="showAvatarModal" class="modal-overlay" @click.self="showAvatarModal = false">
      <div class="modal-content">
        <div class="modal-header">
          <h3>上传头像 - {{ currentArtist?.name }}</h3>
          <button class="close-btn" @click="showAvatarModal = false">×</button>
        </div>
        <div class="modal-body">
          <div class="avatar-preview">
            <img v-if="currentArtist?.avatar_url" :src="currentArtist.avatar_url" alt="" />
            <span v-else class="preview-placeholder">{{ currentArtist?.name?.charAt(0) }}</span>
          </div>
          <input type="file" ref="avatarInput" accept="image/*" @change="onAvatarSelect" />
        </div>
        <div class="modal-footer">
          <button class="btn-cancel" @click="showAvatarModal = false">取消</button>
          <button class="btn-submit" @click="uploadAvatar" :disabled="!selectedFile">上传</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '../../api';

const artists = ref([]);
const showModal = ref(false);
const showAvatarModal = ref(false);
const isEdit = ref(false);
const currentArtist = ref(null);
const selectedFile = ref(null);
const avatarInput = ref(null);

const form = ref({
  name: '',
  description: ''
});

const adminUserId = localStorage.getItem('user_id');

const loadArtists = async () => {
  try {
    const res = await api.get('/admin/artists', { params: { admin_user_id: adminUserId } });
    artists.value = res.data;
  } catch (e) {
    console.error('加载歌手失败', e);
    alert('加载失败：' + (e.response?.data?.msg || e.message));
  }
};

const openAddModal = () => {
  isEdit.value = false;
  form.value = { name: '', description: '' };
  showModal.value = true;
};

const openEditModal = (artist) => {
  isEdit.value = true;
  currentArtist.value = artist;
  form.value = { name: artist.name, description: artist.description || '' };
  showModal.value = true;
};

const openAvatarModal = (artist) => {
  currentArtist.value = artist;
  selectedFile.value = null;
  if (avatarInput.value) avatarInput.value.value = '';
  showAvatarModal.value = true;
};

const onAvatarSelect = (e) => {
  selectedFile.value = e.target.files[0];
};

const submitForm = async () => {
  if (!form.value.name.trim()) {
    alert('请输入歌手名称');
    return;
  }
  try {
    if (isEdit.value) {
      await api.put(`/admin/artists/${currentArtist.value.id}?admin_user_id=${adminUserId}`, form.value);
      alert('修改成功');
    } else {
      await api.post(`/admin/artists?admin_user_id=${adminUserId}`, form.value);
      alert('添加成功');
    }
    showModal.value = false;
    loadArtists();
  } catch (e) {
    alert('操作失败：' + (e.response?.data?.msg || e.message));
  }
};

const uploadAvatar = async () => {
  if (!selectedFile.value) return;
  const formData = new FormData();
  formData.append('avatar', selectedFile.value);
  try {
    await api.post(`/admin/artists/${currentArtist.value.id}/avatar?admin_user_id=${adminUserId}`, formData);
    alert('上传成功');
    showAvatarModal.value = false;
    loadArtists();
  } catch (e) {
    alert('上传失败：' + (e.response?.data?.msg || e.message));
  }
};

const deleteArtist = async (artist) => {
  if (!confirm(`确定删除歌手「${artist.name}」吗？该歌手下的歌曲将不再关联此歌手。`)) return;
  try {
    await api.delete(`/admin/artists/${artist.id}?admin_user_id=${adminUserId}`);
    alert('删除成功');
    loadArtists();
  } catch (e) {
    alert('删除失败：' + (e.response?.data?.msg || e.message));
  }
};

onMounted(() => {
  loadArtists();
});
</script>

<style scoped>
.admin-artists-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-header h2 {
  font-size: 22px;
  color: #2d5a5a;
  margin: 0;
}

.add-btn {
  padding: 10px 20px;
  background: linear-gradient(135deg, #2d5a5a, #3d7a7a);
  color: #fff;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
}

.add-btn:hover {
  background: linear-gradient(135deg, #3d7a7a, #4d8a8a);
}

.artists-table {
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 14px 16px;
  text-align: left;
  border-bottom: 1px solid #f0f0f0;
}

th {
  background: #f8f8f8;
  font-weight: 600;
  color: #666;
  font-size: 13px;
}

td {
  font-size: 14px;
  color: #333;
}

.avatar-cell {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  overflow: hidden;
  background: linear-gradient(135deg, #8BA8A8, #7a9999);
}

.avatar-cell img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 16px;
  font-weight: 600;
}

.desc-cell {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: #999;
}

.action-btns {
  display: flex;
  gap: 8px;
}

.action-btns button {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
}

.btn-edit {
  background: #e6f7ff;
  color: #1890ff;
}

.btn-avatar {
  background: #fff7e6;
  color: #fa8c16;
}

.btn-delete {
  background: #fff1f0;
  color: #ff4d4f;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: #999;
}

/* 弹窗样式 */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: #fff;
  border-radius: 12px;
  width: 450px;
  max-width: 90%;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #f0f0f0;
}

.modal-header h3 {
  margin: 0;
  font-size: 16px;
  color: #333;
}

.close-btn {
  border: none;
  background: none;
  font-size: 20px;
  color: #999;
  cursor: pointer;
}

.modal-body {
  padding: 20px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  color: #666;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 6px;
  font-size: 14px;
  box-sizing: border-box;
}

.form-group input:focus,
.form-group textarea:focus {
  border-color: #d4a84b;
  outline: none;
}

.avatar-preview {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  overflow: hidden;
  background: linear-gradient(135deg, #8BA8A8, #7a9999);
  margin: 0 auto 20px;
}

.avatar-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.preview-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 36px;
  font-weight: 600;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 20px;
  border-top: 1px solid #f0f0f0;
}

.btn-cancel {
  padding: 8px 20px;
  border: 1px solid #d9d9d9;
  background: #fff;
  border-radius: 6px;
  cursor: pointer;
}

.btn-submit {
  padding: 8px 20px;
  border: none;
  background: #d4a84b;
  color: #fff;
  border-radius: 6px;
  cursor: pointer;
}

.btn-submit:disabled {
  background: #ccc;
  cursor: not-allowed;
}
</style>
