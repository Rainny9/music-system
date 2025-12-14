<template>
  <div class="favorites-container">
    <!-- 顶部标题栏 -->
    <div class="header">
      <h2>我的收藏</h2>
      <span class="song-count">共 {{ songs.length }} 首</span>
    </div>

    <!-- 歌曲列表表头 -->
    <div class="song-list-header">
      <span class="col-index">#</span>
      <span class="col-title">歌曲</span>
      <span class="col-artist">歌手</span>
      <span class="col-album">专辑</span>
      <span class="col-duration">时长</span>
      <span class="col-actions">操作</span>
    </div>

    <!-- 歌曲列表 -->
    <div class="song-list">
      <div 
        v-for="(song, index) in songs" 
        :key="song.id" 
        class="song-item"
        :class="{ 'playing': playerState.currentSong && playerState.currentSong.id === song.id }"
      >
        <span class="col-index">
          <span class="index-number">{{ index + 1 }}</span>
          <button 
            class="play-btn" 
            @click="play(song)"
            title="播放"
          >
            <svg viewBox="0 0 24 24" class="play-icon">
              <path d="M8 5v14l11-7z" fill="currentColor"/>
            </svg>
          </button>
        </span>
        <span class="col-title">{{ song.title }}</span>
        <span class="col-artist">{{ song.artist || '未知歌手' }}</span>
        <span class="col-album">{{ song.album || '未知专辑' }}</span>
        <span class="col-duration">{{ formatDuration(song.duration) }}</span>
        <span class="col-actions">
          <button class="icon-btn" @click.stop="openAddToPlaylist(song)" title="添加到歌单">
            <svg viewBox="0 0 24 24" width="18" height="18"><path fill="currentColor" d="M14 10H2v2h12v-2zm0-4H2v2h12V6zm4 8v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zM2 16h8v-2H2v2z"/></svg>
          </button>
        </span>
      </div>

      <div v-if="songs.length === 0" class="empty-state">
        <p>暂无收藏歌曲</p>
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
import { ref, onMounted } from "vue";
import api from "../api";
import { useRouter } from "vue-router";
import { playerState, playSong, formatDuration } from "../stores/player";

const router = useRouter();
const songs = ref([]);

// 添加到歌单相关
const showPlaylistModal = ref(false);
const userPlaylists = ref([]);
const selectedSongForPlaylist = ref(null);

const loadFavorites = async () => {
  const userId = localStorage.getItem("user_id");
  if (!userId) {
    alert("请先登录");
    router.push("/login");
    return;
  }
  const res = await api.get(`/users/${userId}/favorites`);
  songs.value = res.data;
};

const play = (song) => {
  playSong(song);
};

// 打开添加到歌单弹窗
const openAddToPlaylist = async (song) => {
  const uid = localStorage.getItem("user_id");
  if (!uid) { alert("请先登录"); router.push("/login"); return; }
  selectedSongForPlaylist.value = song;
  try {
    const res = await api.get(`/playlists?user_id=${uid}`);
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

onMounted(loadFavorites);
</script>

<style scoped>
/* 我的收藏 - 中华风 */
.favorites-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  padding-bottom: 100px;
  min-height: calc(100vh - 140px);
  background: rgba(255, 254, 249, 0.85);
}

.header {
  display: flex;
  align-items: baseline;
  gap: 15px;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(212, 168, 75, 0.2);
}

.header h2 {
  margin: 0;
  font-size: 24px;
  color: #1a1a1a;
  letter-spacing: 2px;
  position: relative;
  padding-left: 14px;
}

.header h2::before {
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

.song-count {
  color: #999;
  font-size: 14px;
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

.song-item:hover .index-number {
  display: none;
}

.song-item:hover .play-btn {
  display: flex;
}

.song-item.playing {
  background: rgba(45, 90, 90, 0.05);
}

.song-item.playing .col-title,
.song-item.playing .col-artist {
  color: #2d5a5a;
}

.col-index {
  width: 50px;
  text-align: center;
  color: #999;
  position: relative;
}

.index-number {
  font-size: 14px;
}

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
  padding: 0;
  position: relative;
  transition: all 0.3s;
}

.play-btn:hover {
  transform: scale(1.1);
}

.play-btn:hover::after {
  content: '播放';
  position: absolute;
  top: -25px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(26,26,26,0.8);
  color: #d4a84b;
  padding: 3px 8px;
  border-radius: 3px;
  font-size: 12px;
  white-space: nowrap;
}

.play-icon {
  width: 20px;
  height: 20px;
}

.col-title {
  flex: 2;
  font-size: 14px;
  color: #1a1a1a;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  padding-right: 15px;
}

.col-artist {
  flex: 1.5;
  font-size: 13px;
  color: #666;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  padding-right: 15px;
}

.col-album {
  flex: 1.5;
  font-size: 13px;
  color: #666;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  padding-right: 15px;
}

.col-duration {
  width: 60px;
  text-align: right;
  font-size: 13px;
  color: #999;
}

.empty-state {
  padding: 60px 20px;
  text-align: center;
  color: #999;
  background: rgba(212, 168, 75, 0.03);
  border-radius: 4px;
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

.icon-btn:hover {
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
.create-btn { padding: 10px 24px; background: linear-gradient(135deg, rgba(255,255,255,0.4) 0%, #8BA8A8 50%, #7a9999 100%); color: #d4a84b; border: 1px solid #d4a84b; border-radius: 4px; cursor: pointer; transition: all 0.3s; }
.create-btn:hover { background: linear-gradient(135deg, #4a7c7c, #2d5a5a); box-shadow: 0 4px 12px rgba(45, 90, 90, 0.3); }
.playlist-list { display: flex; flex-direction: column; gap: 8px; }
.playlist-item { display: flex; align-items: center; gap: 12px; padding: 12px; border-radius: 4px; cursor: pointer; transition: all 0.3s; border: 1px solid transparent; }
.playlist-item:hover { background: rgba(212, 168, 75, 0.1); border-color: rgba(212, 168, 75, 0.2); }
.playlist-icon { width: 40px; height: 40px; border-radius: 4px; background: linear-gradient(135deg, rgba(255,255,255,0.4) 0%, #8BA8A8 50%, #7a9999 100%); color: #d4a84b; display: flex; align-items: center; justify-content: center; font-size: 18px; }
.playlist-info { flex: 1; }
.playlist-name { font-size: 14px; color: #1a1a1a; margin-bottom: 2px; }
.playlist-count { font-size: 12px; color: #999; }
</style>
