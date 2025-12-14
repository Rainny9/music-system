<template>
  <div class="app-root">
    <!-- 顶部导航栏 -->
    <header class="top-bar">
      <!-- 左侧 LOGO + 名称 -->
      <div class="logo-area">
        <div class="logo-circle">♪</div>
        <span class="logo-text">音乐检索</span>
      </div>

      <!-- 中间主导航 -->
      <nav class="main-nav">
        <router-link
          to="/"
          class="nav-item"
          :class="{ active: $route.path === '/' }"
        >
          首页
        </router-link>
        <router-link
          v-if="userId"
          to="/favorites"
          class="nav-item"
          :class="{ active: $route.path === '/favorites' }"
        >
          我的收藏
        </router-link>
        <router-link
          v-if="userId"
          to="/playlists"
          class="nav-item"
          :class="{ active: $route.path === '/playlists' }"
        >
          我的歌单
        </router-link>
        <router-link
          v-if="userId"
          to="/history"
          class="nav-item"
          :class="{ active: $route.path === '/history' }"
        >
          播放历史
        </router-link>
        <router-link
          to="/recognize"
          class="nav-item"
          :class="{ active: $route.path === '/recognize' }"
        >
          歌曲检索
        </router-link>
        <router-link
          v-if="userId"
          to="/profile"
          class="nav-item"
          :class="{ active: $route.path === '/profile' }"
        >
          个人中心
        </router-link>
        <router-link
          v-if="isAdmin"
          to="/admin/songs"
          class="nav-item"
          :class="{ active: $route.path === '/admin/songs' }"
        >
          歌曲管理
        </router-link>
        <router-link
          v-if="isAdmin"
          to="/admin/users"
          class="nav-item"
          :class="{ active: $route.path === '/admin/users' }"
        >
          用户管理
        </router-link>
        <router-link
          v-if="isAdmin"
          to="/admin/announcements"
          class="nav-item"
          :class="{ active: $route.path === '/admin/announcements' }"
        >
          公告管理
        </router-link>
      </nav>

      <!-- 右侧搜索 + 登录/用户 -->
      <div class="right-area">
        <div class="search-box">
          <input
            v-model="searchText"
            class="search-input"
            placeholder="搜索歌曲 / 歌手 / 标签"
            @keyup.enter="goSearch"
            @focus="showDropdown = true"
            @blur="hideDropdown"
          />
          <button class="search-btn" @click="goSearch">
            <svg viewBox="0 0 24 24" width="16" height="16">
              <path fill="currentColor" d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>
            </svg>
          </button>
          <!-- 搜索下拉列表 -->
          <div v-if="showDropdown" class="search-dropdown">
            <div v-if="searchHistory.length > 0 && !searchText" class="dropdown-section">
              <div class="dropdown-header">
                <span>搜索历史</span>
                <button class="clear-history" @click.stop="clearHistory">清空</button>
              </div>
              <div 
                v-for="(item, index) in searchHistory" 
                :key="index" 
                class="dropdown-item history-item"
                @mousedown.prevent="selectHistory(item)"
              >
                <svg viewBox="0 0 24 24" width="14" height="14">
                  <path fill="#999" d="M13 3c-4.97 0-9 4.03-9 9H1l3.89 3.89.07.14L9 12H6c0-3.87 3.13-7 7-7s7 3.13 7 7-3.13 7-7 7c-1.93 0-3.68-.79-4.94-2.06l-1.42 1.42C8.27 19.99 10.51 21 13 21c4.97 0 9-4.03 9-9s-4.03-9-9-9z"/>
                </svg>
                <span>{{ item }}</span>
                <button class="delete-item" @mousedown.prevent.stop="deleteHistory(index)">×</button>
              </div>
            </div>
            <div v-if="!searchText && searchHistory.length === 0" class="dropdown-empty">
              暂无搜索历史
            </div>
          </div>
        </div>

        <div class="auth-area">
          <div v-if="userId" class="user-info">
            <div class="user-avatar" @click="toggleUserMenu">
              <img v-if="userAvatar" :src="userAvatar" alt="头像" />
              <span v-else class="avatar-text">{{ userName?.charAt(0)?.toUpperCase() || 'U' }}</span>
            </div>
            <span class="user-name">{{ userName || '用户' + userId }}</span>
            <div v-if="showUserMenu" class="user-menu">
              <div class="menu-item" @click="goProfile">个人中心</div>
              <div class="menu-item" @click="goFavorites">我的收藏</div>
              <div class="menu-item" @click="logout">退出登录</div>
            </div>
          </div>
          <button v-if="!userId" class="auth-btn" @click="goLogin">
            登录
          </button>
          <button v-if="!userId" class="auth-btn ghost" @click="goRegister">
            注册
          </button>
        </div>
      </div>
    </header>

    <!-- 顶部与页面主体之间的分隔条 -->
    <div class="top-bar-divider"></div>

    <!-- 页面主体 -->
    <main class="main-container" :class="{ 'has-player': playerState.currentSong }">
      <router-view />
    </main>

    <!-- 全局播放器 -->
    <div v-if="playerState.currentSong" class="global-player">
      <div class="player-left clickable" @click="goToSongDetail">
        <div class="song-cover" :class="{ spinning: playerState.isPlaying }">
          <img v-if="playerState.currentSong.cover_url" :src="playerState.currentSong.cover_url" alt="封面" class="cover-img" />
          <span v-else class="cover-icon">♪</span>
        </div>
        <div class="song-meta">
          <div class="song-title">{{ playerState.currentSong.title }}</div>
          <div class="song-artist">{{ playerState.currentSong.artist || '未知歌手' }}</div>
        </div>
      </div>
      
      <div class="player-center">
        <div class="player-top-row">
          <div class="player-controls">
            <!-- 上一首 -->
            <button class="ctrl-btn small" @click="handlePrev" title="上一首">
              <svg viewBox="0 0 24 24" width="20" height="20">
                <path fill="currentColor" d="M6 6h2v12H6zm3.5 6l8.5 6V6z"/>
              </svg>
            </button>
            <!-- 播放/暂停 -->
            <button class="ctrl-btn" @click="togglePlay">
              <svg v-if="playerState.isPlaying" viewBox="0 0 24 24" width="28" height="28">
                <path fill="currentColor" d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/>
              </svg>
              <svg v-else viewBox="0 0 24 24" width="28" height="28">
                <path fill="currentColor" d="M8 5v14l11-7z"/>
              </svg>
            </button>
            <!-- 下一首 -->
            <button class="ctrl-btn small" @click="handleNext" title="下一首">
              <svg viewBox="0 0 24 24" width="20" height="20">
                <path fill="currentColor" d="M6 18l8.5-6L6 6v12zM16 6v12h2V6h-2z"/>
              </svg>
            </button>
          </div>
          <!-- 滚动歌词（已禁用）
          <div class="lyrics-scroll" v-if="currentLyric">
            <span class="lyric-text">{{ currentLyric }}</span>
          </div>
          -->
        </div>
        <div class="progress-wrapper">
          <span class="time-current">{{ formatDuration(playerState.currentTime) }}</span>
          <input 
            type="range" 
            class="progress-bar"
            :value="playerState.currentTime"
            :max="playerState.duration || 100"
            :style="progressStyle"
            @input="onSeek"
          />
          <span class="time-total">{{ formatDuration(playerState.duration) }}</span>
        </div>
      </div>

      <div class="player-right">
        <!-- 播放模式 -->
        <button class="icon-btn" @click="handleToggleMode" :title="playModeTitle">
          <svg v-if="playerState.playMode === 'loop'" viewBox="0 0 24 24" width="18" height="18">
            <path fill="currentColor" d="M7 7h10v3l4-4-4-4v3H5v6h2V7zm10 10H7v-3l-4 4 4 4v-3h12v-6h-2v4z"/>
          </svg>
          <svg v-else-if="playerState.playMode === 'single'" viewBox="0 0 24 24" width="18" height="18">
            <path fill="currentColor" d="M7 7h10v3l4-4-4-4v3H5v6h2V7zm10 10H7v-3l-4 4 4 4v-3h12v-6h-2v4zm-4-2V9h-1l-2 1v1h1.5v4H13z"/>
          </svg>
          <svg v-else-if="playerState.playMode === 'random'" viewBox="0 0 24 24" width="18" height="18">
            <path fill="currentColor" d="M10.59 9.17L5.41 4 4 5.41l5.17 5.17 1.42-1.41zM14.5 4l2.04 2.04L4 18.59 5.41 20 17.96 7.46 20 9.5V4h-5.5zm.33 9.41l-1.41 1.41 3.13 3.13L14.5 20H20v-5.5l-2.04 2.04-3.13-3.13z"/>
          </svg>
          <svg v-else viewBox="0 0 24 24" width="18" height="18">
            <path fill="currentColor" d="M3 15h2v-2H3v2zm0 4h2v-2H3v2zm0-8h2V9H3v2zm4 4h14v-2H7v2zm0 4h14v-2H7v2zM7 9v2h14V9H7z"/>
          </svg>
        </button>
        <!-- 收藏 -->
        <button class="icon-btn" :class="{ active: isFavorited }" @click="handleToggleFavorite" title="收藏">
          <svg viewBox="0 0 24 24" width="18" height="18">
            <path fill="currentColor" d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
          </svg>
        </button>
        <!-- 添加到歌单 -->
        <button class="icon-btn" @click="showAddToPlaylist = true" title="添加到歌单">
          <svg viewBox="0 0 24 24" width="18" height="18">
            <path fill="currentColor" d="M14 10H2v2h12v-2zm0-4H2v2h12V6zm4 8v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zM2 16h8v-2H2v2z"/>
          </svg>
        </button>
        <!-- 下载 -->
        <a class="icon-btn" :href="playerState.currentSong.download_url" target="_blank" title="下载" @click.stop>
          <svg viewBox="0 0 24 24" width="18" height="18">
            <path fill="currentColor" d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/>
          </svg>
        </a>
        <!-- 评论 -->
        <button class="icon-btn" @click="goToSongDetail" title="评论">
          <svg viewBox="0 0 24 24" width="18" height="18">
            <path fill="currentColor" d="M21.99 4c0-1.1-.89-2-1.99-2H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h14l4 4-.01-18z"/>
          </svg>
        </button>
        <!-- 音量 -->
        <div class="volume-control">
          <button class="icon-btn" @click="toggleMute" :title="playerState.volume === 0 ? '取消静音' : '静音'">
            <svg v-if="playerState.volume === 0" viewBox="0 0 24 24" width="18" height="18">
              <path fill="currentColor" d="M16.5 12c0-1.77-1.02-3.29-2.5-4.03v2.21l2.45 2.45c.03-.2.05-.41.05-.63zm2.5 0c0 .94-.2 1.82-.54 2.64l1.51 1.51C20.63 14.91 21 13.5 21 12c0-4.28-2.99-7.86-7-8.77v2.06c2.89.86 5 3.54 5 6.71zM4.27 3L3 4.27 7.73 9H3v6h4l5 5v-6.73l4.25 4.25c-.67.52-1.42.93-2.25 1.18v2.06c1.38-.31 2.63-.95 3.69-1.81L19.73 21 21 19.73l-9-9L4.27 3zM12 4L9.91 6.09 12 8.18V4z"/>
            </svg>
            <svg v-else-if="playerState.volume < 0.5" viewBox="0 0 24 24" width="18" height="18">
              <path fill="currentColor" d="M18.5 12c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM5 9v6h4l5 5V4L9 9H5z"/>
            </svg>
            <svg v-else viewBox="0 0 24 24" width="18" height="18">
              <path fill="currentColor" d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/>
            </svg>
          </button>
          <input 
            type="range" 
            class="volume-slider"
            min="0"
            max="1"
            step="0.01"
            :value="playerState.volume"
            @input="onVolumeChange"
            @click.stop
          />
        </div>
      </div>

      <audio
        ref="globalAudioRef"
        :src="playerState.currentSong.play_url"
        :volume="playerState.volume"
        @timeupdate="onTimeUpdate"
        @loadedmetadata="onMetadataLoaded"
        @canplay="onCanPlay"
        @ended="onEnded"
        @play="playerState.isPlaying = true"
        @pause="playerState.isPlaying = false"
      ></audio>
    </div>

    <!-- 添加到歌单弹窗 -->
    <div v-if="showAddToPlaylist" class="modal-overlay" @click.self="showAddToPlaylist = false">
      <div class="modal-content playlist-modal">
        <div class="modal-header">
          <h3>添加到歌单</h3>
          <button class="close-btn" @click="showAddToPlaylist = false">×</button>
        </div>
        <div class="modal-body">
          <div v-if="userPlaylists.length === 0" class="empty-playlists">
            <p>暂无歌单</p>
            <button class="create-btn" @click="goToCreatePlaylist">创建歌单</button>
          </div>
          <div v-else class="playlist-list">
            <div 
              v-for="playlist in userPlaylists" 
              :key="playlist.id" 
              class="playlist-item"
              @click="addSongToPlaylist(playlist.id)"
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
import { ref, computed, onMounted, watch, nextTick } from "vue";
import { useRouter, useRoute } from "vue-router";
import { playerState, audioRef, formatDuration, playPrev, playNext, togglePlayMode, setVolume, PLAY_MODES } from "./stores/player";
import api from "./api";

// 进度条样式（已播放部分金色，未播放部分灰色）
const progressStyle = computed(() => {
  const percent = playerState.duration ? (playerState.currentTime / playerState.duration) * 100 : 0;
  return {
    background: `linear-gradient(to right, #d4a84b ${percent}%, #ccc ${percent}%)`
  };
});

// 播放模式标题
const playModeTitle = computed(() => {
  const titles = {
    [PLAY_MODES.LOOP]: '列表循环',
    [PLAY_MODES.SINGLE]: '单曲循环',
    [PLAY_MODES.RANDOM]: '随机播放',
    [PLAY_MODES.ORDER]: '顺序播放',
  };
  return titles[playerState.playMode] || '列表循环';
});

// 是否已收藏
const isFavorited = ref(false);
const prevVolume = ref(0.8);

// 添加到歌单相关
const showAddToPlaylist = ref(false);
const userPlaylists = ref([]);

// 歌词相关
const lyrics = ref([]);
const currentLyricIndex = ref(0);

// 当前歌词
const currentLyric = computed(() => {
  if (lyrics.value.length === 0) return '';
  return lyrics.value[currentLyricIndex.value]?.text || '';
});

// 解析歌词（支持 LRC 格式和普通文本）
const parseLyrics = (lyricsText) => {
  if (!lyricsText) return [];
  const lines = lyricsText.split('\n').filter(line => line.trim());
  const result = [];
  
  // 尝试解析 LRC 格式 [mm:ss.xx]歌词
  const lrcRegex = /\[(\d{2}):(\d{2})\.?(\d{0,2})\](.*)/;
  
  for (const line of lines) {
    const match = line.match(lrcRegex);
    if (match) {
      const minutes = parseInt(match[1]);
      const seconds = parseInt(match[2]);
      const ms = match[3] ? parseInt(match[3].padEnd(2, '0')) : 0;
      const time = minutes * 60 + seconds + ms / 100;
      const text = match[4].trim();
      if (text) {
        result.push({ time, text });
      }
    } else if (line.trim() && !line.startsWith('[')) {
      // 普通文本，按行分配时间
      result.push({ time: result.length * 5, text: line.trim() });
    }
  }
  
  return result.sort((a, b) => a.time - b.time);
};

// 加载歌词
const loadLyrics = async () => {
  if (!playerState.currentSong) {
    lyrics.value = [];
    return;
  }
  try {
    const res = await api.get(`/songs/${playerState.currentSong.id}`);
    lyrics.value = parseLyrics(res.data.lyrics);
    currentLyricIndex.value = 0;
  } catch (e) {
    lyrics.value = [];
  }
};

// 更新当前歌词索引
const updateLyricIndex = () => {
  if (lyrics.value.length === 0) return;
  const currentTime = playerState.currentTime;
  
  // 找到当前时间对应的歌词
  for (let i = lyrics.value.length - 1; i >= 0; i--) {
    if (currentTime >= lyrics.value[i].time) {
      if (currentLyricIndex.value !== i) {
        currentLyricIndex.value = i;
      }
      break;
    }
  }
};

// 检查收藏状态
const checkFavoriteStatus = async () => {
  const uid = localStorage.getItem("user_id");
  if (!uid || !playerState.currentSong) {
    isFavorited.value = false;
    return;
  }
  try {
    const res = await api.get(`/users/${uid}/favorites`);
    isFavorited.value = res.data.some(s => s.id === playerState.currentSong.id);
  } catch (e) {
    isFavorited.value = false;
  }
};

// 切换收藏
const handleToggleFavorite = async () => {
  const uid = localStorage.getItem("user_id");
  if (!uid) {
    alert("请先登录");
    router.push("/login");
    return;
  }
  await api.post(`/songs/${playerState.currentSong.id}/favorite`, { user_id: Number(uid) });
  isFavorited.value = !isFavorited.value;
};

// 上一首
const handlePrev = () => {
  playPrev();
};

// 下一首
const handleNext = () => {
  playNext();
};

// 切换播放模式
const handleToggleMode = () => {
  togglePlayMode();
};

// 音量变化
const onVolumeChange = (e) => {
  setVolume(parseFloat(e.target.value));
};

// 静音切换
const toggleMute = () => {
  if (playerState.volume > 0) {
    prevVolume.value = playerState.volume;
    setVolume(0);
  } else {
    setVolume(prevVolume.value || 0.8);
  }
};

const router = useRouter();
const route = useRoute();

const userId = ref(null);
const isAdmin = ref(false);
const userName = ref("");
const userAvatar = ref("");
const showUserMenu = ref(false);
const searchText = ref("");
const globalAudioRef = ref(null);
const showDropdown = ref(false);
const searchHistory = ref([]);

// 加载搜索历史
const loadSearchHistory = () => {
  const history = localStorage.getItem("search_history");
  if (history) {
    searchHistory.value = JSON.parse(history);
  }
};

// 保存搜索历史
const saveSearchHistory = (keyword) => {
  if (!keyword.trim()) return;
  // 移除重复项
  const index = searchHistory.value.indexOf(keyword);
  if (index > -1) {
    searchHistory.value.splice(index, 1);
  }
  // 添加到开头
  searchHistory.value.unshift(keyword);
  // 最多保存10条
  if (searchHistory.value.length > 10) {
    searchHistory.value.pop();
  }
  localStorage.setItem("search_history", JSON.stringify(searchHistory.value));
};

// 选择历史记录
const selectHistory = (item) => {
  searchText.value = item;
  goSearch();
};

// 删除单条历史
const deleteHistory = (index) => {
  searchHistory.value.splice(index, 1);
  localStorage.setItem("search_history", JSON.stringify(searchHistory.value));
};

// 清空历史
const clearHistory = () => {
  searchHistory.value = [];
  localStorage.removeItem("search_history");
};

// 隐藏下拉框（延迟以便点击事件生效）
const hideDropdown = () => {
  setTimeout(() => {
    showDropdown.value = false;
  }, 200);
};

// 同步 audio 引用
watch(globalAudioRef, (newRef) => {
  audioRef.value = newRef;
});

// 监听歌曲变化，自动播放
watch(() => playerState.currentSong, async (newSong, oldSong) => {
  if (newSong) {
    // 等待 DOM 更新（audio 元素创建）
    await nextTick();
    // 再等一帧确保 audio 元素已挂载
    await nextTick();
    if (globalAudioRef.value) {
      // 设置音量
      globalAudioRef.value.volume = playerState.volume;
      // 如果是同一首歌，不需要重新加载
      if (oldSong && oldSong.id === newSong.id) {
        globalAudioRef.value.play();
      } else {
        // 新歌曲，等待加载后播放
        globalAudioRef.value.load();
        globalAudioRef.value.play().catch(() => {
          // 自动播放可能被浏览器阻止，忽略错误
        });
      }
    }
    // 检查收藏状态
    checkFavoriteStatus();
    // 加载歌词
    loadLyrics();
  }
});

// 播放/暂停切换
const togglePlay = () => {
  if (globalAudioRef.value) {
    if (playerState.isPlaying) {
      globalAudioRef.value.pause();
    } else {
      globalAudioRef.value.play();
    }
  }
};

// 时间更新
const onTimeUpdate = () => {
  if (globalAudioRef.value) {
    playerState.currentTime = globalAudioRef.value.currentTime;
    updateLyricIndex();
  }
};

// 元数据加载完成
const onMetadataLoaded = () => {
  if (globalAudioRef.value) {
    playerState.duration = globalAudioRef.value.duration;
  }
};

// 可以播放时自动播放
const onCanPlay = () => {
  if (globalAudioRef.value && playerState.isPlaying) {
    globalAudioRef.value.play().catch(() => {});
  }
};

// 播放结束
const onEnded = () => {
  if (playerState.playMode === PLAY_MODES.SINGLE) {
    // 单曲循环
    if (globalAudioRef.value) {
      globalAudioRef.value.currentTime = 0;
      globalAudioRef.value.play();
    }
  } else {
    // 其他模式播放下一首
    playNext();
  }
};

// 进度条拖动
const onSeek = (e) => {
  if (globalAudioRef.value) {
    globalAudioRef.value.currentTime = e.target.value;
  }
};

// 跳转到歌曲详情
const goToSongDetail = () => {
  if (playerState.currentSong) {
    router.push(`/songs/${playerState.currentSong.id}`);
  }
};

// 切换用户菜单
const toggleUserMenu = () => {
  showUserMenu.value = !showUserMenu.value;
};

// 关闭用户菜单
const closeUserMenu = () => {
  showUserMenu.value = false;
};

// 个人中心
const goProfile = () => {
  showUserMenu.value = false;
  router.push("/profile");
};

// 我的收藏
const goFavorites = () => {
  showUserMenu.value = false;
  router.push("/favorites");
};

// 检查登录状态
const checkLoginStatus = async () => {
  const uid = localStorage.getItem("user_id");
  const flag = localStorage.getItem("is_admin");
  userId.value = uid;
  userName.value = localStorage.getItem("username") || "";
  userAvatar.value = localStorage.getItem("avatar_url") || "";
  // 只有 is_admin 为 "true" 或 "1" 时才显示后台管理
  isAdmin.value = flag === "1" || flag === "true";
  
  // 如果已登录但没有头像URL，尝试获取用户信息
  if (uid && !userAvatar.value) {
    try {
      const res = await api.get(`/users/${uid}/info`);
      if (res.data.avatar_url) {
        userAvatar.value = res.data.avatar_url;
        localStorage.setItem("avatar_url", res.data.avatar_url);
      }
      if (res.data.username) {
        userName.value = res.data.username;
        localStorage.setItem("username", res.data.username);
      }
    } catch (e) {
      // 忽略错误
    }
  }
};

onMounted(() => {
  checkLoginStatus();
  loadSearchHistory();
});

// 监听路由变化，刷新登录状态（登录后跳转回来时更新）
watch(() => route.path, () => {
  checkLoginStatus();
});

const goLogin = () => {
  router.push("/login");
};

const goRegister = () => {
  router.push("/register");
};

const logout = () => {
  localStorage.removeItem("user_id");
  localStorage.removeItem("is_admin");
  localStorage.removeItem("username");
  localStorage.removeItem("avatar_url");
  userId.value = null;
  isAdmin.value = false;
  userName.value = "";
  userAvatar.value = "";
  showUserMenu.value = false;
  router.push("/login");
};

// 搜索：跳转到搜索结果页面
const goSearch = () => {
  const keyword = searchText.value.trim();
  if (keyword) {
    saveSearchHistory(keyword);
    showDropdown.value = false;
    router.push({
      path: "/search",
      query: { keyword },
    });
  }
};

// 加载用户歌单
const loadUserPlaylists = async () => {
  const uid = localStorage.getItem("user_id");
  if (!uid) return;
  try {
    const res = await api.get(`/playlists?user_id=${uid}`);
    userPlaylists.value = res.data;
  } catch (e) {
    userPlaylists.value = [];
  }
};

// 添加歌曲到歌单
const addSongToPlaylist = async (playlistId) => {
  if (!playerState.currentSong) return;
  try {
    await api.post(`/playlists/${playlistId}/songs`, {
      song_id: playerState.currentSong.id
    });
    alert("已添加到歌单");
    showAddToPlaylist.value = false;
  } catch (e) {
    if (e.response?.data?.msg === "song already in playlist") {
      alert("歌曲已在该歌单中");
    } else {
      alert("添加失败");
    }
  }
};

// 跳转到创建歌单页面
const goToCreatePlaylist = () => {
  showAddToPlaylist.value = false;
  router.push("/playlists");
};

// 监听弹窗打开，加载歌单
watch(showAddToPlaylist, (val) => {
  if (val) {
    const uid = localStorage.getItem("user_id");
    if (!uid) {
      alert("请先登录");
      showAddToPlaylist.value = false;
      router.push("/login");
      return;
    }
    loadUserPlaylists();
  }
});
</script>

<style scoped>
.app-root {
  min-height: 100vh;
  background-color: #fffef9;
  /* 水墨竹石淡纹背景 */
  background-image: 
    url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 200 800'%3E%3Cg fill='none' stroke='%232d5a5a' stroke-width='0.5' opacity='0.08'%3E%3Cpath d='M30 800 Q35 600 30 400 Q25 200 35 0'/%3E%3Cpath d='M35 350 Q60 320 45 280'/%3E%3Cpath d='M28 450 Q5 420 15 380'/%3E%3Cpath d='M32 550 Q55 530 48 490'/%3E%3Cpath d='M25 650 Q0 620 12 580'/%3E%3Cpath d='M38 250 Q58 230 52 200'/%3E%3Cpath d='M33 150 Q10 130 18 100'/%3E%3Cellipse cx='80' cy='750' rx='35' ry='20'/%3E%3Cellipse cx='90' cy='730' rx='25' ry='15'/%3E%3Cellipse cx='70' cy='770' rx='20' ry='12'/%3E%3Cpath d='M120 800 Q125 650 118 500 Q122 350 115 200'/%3E%3Cpath d='M118 400 Q140 380 130 350'/%3E%3Cpath d='M122 550 Q100 520 108 480'/%3E%3Cpath d='M116 300 Q138 270 128 240'/%3E%3C/g%3E%3C/svg%3E"),
    url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 200 800'%3E%3Cg fill='none' stroke='%232d5a5a' stroke-width='0.5' opacity='0.08'%3E%3Cpath d='M170 800 Q165 600 170 400 Q175 200 165 0'/%3E%3Cpath d='M165 350 Q140 320 155 280'/%3E%3Cpath d='M172 450 Q195 420 185 380'/%3E%3Cpath d='M168 550 Q145 530 152 490'/%3E%3Cpath d='M175 650 Q200 620 188 580'/%3E%3Cpath d='M162 250 Q142 230 148 200'/%3E%3Cpath d='M167 150 Q190 130 182 100'/%3E%3Cellipse cx='120' cy='750' rx='35' ry='20'/%3E%3Cellipse cx='110' cy='730' rx='25' ry='15'/%3E%3Cellipse cx='130' cy='770' rx='20' ry='12'/%3E%3Cpath d='M80 800 Q75 650 82 500 Q78 350 85 200'/%3E%3Cpath d='M82 400 Q60 380 70 350'/%3E%3Cpath d='M78 550 Q100 520 92 480'/%3E%3Cpath d='M84 300 Q62 270 72 240'/%3E%3C/g%3E%3C/svg%3E"),
    linear-gradient(90deg, rgba(230, 244, 234, 0.5) 0%, transparent 12%, transparent 88%, rgba(230, 244, 234, 0.5) 100%);
  background-position: left top, right top, center;
  background-repeat: repeat-y, repeat-y, no-repeat;
  background-size: 200px auto, 200px auto, 100% 100%;
  background-attachment: fixed, fixed, fixed;
}

/* 顶部导航栏 - 浅青白渐变 */
.top-bar {
  height: 68px;
  padding: 0 40px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: linear-gradient(180deg, #ffffff 0%, #C8E0E2 100%);
  box-shadow: 0 2px 12px rgba(200, 224, 226, 0.4);
  position: sticky;
  top: 0;
  z-index: 100;
  /* 底部金色装饰线 */
  border-bottom: 2px solid;
  border-image: linear-gradient(90deg, transparent, #d4a84b 20%, #f0c674 50%, #d4a84b 80%, transparent) 1;
}

/* 左侧 LOGO 区域 */
.logo-area {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-circle {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: 
    radial-gradient(circle at center, #d4a84b 0%, #d4a84b 15%, transparent 16%),
    radial-gradient(circle at center, #1a1a1a 17%, #1a1a1a 30%, transparent 31%),
    repeating-radial-gradient(circle at center, transparent 0%, transparent 4%, rgba(255,255,255,0.03) 5%, transparent 6%),
    linear-gradient(135deg, #2a2a2a 0%, #1a1a1a 50%, #2a2a2a 100%);
  color: #d4a84b;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: bold;
  /* 黑胶唱片效果 */
  border: 3px solid #2d5a5a;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.4), inset 0 0 10px rgba(0,0,0,0.3);
  position: relative;
}

.logo-text {
  font-size: 22px;
  font-weight: 700;
  color: #2d5a5a;
  letter-spacing: 4px;
  text-shadow: 0 1px 2px rgba(255, 255, 255, 0.5);
}

/* 中间主导航 - 古典风格 */
.main-nav {
  display: flex;
  align-items: center;
  gap: 8px;
}

.nav-item {
  font-size: 14px;
  color: #2d5a5a;
  text-decoration: none;
  padding: 8px 16px;
  border-radius: 2px;
  transition: all 0.3s ease;
  position: relative;
  letter-spacing: 1px;
}

.nav-item:hover {
  color: #d4a84b;
  background: rgba(212, 168, 75, 0.15);
}

.nav-item.active {
  color: #d4a84b;
  background: rgba(200, 224, 226, 0.5);
}

.nav-item.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 20px;
  height: 2px;
  background: #d4a84b;
  border-radius: 1px;
}

/* 右侧区域 */
.right-area {
  display: flex;
  align-items: center;
  gap: 16px;
}

/* 搜索框 - 浅青风格 */
.search-box {
  position: relative;
  display: flex;
  align-items: center;
  border: 1px solid rgba(45, 90, 90, 0.3);
  border-radius: 4px;
  overflow: visible;
  background: rgba(255, 255, 255, 0.6);
  transition: all 0.3s;
}

.search-box:focus-within {
  border-color: #d4a84b;
  background: rgba(255, 255, 255, 0.9);
  box-shadow: 0 2px 12px rgba(212, 168, 75, 0.2);
}

.search-input {
  border: none;
  outline: none;
  padding: 8px 14px;
  width: 200px;
  font-size: 13px;
  background: transparent;
  color: #1a1a1a;
}

.search-input::placeholder {
  color: #888;
}

.search-btn {
  border: none;
  outline: none;
  width: 36px;
  height: 34px;
  background: linear-gradient(135deg, rgba(255,255,255,0.4) 0%, #8BA8A8 50%, #7a9999 100%);
  color: #fff;
  cursor: pointer;
  border-radius: 0 3px 3px 0;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
}

.search-btn:hover {
  background: linear-gradient(135deg, rgba(255,255,255,0.5) 0%, #9ab8b8 50%, #8BA8A8 100%);
}

/* 搜索下拉列表 */
.search-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  margin-top: 8px;
  background: #fffef9;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  overflow: hidden;
  border: 1px solid rgba(212, 168, 75, 0.2);
}

.dropdown-section {
  padding: 8px 0;
}

.dropdown-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 14px;
  font-size: 12px;
  color: #999;
}

.clear-history {
  border: none;
  background: none;
  color: #2d5a5a;
  font-size: 12px;
  cursor: pointer;
}

.clear-history:hover {
  text-decoration: underline;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  cursor: pointer;
  transition: background 0.2s;
}

.dropdown-item:hover {
  background: #f5f5f5;
}

.history-item span {
  flex: 1;
  font-size: 13px;
  color: #333;
}

.delete-item {
  border: none;
  background: none;
  color: #999;
  font-size: 16px;
  cursor: pointer;
  padding: 0 4px;
  opacity: 0;
  transition: opacity 0.2s;
}

.dropdown-item:hover .delete-item {
  opacity: 1;
}

.delete-item:hover {
  color: #ff4d4f;
}

.dropdown-empty {
  padding: 20px;
  text-align: center;
  font-size: 13px;
  color: #999;
}

/* 登录/注册按钮区域 - 中华风 */
.auth-area {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
}

.auth-btn {
  border-radius: 4px;
  padding: 6px 18px;
  border: 1px solid #d4a84b;
  background: linear-gradient(135deg, #d4a84b, #b8923d);
  color: #fff;
  cursor: pointer;
  font-size: 13px;
  letter-spacing: 1px;
  transition: all 0.3s;
}

.auth-btn:hover {
  background: linear-gradient(135deg, #e8c478, #d4a84b);
  box-shadow: 0 2px 8px rgba(212, 168, 75, 0.4);
}

.auth-btn.ghost {
  background: rgba(255, 255, 255, 0.6);
  color: #2d5a5a;
  border: 1px solid rgba(45, 90, 90, 0.3);
}

.auth-btn.ghost:hover {
  background: rgba(255, 255, 255, 0.9);
  border-color: #d4a84b;
}

/* 用户信息区域 */
.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  position: relative;
}

.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 4px;
  background: linear-gradient(135deg, rgba(255,255,255,0.4) 0%, #8BA8A8 50%, #7a9999 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  overflow: hidden;
  border: 2px solid #d4a84b;
  transition: all 0.3s;
}

.user-avatar:hover {
  border-color: #f0c674;
  transform: scale(1.05);
  box-shadow: 0 2px 8px rgba(212, 168, 75, 0.4);
}

.user-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-text {
  color: #d4a84b;
  font-size: 14px;
  font-weight: 600;
}

.user-name {
  color: #2d5a5a;
  font-size: 14px;
  max-width: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.user-menu {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 8px;
  background: #fffef9;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  overflow: hidden;
  z-index: 1000;
  min-width: 120px;
  border: 1px solid rgba(212, 168, 75, 0.2);
}

.menu-item {
  padding: 12px 16px;
  font-size: 14px;
  color: #333;
  cursor: pointer;
  transition: all 0.2s;
}

.menu-item:hover {
  background: rgba(45, 90, 90, 0.08);
  color: #2d5a5a;
}

/* 顶部与页面主体之间的分隔条 */
.top-bar-divider {
  height: 8px;
  background: linear-gradient(180deg, rgba(200, 224, 226, 0.3) 0%, transparent 100%);
}

/* 主体容器 */
.main-container {
  max-width: 1100px;
  margin: 0 auto;
  padding: 20px 20px 40px;
}

.main-container.has-player {
  padding-bottom: 110px;
}

/* 全局播放器 - 浅青白渐变 */
.global-player {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 76px;
  background: linear-gradient(180deg, #C8E0E2 0%, #ffffff 100%);
  box-shadow: 0 -4px 20px rgba(200, 224, 226, 0.4);
  display: flex;
  align-items: center;
  padding: 0 24px;
  z-index: 1000;
  cursor: pointer;
  /* 顶部金色装饰线 */
  border-top: 2px solid;
  border-image: linear-gradient(90deg, transparent, #d4a84b 20%, #f0c674 50%, #d4a84b 80%, transparent) 1;
}

.global-player .clickable:hover {
  opacity: 0.8;
}

.player-center {
  cursor: default;
}

.player-top-row {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 4px;
}

.lyrics-scroll {
  flex: 1;
  overflow: hidden;
  height: 24px;
  display: flex;
  align-items: center;
}

.lyric-text {
  font-size: 13px;
  color: #d4a84b;
  white-space: nowrap;
  animation: lyricFade 0.3s ease-in-out;
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
}

@keyframes lyricFade {
  0% { opacity: 0; transform: translateY(10px); }
  100% { opacity: 1; transform: translateY(0); }
}

.player-left {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 200px;
}

.song-cover {
  width: 54px;
  height: 54px;
  border-radius: 50%;
  background: 
    radial-gradient(circle at center, #d4a84b 0%, #d4a84b 12%, transparent 13%),
    radial-gradient(circle at center, #1a1a1a 14%, #1a1a1a 25%, transparent 26%),
    repeating-radial-gradient(circle at center, transparent 0%, transparent 5%, rgba(255,255,255,0.03) 6%, transparent 7%),
    linear-gradient(135deg, #2a2a2a 0%, #1a1a1a 50%, #2a2a2a 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  flex-shrink: 0;
  border: 3px solid #2d5a5a;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.4), inset 0 0 15px rgba(0,0,0,0.3);
  position: relative;
}

.song-cover .cover-img {
  width: 60%;
  height: 60%;
  object-fit: cover;
  border-radius: 50%;
  border: 2px solid #d4a84b;
}

.cover-icon {
  color: #d4a84b;
  font-size: 16px;
  z-index: 1;
}

/* 黑胶唱片旋转动画 */
@keyframes vinyl-spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.song-cover.spinning {
  animation: vinyl-spin 8s linear infinite;
}

.song-cover.spinning:hover {
  animation-play-state: running;
}

.song-meta {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.song-title {
  font-size: 14px;
  font-weight: 500;
  color: #1a1a1a;
  max-width: 150px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.song-artist {
  font-size: 12px;
  color: #666;
}

.player-center {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 0 30px;
}

.player-controls {
  display: flex;
  align-items: center;
  gap: 20px;
}

.ctrl-btn {
  width: 44px;
  height: 44px;
  border: none;
  background: linear-gradient(135deg, rgba(255,255,255,0.4) 0%, #8BA8A8 50%, #7a9999 100%);
  border-radius: 50%;
  color: #d4a84b;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
  border: 2px solid #d4a84b;
  box-shadow: 0 2px 8px rgba(139, 168, 168, 0.4);
}

.ctrl-btn:hover {
  transform: scale(1.1);
  background: linear-gradient(135deg, rgba(255,255,255,0.5) 0%, #9ab8b8 50%, #8BA8A8 100%);
  box-shadow: 0 4px 12px rgba(139, 168, 168, 0.6);
}

.progress-wrapper {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  max-width: 500px;
}

.time-current,
.time-total {
  font-size: 12px;
  color: #666;
  min-width: 40px;
}

.time-current {
  text-align: right;
}

.progress-bar {
  flex: 1;
  height: 4px;
  -webkit-appearance: none;
  appearance: none;
  background: rgba(45, 90, 90, 0.2);
  border-radius: 2px;
  cursor: pointer;
}

.progress-bar::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 12px;
  height: 12px;
  background: #d4a84b;
  border-radius: 50%;
  cursor: pointer;
  box-shadow: 0 0 6px rgba(212, 168, 75, 0.5);
}

.progress-bar::-moz-range-thumb {
  width: 12px;
  height: 12px;
  background: #d4a84b;
  border-radius: 50%;
  cursor: pointer;
  border: none;
  box-shadow: 0 0 6px rgba(212, 168, 75, 0.5);
}

.progress-bar::-moz-range-track {
  height: 4px;
  border-radius: 2px;
}

.player-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.player-right .icon-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  color: #666;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all 0.2s;
  text-decoration: none;
}

.player-right .icon-btn:hover {
  background: rgba(200, 224, 226, 0.5);
  color: #d4a84b;
}

.player-right .icon-btn.active {
  color: #ff4d4f;
}

.volume-control {
  display: flex;
  align-items: center;
  gap: 4px;
}

.volume-slider {
  width: 80px;
  height: 4px;
  -webkit-appearance: none;
  appearance: none;
  background: rgba(45, 90, 90, 0.2);
  border-radius: 2px;
  cursor: pointer;
}

.volume-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 12px;
  height: 12px;
  background: #d4a84b;
  border-radius: 50%;
  cursor: pointer;
}

.ctrl-btn.small {
  width: 34px;
  height: 34px;
  background: transparent;
  color: rgba(255, 255, 255, 0.6);
  border: none;
}

.ctrl-btn.small:hover {
  color: #d4a84b;
  transform: none;
}

/* 弹窗样式 - 中华风 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.modal-content {
  background: #fffef9;
  border-radius: 8px;
  width: 360px;
  max-height: 80vh;
  overflow: hidden;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(212, 168, 75, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid rgba(212, 168, 75, 0.2);
  background: linear-gradient(180deg, #faf8f5 0%, #fffef9 100%);
}

.modal-header h3 {
  margin: 0;
  font-size: 16px;
  color: #333;
}

.close-btn {
  border: none;
  background: none;
  font-size: 24px;
  color: #999;
  cursor: pointer;
  line-height: 1;
}

.close-btn:hover {
  color: #333;
}

.modal-body {
  padding: 16px 20px;
  max-height: 400px;
  overflow-y: auto;
}

.empty-playlists {
  text-align: center;
  padding: 30px 0;
}

.empty-playlists p {
  color: #999;
  margin-bottom: 16px;
}

.create-btn {
  padding: 8px 20px;
  background: linear-gradient(135deg, #d4a84b, #b8923d);
  color: #fff;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  font-size: 14px;
}

.create-btn:hover {
  background: linear-gradient(135deg, #e8c478, #d4a84b);
}

.playlist-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.playlist-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
}

.playlist-item:hover {
  background: #E6F4EA;
}

.playlist-icon {
  width: 40px;
  height: 40px;
  border-radius: 6px;
  background: linear-gradient(135deg, #d4a84b, #b8923d);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}

.playlist-info {
  flex: 1;
}

.playlist-name {
  font-size: 14px;
  color: #333;
  margin-bottom: 2px;
}

.playlist-count {
  font-size: 12px;
  color: #999;
}
</style>