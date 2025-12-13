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
      </div>

      <div v-if="songs.length === 0 && keyword" class="empty-state">
        <p>未找到与 "{{ keyword }}" 相关的歌曲</p>
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
  background: #fafafa;
  min-height: 100vh;
}

/* 搜索框区域 */
.search-header {
  text-align: center;
  padding: 30px 0;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-radius: 8px;
  margin-bottom: 20px;
}

.search-box-large {
  display: inline-flex;
  align-items: center;
  background: #fff;
  border: 2px solid #31c27c;
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
}

.search-btn-large {
  width: 50px;
  height: 44px;
  border: none;
  background: #31c27c;
  color: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.search-btn-large:hover {
  background: #28a86d;
}

.hot-search {
  margin-top: 15px;
  font-size: 13px;
  color: #666;
}

.hot-tag {
  color: #31c27c;
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
  color: #31c27c;
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
  color: #31c27c;
}

.tab.active {
  color: #31c27c;
  border-color: #31c27c;
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
  border: 1px solid #ddd;
  background: #fff;
  color: #333;
}

.action-btn.primary {
  background: #31c27c;
  color: #fff;
  border-color: #31c27c;
}

.action-btn.primary:hover {
  background: #28a86d;
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
  background: #f0fff0;
}

.song-item.playing .col-title {
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
  display: flex;
  align-items: center;
  gap: 8px;
}

.col-title :deep(.highlight) {
  color: #31c27c;
  font-style: normal;
}

.exact-badge {
  font-size: 11px;
  background: #31c27c;
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

</style>
