<template>
  <div class="playlist-detail-page">
    <!-- 返回按钮 -->
    <button class="back-btn" @click="goBack">
      <svg viewBox="0 0 24 24" width="20" height="20">
        <path fill="currentColor" d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z"/>
      </svg>
      返回
    </button>

    <div v-if="loading" class="loading">加载中...</div>

    <template v-else>
      <!-- 歌单信息 -->
      <div class="playlist-header">
        <div class="playlist-cover">
          <div class="cover-placeholder">
            <svg viewBox="0 0 24 24" width="64" height="64">
              <path fill="#fff" d="M15 6H3v2h12V6zm0 4H3v2h12v-2zM3 16h8v-2H3v2zM17 6v8.18c-.31-.11-.65-.18-1-.18-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3V8h3V6h-5z"/>
            </svg>
          </div>
        </div>
        <div class="playlist-info">
          <h2>{{ playlist.name }}</h2>
          <p class="description">{{ playlist.description || '暂无简介' }}</p>
          <p class="meta">{{ songs.length }} 首歌曲</p>
          <div class="action-row">
            <button class="btn primary" @click="playAll" :disabled="songs.length === 0">
              <svg viewBox="0 0 24 24" width="16" height="16">
                <path fill="currentColor" d="M8 5v14l11-7z"/>
              </svg>
              播放全部
            </button>
          </div>
        </div>
      </div>

      <!-- 歌曲列表 -->
      <div class="song-list-header">
        <span class="col-index">#</span>
        <span class="col-title">歌曲</span>
        <span class="col-artist">歌手</span>
        <span class="col-duration">时长</span>
        <span class="col-actions">操作</span>
      </div>

      <div class="song-list">
        <div 
          v-for="(song, index) in songs" 
          :key="song.id" 
          class="song-item"
          :class="{ playing: playerState.currentSong?.id === song.id }"
        >
          <span class="col-index">
            <span class="index-number">{{ index + 1 }}</span>
            <button class="play-btn" @click="play(song)">
              <svg viewBox="0 0 24 24" width="20" height="20">
                <path fill="currentColor" d="M8 5v14l11-7z"/>
              </svg>
            </button>
          </span>
          <span class="col-title">{{ song.title }}</span>
          <span class="col-artist">{{ song.artist || '未知歌手' }}</span>
          <span class="col-duration">{{ formatDuration(song.duration) }}</span>
          <span class="col-actions">
            <button class="icon-btn danger" @click="removeSong(song)" title="从歌单移除">
              <svg viewBox="0 0 24 24" width="18" height="18">
                <path fill="currentColor" d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
              </svg>
            </button>
          </span>
        </div>

        <div v-if="songs.length === 0" class="empty-state">
          <p>歌单暂无歌曲</p>
          <button class="btn" @click="goHome">去添加歌曲</button>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import api from '../api';
import { playerState, playSong, formatDuration } from '../stores/player';

const route = useRoute();
const router = useRouter();
const playlistId = Number(route.params.id);

const playlist = ref({});
const songs = ref([]);
const loading = ref(true);

const loadPlaylist = async () => {
  loading.value = true;
  try {
    const res = await api.get(`/playlists/${playlistId}`);
    playlist.value = res.data;
    songs.value = res.data.songs || [];
  } catch (e) {
    alert('加载歌单失败');
    router.push('/playlists');
  } finally {
    loading.value = false;
  }
};

const goBack = () => router.back();
const goHome = () => router.push('/');

const play = (song) => {
  playSong(song, songs.value);
};

const playAll = () => {
  if (songs.value.length > 0) {
    playSong(songs.value[0], songs.value);
  }
};

const removeSong = async (song) => {
  if (!confirm(`确定从歌单移除「${song.title}」吗？`)) return;
  try {
    await api.delete(`/playlists/${playlistId}/songs/${song.id}`);
    songs.value = songs.value.filter(s => s.id !== song.id);
  } catch (e) {
    alert('移除失败');
  }
};

onMounted(loadPlaylist);
</script>

<style scoped>
/* 歌单详情 - 中华风 */
.playlist-detail-page {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
  padding-bottom: 100px;
  min-height: calc(100vh - 140px);
  background: rgba(255, 254, 249, 0.85);
}

.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  margin-bottom: 16px;
  background: #fffef9;
  border: 1px solid rgba(212, 168, 75, 0.3);
  border-radius: 4px;
  font-size: 14px;
  color: #666;
  cursor: pointer;
  transition: all 0.3s;
}

.back-btn:hover {
  background: rgba(212, 168, 75, 0.1);
  color: #d4a84b;
  border-color: #d4a84b;
}

.loading {
  text-align: center;
  padding: 60px 20px;
  color: #999;
}

.playlist-header {
  display: flex;
  gap: 24px;
  background: linear-gradient(135deg, #fffef9, rgba(212, 168, 75, 0.05));
  padding: 24px;
  border-radius: 8px;
  margin-bottom: 24px;
  border: 1px solid rgba(212, 168, 75, 0.2);
  position: relative;
  overflow: hidden;
}

.playlist-header::before {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 250px;
  height: 250px;
  background: radial-gradient(circle, rgba(45, 90, 90, 0.03) 0%, transparent 70%);
  pointer-events: none;
}

.playlist-cover {
  width: 180px;
  height: 180px;
  border-radius: 4px;
  overflow: hidden;
  flex-shrink: 0;
  border: 2px solid #d4a84b;
  box-shadow: 0 8px 25px rgba(45, 90, 90, 0.15);
}

.cover-placeholder {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, rgba(255,255,255,0.4) 0%, #8BA8A8 50%, #7a9999 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}

.playlist-info {
  flex: 1;
  position: relative;
  z-index: 1;
}

.playlist-info h2 {
  font-size: 24px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0 0 12px;
  letter-spacing: 1px;
}

.description {
  font-size: 14px;
  color: #666;
  margin: 0 0 8px;
  line-height: 1.6;
}

.meta {
  font-size: 13px;
  color: #999;
  margin: 0 0 16px;
}

.action-row {
  display: flex;
  gap: 12px;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 10px 24px;
  border: 1px solid rgba(212, 168, 75, 0.3);
  border-radius: 4px;
  background: #fffef9;
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
  background: linear-gradient(135deg, rgba(255,255,255,0.4) 0%, #8BA8A8 50%, #7a9999 100%);
  border-color: #d4a84b;
  color: #d4a84b;
}

.btn.primary:hover {
  background: linear-gradient(135deg, rgba(255,255,255,0.5) 0%, #9ab8b8 50%, #8BA8A8 100%);
  box-shadow: 0 4px 12px rgba(139, 168, 168, 0.4);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.song-list-header {
  display: flex;
  align-items: center;
  padding: 12px 15px;
  background: rgba(212, 168, 75, 0.08);
  border-radius: 4px;
  font-size: 13px;
  color: #888;
  margin-bottom: 5px;
  border: 1px solid rgba(212, 168, 75, 0.1);
}

.song-list {
  background: #fffef9;
  border-radius: 4px;
  border: 1px solid rgba(212, 168, 75, 0.15);
}

.song-item {
  display: flex;
  align-items: center;
  padding: 12px 15px;
  border-bottom: 1px solid rgba(212, 168, 75, 0.1);
  transition: all 0.3s;
}

.song-item:last-child {
  border-bottom: none;
}

.song-item:hover {
  background: rgba(212, 168, 75, 0.05);
}

.song-item:hover .index-number { display: none; }
.song-item:hover .play-btn { display: flex; }

.song-item.playing {
  background: rgba(45, 90, 90, 0.05);
}

.song-item.playing .col-title {
  color: #2d5a5a;
}

.col-index {
  width: 50px;
  text-align: center;
  color: #999;
}

.index-number { font-size: 14px; }

.play-btn {
  display: none;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border: none;
  background: transparent;
  cursor: pointer;
  color: #2d5a5a;
  transition: all 0.3s;
}

.play-btn:hover {
  transform: scale(1.1);
}

.col-title {
  flex: 2;
  font-size: 14px;
  color: #1a1a1a;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.col-artist {
  flex: 1.5;
  font-size: 13px;
  color: #666;
}

.col-duration {
  width: 60px;
  text-align: right;
  font-size: 13px;
  color: #999;
}

.col-actions {
  width: 60px;
  display: flex;
  justify-content: center;
}

.icon-btn {
  width: 28px;
  height: 28px;
  border: none;
  background: transparent;
  cursor: pointer;
  color: #999;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
}

.icon-btn.danger:hover {
  color: #dc3545;
}

.empty-state {
  padding: 60px 20px;
  text-align: center;
  color: #999;
  background: rgba(212, 168, 75, 0.03);
  border-radius: 4px;
}

.empty-state p {
  margin-bottom: 16px;
}

@media (max-width: 768px) {
  .playlist-header { flex-direction: column; align-items: center; text-align: center; }
  .playlist-cover { width: 150px; height: 150px; }
  .action-row { justify-content: center; }
}
</style>
