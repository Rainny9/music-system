<template>
  <div class="search-container">
    <!-- 搜索框区域 -->
    <div class="search-header">
      <div class="search-box-large">
        <input
          v-model="searchKeyword"
          class="search-input-large"
          placeholder="搜索歌曲 / 歌手 / 标签"
          @keyup.enter="doSearch"
        />
        <button class="search-btn-large" @click="doSearch">
          <svg viewBox="0 0 24 24" width="20" height="20">
            <path fill="currentColor" d="M15.5 14h-.79l-.28-.27A6.471 6.471 0 0 0 16 9.5 6.5 6.5 0 1 0 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>
          </svg>
        </button>
      </div>
      <div class="hot-search">
        热门搜索：
        <span class="hot-tag" @click="quickSearch('流行')">流行</span>
        <span class="hot-tag" @click="quickSearch('伤感')">伤感</span>
        <span class="hot-tag" @click="quickSearch('经典')">经典</span>
      </div>
    </div>

    <!-- 搜索结果信息 -->
    <div class="result-info" v-if="keyword">
      <span>搜索 "<em>{{ keyword }}</em>" 找到 {{ songs.length }} 首相关歌曲</span>
    </div>

    <!-- 分类标签 -->
    <div class="tabs">
      <span class="tab active">单曲</span>
      <span class="tab">专辑</span>
      <span class="tab">歌手</span>
      <span class="tab">歌单</span>
    </div>

    <!-- 操作按钮 -->
    <div class="action-bar">
      <button class="action-btn primary" @click="playAll">
        <svg viewBox="0 0 24 24" width="16" height="16">
          <path fill="currentColor" d="M8 5v14l11-7z"/>
        </svg>
        播放全部
      </button>
    </div>

    <!-- 歌曲列表表头 -->
    <div class="song-list-header">
      <span class="col-index"></span>
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
        <span class="col-title">
          <span v-html="highlightKeyword(song.title)"></span>
          <span v-if="song.isExactMatch" class="exact-badge">完全匹配</span>
        </span>
        <span class="col-artist">{{ song.artist || '未知歌手' }}</span>
        <span class="col-album">{{ song.album || '未知专辑' }}</span>
        <span class="col-duration">{{ formatDuration(song.duration) }}</span>
        <span class="col-actions">
          <button class="icon-btn" @click.stop="openAddToPlaylist(song)" title="添加到歌单">
            <svg viewBox="0 0 24 24" width="18" height="18"><path fill="currentColor" d="M14 10H2v2h12v-2zm0-4H2v2h12V6zm4 8v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zM2 16h8v-2H2v2z"/></svg>
          </button>
        </span>
      </div>

      <div v-if="songs.length === 0 && keyword" class="empty-state">
        <p>未找到与 "{{ keyword }}" 相关的歌曲</p>
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
import { ref, onMounted, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import api from "../api";
import { playerState, playSong, formatDuration } from "../stores/player";

const route = useRoute();
const router = useRouter();

const keyword = ref("");
const searchKeyword = ref("");
const songs = ref([]);

// 添加到歌单相关
const showPlaylistModal = ref(false);
const userPlaylists = ref([]);
const selectedSongForPlaylist = ref(null);

// 搜索歌曲
const searchSongs = async (kw) => {
  if (!kw) {
    songs.value = [];
    return;
  }
  
  const res = await api.get("/songs", {
    params: { keyword: kw }
  });
  
  let results = res.data;
  
  // 标记完全匹配的歌曲并排序
  results = results.map(song => ({
    ...song,
    isExactMatch: song.title.toLowerCase() === kw.toLowerCase()
  }));
  
  // 完全匹配的排在最前面
  results.sort((a, b) => {
    if (a.isExactMatch && !b.isExactMatch) return -1;
    if (!a.isExactMatch && b.isExactMatch) return 1;
    return 0;
  });
  
  songs.value = results;
};

// 执行搜索
const doSearch = () => {
  const kw = searchKeyword.value.trim();
  if (kw) {
    router.push({ path: "/search", query: { keyword: kw } });
  }
};

// 快速搜索
const quickSearch = (kw) => {
  searchKeyword.value = kw;
  doSearch();
};

// 播放歌曲
const play = (song) => {
  playSong(song);
};

// 播放全部
const playAll = () => {
  if (songs.value.length > 0) {
    playSong(songs.value[0]);
  }
};

// 高亮关键词
const highlightKeyword = (text) => {
  if (!keyword.value || !text) return text;
  const regex = new RegExp(`(${keyword.value})`, 'gi');
  return text.replace(regex, '<em class="highlight">$1</em>');
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

// 监听路由变化
watch(() => route.query.keyword, (newKeyword) => {
  keyword.value = newKeyword || "";
  searchKeyword.value = newKeyword || "";
  searchSongs(newKeyword);
}, { immediate: true });

onMounted(() => {
  const kw = route.query.keyword;
  if (kw) {
    keyword.value = kw;
    searchKeyword.value = kw;
    searchSongs(kw);
  }
});
</script>

<style scoped>
.search-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  padding-bottom: 100px;
  background: rgba(255, 254, 249, 0.85);
  min-height: 100vh;
}

/* 搜索框区域 */
.search-header {
  text-align: center;
  padding: 30px 0;
  background: linear-gradient(135deg, #E6F4EA 0%, #fffef9 100%);
  border-radius: 8px;
  margin-bottom: 20px;
  border: 1px solid rgba(212, 168, 75, 0.2);
}

.search-box-large {
  display: inline-flex;
  align-items: center;
  background: #fffef9;
  border: 2px solid #d4a84b;
  border-radius: 25px;
  overflow: hidden;
  width: 500px;
  max-width: 90%;
}

.search-input-large {
  flex: 1;
  border: none;
  outline: none;
  padding: 12px 20px;
  font-size: 15px;
  background: transparent;
}

.search-btn-large {
  width: 50px;
  height: 44px;
  border: none;
  background: linear-gradient(135deg, #d4a84b, #b8923d);
  color: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.search-btn-large:hover {
  background: linear-gradient(135deg, #e8c478, #d4a84b);
}

.hot-search {
  margin-top: 15px;
  font-size: 13px;
  color: #666;
}

.hot-tag {
  color: #d4a84b;
  cursor: pointer;
  margin: 0 8px;
}

.hot-tag:hover {
  text-decoration: underline;
}

/* 搜索结果信息 */
.result-info {
  padding: 15px 0;
  font-size: 14px;
  color: #666;
  border-bottom: 1px solid #e5e5e5;
}

.result-info em {
  color: #d4a84b;
  font-style: normal;
  font-weight: 500;
}

/* 分类标签 */
.tabs {
  display: flex;
  gap: 30px;
  padding: 15px 0;
  border-bottom: 1px solid #e5e5e5;
}

.tab {
  font-size: 14px;
  color: #666;
  cursor: pointer;
  padding-bottom: 8px;
  border-bottom: 2px solid transparent;
}

.tab:hover {
  color: #d4a84b;
}

.tab.active {
  color: #d4a84b;
  border-color: #d4a84b;
}

/* 操作按钮 */
.action-bar {
  padding: 15px 0;
  display: flex;
  gap: 12px;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 20px;
  border-radius: 20px;
  font-size: 13px;
  cursor: pointer;
  border: 1px solid rgba(212, 168, 75, 0.3);
  background: #fffef9;
  color: #333;
}

.action-btn.primary {
  background: linear-gradient(135deg, #d4a84b, #b8923d);
  color: #fff;
  border-color: #d4a84b;
}

.action-btn.primary:hover {
  background: linear-gradient(135deg, #e8c478, #d4a84b);
}

/* 歌曲列表 */
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
  background: #E6F4EA;
}

.song-item.playing .col-title {
  color: #d4a84b;
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
  color: #d4a84b;
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
  display: flex;
  align-items: center;
  gap: 8px;
}

.col-title :deep(.highlight) {
  color: #d4a84b;
  font-style: normal;
}

.exact-badge {
  font-size: 11px;
  background: linear-gradient(135deg, #d4a84b, #b8923d);
  color: #fff;
  padding: 2px 6px;
  border-radius: 3px;
  flex-shrink: 0;
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
}

.icon-btn:hover {
  color: #d4a84b;
}

/* 弹窗样式 */
.modal-overlay { position: fixed; inset: 0; background: rgba(26,26,26,0.6); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.playlist-modal { background: #fffef9; border-radius: 10px; width: 360px; max-width: 90%; border: 1px solid rgba(212, 168, 75, 0.3); }
.playlist-modal-header { display: flex; justify-content: space-between; align-items: center; padding: 14px 18px; border-bottom: 1px solid rgba(212, 168, 75, 0.2); background: linear-gradient(90deg, rgba(230, 244, 234, 0.5), transparent); }
.playlist-modal-header h3 { font-size: 16px; font-weight: 600; color: #1a1a1a; margin: 0; }
.close-btn { width: 28px; height: 28px; border: none; background: none; font-size: 20px; color: #999; cursor: pointer; }
.playlist-modal-body { padding: 16px; max-height: 400px; overflow-y: auto; }
.empty-playlists { text-align: center; padding: 30px 0; }
.empty-playlists p { color: #999; margin-bottom: 16px; }
.create-btn { padding: 8px 20px; background: linear-gradient(135deg, #d4a84b, #b8923d); color: #fff; border: none; border-radius: 20px; cursor: pointer; }
.create-btn:hover { background: linear-gradient(135deg, #e8c478, #d4a84b); }
.playlist-list { display: flex; flex-direction: column; gap: 8px; }
.playlist-item { display: flex; align-items: center; gap: 12px; padding: 12px; border-radius: 8px; cursor: pointer; transition: background 0.2s; }
.playlist-item:hover { background: #E6F4EA; }
.playlist-icon { width: 40px; height: 40px; border-radius: 6px; background: linear-gradient(135deg, #d4a84b, #b8923d); color: #fff; display: flex; align-items: center; justify-content: center; font-size: 18px; }
.playlist-info { flex: 1; }
.playlist-name { font-size: 14px; color: #333; margin-bottom: 2px; }
.playlist-count { font-size: 12px; color: #999; }

</style>
