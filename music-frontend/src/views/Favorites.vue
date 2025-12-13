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
      </div>

      <div v-if="songs.length === 0" class="empty-state">
        <p>暂无收藏歌曲</p>
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

onMounted(loadFavorites);
</script>

<style scoped>
.favorites-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  padding-bottom: 100px;
  background: #fafafa;
  min-height: 100vh;
}

.header {
  display: flex;
  align-items: baseline;
  gap: 15px;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #e5e5e5;
}

.header h2 {
  margin: 0;
  font-size: 24px;
  color: #333;
}

.song-count {
  color: #999;
  font-size: 14px;
}

.song-list-header {
  display: flex;
  align-items: center;
  padding: 12px 15px;
  background: #f5f5f5;
  border-radius: 4px;
  font-size: 13px;
  color: #888;
  margin-bottom: 5px;
}

.song-list {
  background: #fff;
  border-radius: 4px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

.song-item {
  display: flex;
  align-items: center;
  padding: 12px 15px;
  border-bottom: 1px solid #f0f0f0;
  transition: background 0.2s;
}

.song-item:last-child {
  border-bottom: none;
}

.song-item:hover {
  background: #f9f9f9;
}

.song-item:hover .index-number {
  display: none;
}

.song-item:hover .play-btn {
  display: flex;
}

.song-item.playing {
  background: #f0fff0;
}

.song-item.playing .col-title,
.song-item.playing .col-artist {
  color: #31c27c;
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
  color: #31c27c;
  padding: 0;
  position: relative;
}

.play-btn:hover::after {
  content: '播放';
  position: absolute;
  top: -25px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0,0,0,0.7);
  color: #fff;
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
  color: #333;
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
}

</style>
