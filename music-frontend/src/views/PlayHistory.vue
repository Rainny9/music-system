<template>
  <div class="history-page">
    <div class="page-header">
      <h2>播放历史</h2>
      <button v-if="histories.length > 0" class="btn-clear" @click="clearAll">
        <svg viewBox="0 0 24 24" width="16" height="16">
          <path fill="currentColor" d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
        </svg>
        清空历史
      </button>
    </div>

    <div v-if="loading" class="loading">加载中...</div>

    <div v-else-if="histories.length === 0" class="empty-state">
      <svg viewBox="0 0 24 24" width="64" height="64">
        <path fill="#ccc" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
      </svg>
      <p>暂无播放历史</p>
    </div>

    <div v-else class="history-list">
      <div v-for="item in histories" :key="item.id" class="history-item">
        <div class="song-cover" @click="playSong(item)">
          <img v-if="item.cover_url" :src="item.cover_url" alt="封面" />
          <div v-else class="cover-placeholder">♪</div>
          <div class="play-overlay">
            <svg viewBox="0 0 24 24" width="32" height="32">
              <path fill="#fff" d="M8 5v14l11-7z"/>
            </svg>
          </div>
        </div>
        <div class="song-info">
          <div class="song-title">{{ item.title }}</div>
          <div class="song-meta">
            <span class="artist">{{ item.artist || '未知歌手' }}</span>
            <span class="separator">·</span>
            <span class="played-time">{{ formatTime(item.played_at) }}</span>
          </div>
        </div>
        <div class="song-actions">
          <button class="icon-btn add-btn" @click="openAddToPlaylist(item)" title="添加到歌单">
            <svg viewBox="0 0 24 24" width="18" height="18">
              <path fill="currentColor" d="M14 10H2v2h12v-2zm0-4H2v2h12V6zm4 8v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zM2 16h8v-2H2v2z"/>
            </svg>
          </button>
          <button class="icon-btn" @click="deleteItem(item)" title="删除">
            <svg viewBox="0 0 24 24" width="18" height="18">
              <path fill="currentColor" d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- 添加到歌单弹窗 -->
    <div v-if="showPlaylistModal" class="modal-overlay" @click.self="showPlaylistModal = false">
      <div class="playlist-modal">
        <div class="playlist-modal-header">
          <h3>添加到歌单</h3>
          <button class="close-btn" @click="showPlaylistModal = false">×</button>
        </div>
        <div class="playlist-modal-body">
          <div v-if="userPlaylists.length === 0" class="empty-playlists">
            <p>暂无歌单</p>
            <button class="create-btn" @click="goToPlaylists">创建歌单</button>
          </div>
          <div v-else class="playlist-list">
            <div 
              v-for="playlist in userPlaylists" 
              :key="playlist.id" 
              class="playlist-item"
              @click="addToPlaylist(playlist.id)"
            >
              <div class="playlist-icon">♪</div>
              <div class="playlist-info">
                <div class="playlist-name">{{ playlist.name }}</div>
                <div class="playlist-count">{{ playlist.song_count || 0 }} 首歌曲</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import api from '../api';
import { playSong as playGlobalSong } from '../stores/player';

const router = useRouter();
const histories = ref([]);
const loading = ref(true);
const userId = ref(null);

// 添加到歌单相关
const showPlaylistModal = ref(false);
const userPlaylists = ref([]);
const selectedSongForPlaylist = ref(null);

const formatTime = (dateStr) => {
  const date = new Date(dateStr);
  const now = new Date();
  const diff = now - date;
  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(diff / 3600000);
  const days = Math.floor(diff / 86400000);
  
  if (minutes < 1) return '刚刚';
  if (minutes < 60) return `${minutes}分钟前`;
  if (hours < 24) return `${hours}小时前`;
  if (days < 7) return `${days}天前`;
  return date.toLocaleDateString('zh-CN');
};

const loadHistory = async () => {
  loading.value = true;
  try {
    const res = await api.get(`/users/${userId.value}/history`);
    histories.value = res.data;
  } catch (e) {
    console.error('加载历史失败:', e);
  } finally {
    loading.value = false;
  }
};

const playSong = (song) => {
  playGlobalSong(song);
};

const deleteItem = async (item) => {
  if (!confirm(`确定删除「${item.title}」的播放记录吗？`)) return;
  try {
    // 需要后端提供 history_id
    await api.delete(`/users/${userId.value}/history/${item.id}`);
    histories.value = histories.value.filter(h => h.id !== item.id);
  } catch (e) {
    alert('删除失败');
  }
};

const clearAll = async () => {
  if (!confirm('确定清空所有播放历史吗？')) return;
  try {
    await api.delete(`/users/${userId.value}/history/clear`);
    histories.value = [];
  } catch (e) {
    alert('清空失败');
  }
};

// 打开添加到歌单弹窗
const openAddToPlaylist = async (song) => {
  selectedSongForPlaylist.value = song;
  try {
    const res = await api.get(`/playlists?user_id=${userId.value}`);
    userPlaylists.value = res.data;
  } catch (e) { userPlaylists.value = []; }
  showPlaylistModal.value = true;
};

// 添加歌曲到歌单
const addToPlaylist = async (playlistId) => {
  if (!selectedSongForPlaylist.value) return;
  try {
    await api.post(`/playlists/${playlistId}/songs`, { song_id: selectedSongForPlaylist.value.id });
    alert("已添加到歌单");
    showPlaylistModal.value = false;
  } catch (e) {
    if (e.response?.data?.msg === "song already in playlist") {
      alert("歌曲已在该歌单中");
    } else { alert("添加失败"); }
  }
};

// 跳转到歌单页面
const goToPlaylists = () => {
  showPlaylistModal.value = false;
  router.push("/playlists");
};

onMounted(() => {
  userId.value = localStorage.getItem('user_id');
  if (!userId.value) {
    alert('请先登录');
    router.push('/login');
    return;
  }
  loadHistory();
});
</script>

<style scoped>
/* 播放历史 - 中华风 */
.history-page {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
  min-height: calc(100vh - 140px);
  background: rgba(255, 254, 249, 0.85);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
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

.btn-clear {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: #fffef9;
  border: 1px solid rgba(220, 53, 69, 0.5);
  border-radius: 4px;
  color: #dc3545;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-clear:hover {
  background: #dc3545;
  color: #fff;
  border-color: #dc3545;
}

.loading {
  text-align: center;
  padding: 60px 20px;
  color: #999;
}

.empty-state {
  text-align: center;
  padding: 80px 20px;
  background: rgba(212, 168, 75, 0.03);
  border-radius: 8px;
  border: 1px dashed rgba(212, 168, 75, 0.3);
}

.empty-state svg path {
  fill: rgba(212, 168, 75, 0.5);
}

.empty-state p {
  margin-top: 16px;
  color: #999;
  font-size: 16px;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.history-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 14px;
  background: #fffef9;
  border-radius: 8px;
  transition: all 0.3s;
  border: 1px solid rgba(212, 168, 75, 0.15);
}

.history-item:hover {
  box-shadow: 0 4px 15px rgba(45, 90, 90, 0.1);
  transform: translateY(-2px);
  border-color: rgba(212, 168, 75, 0.3);
}

.song-cover {
  position: relative;
  width: 60px;
  height: 60px;
  border-radius: 4px;
  overflow: hidden;
  cursor: pointer;
  flex-shrink: 0;
  border: 1px solid rgba(212, 168, 75, 0.2);
}

.song-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cover-placeholder {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #2d5a5a, #1e3d3d);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #d4a84b;
  font-size: 24px;
}

.play-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(26, 26, 26, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s;
}

.song-cover:hover .play-overlay {
  opacity: 1;
}

.song-info {
  flex: 1;
  min-width: 0;
}

.song-title {
  font-size: 15px;
  font-weight: 500;
  color: #1a1a1a;
  margin-bottom: 6px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.song-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #999;
}

.separator {
  color: rgba(212, 168, 75, 0.3);
}

.song-actions {
  display: flex;
  gap: 8px;
}

.icon-btn {
  width: 32px;
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
  background: rgba(220, 53, 69, 0.1);
  color: #dc3545;
}

.icon-btn.add-btn:hover {
  background: rgba(212, 168, 75, 0.2);
  color: #d4a84b;
}

/* 弹窗样式 - 中华风 */
.modal-overlay { position: fixed; inset: 0; background: rgba(26,26,26,0.6); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.playlist-modal { background: #fffef9; border-radius: 8px; width: 360px; max-width: 90%; border: 1px solid rgba(212, 168, 75, 0.3); box-shadow: 0 8px 30px rgba(0, 0, 0, 0.2); }
.playlist-modal-header { display: flex; justify-content: space-between; align-items: center; padding: 14px 18px; border-bottom: 1px solid rgba(212, 168, 75, 0.2); background: linear-gradient(90deg, rgba(45, 90, 90, 0.05), transparent); }
.playlist-modal-header h3 { font-size: 16px; font-weight: 600; color: #1a1a1a; margin: 0; letter-spacing: 1px; }
.close-btn { width: 28px; height: 28px; border: none; background: none; font-size: 20px; color: #999; cursor: pointer; transition: all 0.3s; border-radius: 4px; }
.close-btn:hover { background: rgba(45, 90, 90, 0.1); color: #2d5a5a; }
.playlist-modal-body { padding: 16px; max-height: 400px; overflow-y: auto; }
.empty-playlists { text-align: center; padding: 30px 0; }
.empty-playlists p { color: #999; margin-bottom: 16px; }
.create-btn { padding: 10px 24px; background: rgba(255, 255, 255, 0.9); color: #2d5a5a; border: 1px solid #d4a84b; border-radius: 20px; cursor: pointer; transition: all 0.3s; }
.create-btn:hover { background: #fff; box-shadow: 0 2px 8px rgba(212, 168, 75, 0.3); }
.playlist-list { display: flex; flex-direction: column; gap: 8px; }
.playlist-item { display: flex; align-items: center; gap: 12px; padding: 12px; border-radius: 4px; cursor: pointer; transition: all 0.3s; border: 1px solid transparent; }
.playlist-item:hover { background: rgba(212, 168, 75, 0.1); border-color: rgba(212, 168, 75, 0.2); }
.playlist-icon { width: 40px; height: 40px; border-radius: 4px; background: linear-gradient(135deg, rgba(255,255,255,0.4) 0%, #8BA8A8 50%, #7a9999 100%); color: #d4a84b; display: flex; align-items: center; justify-content: center; font-size: 18px; }
.playlist-info { flex: 1; }
.playlist-name { font-size: 14px; color: #1a1a1a; margin-bottom: 2px; }
.playlist-count { font-size: 12px; color: #999; }
</style>
