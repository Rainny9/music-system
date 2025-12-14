<template>
  <div class="song-detail-page">
    <!-- 返回按钮 -->
    <button class="back-btn" @click="goBack">
      <svg viewBox="0 0 24 24" width="20" height="20">
        <path fill="currentColor" d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z"/>
      </svg>
      返回
    </button>

    <div class="song-header">
      <!-- 左侧封面（暂时用一个占位背景，如果有 cover_url 就显示图片） -->
      <div class="cover-box">
        <img
          v-if="song.cover_url"
          :src="song.cover_url"
          alt="封面"
          class="cover-img"
        />
        <div v-else class="cover-placeholder">
          {{ song.title?.slice(0, 2) || "歌" }}
        </div>
      </div>

      <!-- 右侧歌曲信息 -->
      <div class="info-box">
        <h2 class="song-title">
          {{ song.title || "歌曲详情" }}
        </h2>
        <p class="song-artist">
          歌手：{{ song.artist || "未知" }}
        </p>
        <p class="song-meta">
          专辑：{{ song.album || "暂无" }}　|　分类：{{ song.genre || "未分类" }}　|　
          语言：{{ song.language || "未知" }}
        </p>
        <p class="song-meta">
          发行时间：{{ song.release_date || "未知" }}
        </p>

        <div class="action-row">
          <button class="btn primary" @click="handlePlay">
            {{ isCurrentSong && playerState.isPlaying ? '暂停' : '播放' }}
          </button>
          <button class="btn" @click="toggleFavorite">收藏/取消收藏</button>
          <button class="btn" @click="openAddToPlaylist">添加到歌单</button>
          <a v-if="song.download_url" :href="song.download_url" target="_blank" class="btn">
            下载
          </a>
        </div>

        <!-- 当前歌曲播放状态显示 -->
        <div v-if="isCurrentSong" class="now-playing-info">
          <span class="playing-icon">♪</span>
          <span>正在播放</span>
          <span class="playing-time">{{ formatDuration(playerState.currentTime) }} / {{ formatDuration(playerState.duration) }}</span>
        </div>
      </div>
    </div>

    <!-- 歌词 + 评论区 -->
    <div class="song-body">
      <div class="lyrics-box">
        <h3>歌词</h3>
        <div class="lyrics-container" ref="lyricsContainer">
          <div 
            v-for="(line, index) in parsedLyrics" 
            :key="index"
            class="lyric-line"
            :class="{ active: isCurrentSong && index === currentLyricIndex }"
            :ref="el => { if (isCurrentSong && index === currentLyricIndex) scrollToLyric(el) }"
          >
            {{ line.text }}
          </div>
          <div v-if="parsedLyrics.length === 0" class="no-lyrics">暂未提供歌词</div>
        </div>
      </div>

      <div class="comments-box">
        <h3>评论</h3>
        <ul class="comment-list">
          <li v-for="c in comments" :key="c.id" class="comment-item">
            <div class="comment-meta">
              用户 {{ c.user_id }} · {{ c.created_at }}
            </div>
            <div class="comment-content">
              {{ c.content }}
            </div>
          </li>
        </ul>

        <div class="comment-form">
          <textarea
            v-model="commentText"
            placeholder="写下你的评论……"
          ></textarea>
          <button class="btn primary" @click="addComment">发表评论</button>
          <p class="comment-msg">{{ msg }}</p>
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
            <button class="btn primary" @click="goToPlaylists">创建歌单</button>
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
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import api from "../api";
import { playerState, playSong, formatDuration } from "../stores/player";

const route = useRoute();
const router = useRouter();

const songId = Number(route.params.id);
const song = ref({});
const comments = ref([]);
const commentText = ref("");
const msg = ref("");
const lyricsContainer = ref(null);

// 添加到歌单相关
const showPlaylistModal = ref(false);
const userPlaylists = ref([]);

// 判断当前歌曲是否正在播放
const isCurrentSong = computed(() => {
  return playerState.currentSong && playerState.currentSong.id === songId;
});

// 解析歌词
const parsedLyrics = computed(() => {
  if (!song.value.lyrics) return [];
  const lines = song.value.lyrics.split('\n').filter(line => line.trim());
  const result = [];
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
      result.push({ time: result.length * 5, text: line.trim() });
    }
  }
  return result.sort((a, b) => a.time - b.time);
});

// 当前歌词索引
const currentLyricIndex = computed(() => {
  if (!isCurrentSong.value || parsedLyrics.value.length === 0) return -1;
  const currentTime = playerState.currentTime;
  for (let i = parsedLyrics.value.length - 1; i >= 0; i--) {
    if (currentTime >= parsedLyrics.value[i].time) {
      return i;
    }
  }
  return 0;
});

// 滚动到当前歌词（已禁用自动滚动）
const scrollToLyric = (el) => {
  // 已禁用自动滚动功能
  // if (el && lyricsContainer.value) {
  //   el.scrollIntoView({ behavior: 'smooth', block: 'center' });
  // }
};

const loadSongDetail = async () => {
  const res = await api.get(`/songs/${songId}`);
  song.value = res.data;
};

const loadComments = async () => {
  const res = await api.get(`/songs/${songId}/comments`);
  comments.value = res.data;
};

// 返回上一页
const goBack = () => {
  router.back();
};

// 播放/暂停切换
const handlePlay = () => {
  if (isCurrentSong.value) {
    // 当前歌曲，切换播放/暂停
    if (playerState.isPlaying) {
      // 暂停 - 通过修改状态触发 App.vue 中的 watch
      playerState.isPlaying = false;
    } else {
      playerState.isPlaying = true;
    }
  } else {
    // 不是当前歌曲，播放这首歌
    playSong(song.value);
  }
};

const toggleFavorite = async () => {
  const userId = localStorage.getItem("user_id");
  if (!userId) {
    alert("请先登录");
    router.push("/login");
    return;
  }
  await api.post(`/songs/${songId}/favorite`, {
    user_id: Number(userId),
  });
  alert("收藏状态已切换");
};

const addComment = async () => {
  const userId = localStorage.getItem("user_id");
  if (!userId) {
    alert("请先登录");
    router.push("/login");
    return;
  }
  if (!commentText.value.trim()) {
    msg.value = "评论内容不能为空";
    return;
  }
  try {
    await api.post(`/songs/${songId}/comments`, {
      user_id: Number(userId),
      content: commentText.value,
    });
    commentText.value = "";
    msg.value = "评论成功";
    loadComments();
  } catch (e) {
    const data = e.response?.data;
    if (data?.reason) {
      msg.value = `${data.msg}：${data.reason}`;
    } else {
      msg.value = data?.msg || "评论失败";
    }
  }
};

// 打开添加到歌单弹窗
const openAddToPlaylist = async () => {
  const uid = localStorage.getItem("user_id");
  if (!uid) { alert("请先登录"); router.push("/login"); return; }
  try {
    const res = await api.get(`/playlists?user_id=${uid}`);
    userPlaylists.value = res.data;
  } catch (e) { userPlaylists.value = []; }
  showPlaylistModal.value = true;
};

// 添加歌曲到歌单
const addToPlaylist = async (playlistId) => {
  try {
    await api.post(`/playlists/${playlistId}/songs`, { song_id: songId });
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
  // 滚动到页面顶部
  window.scrollTo(0, 0);
  loadSongDetail();
  loadComments();
});
</script>

<style scoped>
/* 歌曲详情 - 中华风 */
.song-detail-page {
  padding: 24px 20px;
  max-width: 1200px;
  margin: 0 auto;
  min-height: calc(100vh - 140px);
  background: rgba(255, 254, 249, 0.85);
}

.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  margin-top: 0;
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

.song-header {
  display: flex;
  gap: 24px;
  background: linear-gradient(135deg, #fffef9, rgba(212, 168, 75, 0.05));
  padding: 24px;
  border-radius: 8px;
  border: 1px solid rgba(212, 168, 75, 0.2);
  position: relative;
  overflow: hidden;
}

.song-header::before {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, rgba(45, 90, 90, 0.03) 0%, transparent 70%);
  pointer-events: none;
}

.cover-box {
  width: 220px;
  height: 220px;
  border-radius: 4px;
  overflow: hidden;
  background: linear-gradient(135deg, rgba(255,255,255,0.4) 0%, #8BA8A8 50%, #7a9999 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid #d4a84b;
  box-shadow: 0 8px 25px rgba(139, 168, 168, 0.2);
  flex-shrink: 0;
}

.cover-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cover-placeholder {
  font-size: 42px;
  color: #d4a84b;
}

.info-box {
  flex: 1;
  position: relative;
  z-index: 1;
}

.song-title {
  font-size: 26px;
  font-weight: 600;
  margin-bottom: 12px;
  color: #1a1a1a;
  letter-spacing: 1px;
}

.song-artist {
  font-size: 15px;
  color: #666;
  margin-bottom: 6px;
}

.song-meta {
  font-size: 13px;
  color: #999;
  margin-bottom: 6px;
}

.action-row {
  margin: 20px 0 12px;
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.btn {
  padding: 8px 20px;
  border-radius: 4px;
  border: 1px solid rgba(212, 168, 75, 0.3);
  background: #fffef9;
  color: #666;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.3s;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
}

.btn:hover {
  border-color: #d4a84b;
  color: #d4a84b;
  background: rgba(212, 168, 75, 0.1);
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

.now-playing-info {
  margin-top: 16px;
  padding: 12px 16px;
  background: linear-gradient(135deg, rgba(212, 168, 75, 0.1), rgba(212, 168, 75, 0.05));
  border-radius: 4px;
  border: 1px solid rgba(212, 168, 75, 0.2);
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
  color: #8b7355;
}

.playing-icon {
  font-size: 16px;
  color: #2d5a5a;
  animation: pulse 1s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.playing-time {
  margin-left: auto;
  font-family: monospace;
  color: #d4a84b;
}

.song-body {
  display: flex;
  gap: 24px;
  margin-top: 24px;
}

/* 左侧歌词 - 中华风 */
.lyrics-box {
  flex: 2;
  background: #fffef9;
  padding: 20px;
  border-radius: 8px;
  border: 1px solid rgba(212, 168, 75, 0.15);
}

.lyrics-box h3,
.comments-box h3 {
  font-size: 16px;
  font-weight: 600;
  color: #1a1a1a;
  padding-left: 12px;
  position: relative;
  letter-spacing: 1px;
  margin: 0;
}

.lyrics-box h3::before,
.comments-box h3::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 16px;
  background: linear-gradient(180deg, #2d5a5a, #d4a84b);
  border-radius: 2px;
}

.lyrics-container {
  margin-top: 12px;
  max-height: 300px;
  overflow-y: auto;
  padding: 10px 0;
}

.lyric-line {
  padding: 8px 12px;
  font-size: 14px;
  line-height: 1.8;
  color: #666;
  transition: all 0.3s;
  border-radius: 4px;
}

.lyric-line.active {
  color: #2d5a5a;
  font-weight: 500;
  font-size: 15px;
  background: rgba(45, 90, 90, 0.05);
}

.no-lyrics {
  text-align: center;
  color: #999;
  padding: 40px 0;
}

/* 右侧评论 - 中华风 */
.comments-box {
  flex: 3;
  background: #fffef9;
  padding: 20px;
  border-radius: 8px;
  border: 1px solid rgba(212, 168, 75, 0.15);
}

.comment-list {
  list-style: none;
  padding: 0;
  margin: 12px 0;
}

.comment-item {
  padding: 12px 0;
  border-bottom: 1px solid rgba(212, 168, 75, 0.1);
}

.comment-meta {
  font-size: 12px;
  color: #999;
  margin-bottom: 4px;
}

.comment-content {
  font-size: 14px;
  color: #333;
  line-height: 1.6;
}

.comment-form textarea {
  width: 100%;
  min-height: 80px;
  margin-top: 12px;
  padding: 10px 12px;
  font-size: 14px;
  border-radius: 4px;
  border: 1px solid rgba(212, 168, 75, 0.3);
  resize: vertical;
  box-sizing: border-box;
  background: #fff;
  transition: all 0.3s;
  font-family: inherit;
}

.comment-form textarea:focus {
  outline: none;
  border-color: #d4a84b;
  box-shadow: 0 0 0 2px rgba(212, 168, 75, 0.1);
}

.comment-form .btn {
  margin-top: 10px;
}

.comment-msg {
  font-size: 12px;
  color: #999;
  margin-top: 6px;
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
.playlist-list { display: flex; flex-direction: column; gap: 8px; }
.playlist-item { display: flex; align-items: center; gap: 12px; padding: 12px; border-radius: 4px; cursor: pointer; transition: all 0.3s; border: 1px solid transparent; }
.playlist-item:hover { background: rgba(212, 168, 75, 0.1); border-color: rgba(212, 168, 75, 0.2); }
.playlist-icon { width: 40px; height: 40px; border-radius: 4px; background: linear-gradient(135deg, rgba(255,255,255,0.4) 0%, #8BA8A8 50%, #7a9999 100%); color: #d4a84b; display: flex; align-items: center; justify-content: center; font-size: 18px; }
.playlist-info { flex: 1; }
.playlist-name { font-size: 14px; color: #1a1a1a; margin-bottom: 2px; }
.playlist-count { font-size: 12px; color: #999; }

@media (max-width: 768px) {
  .song-header { flex-direction: column; align-items: center; text-align: center; }
  .cover-box { width: 180px; height: 180px; }
  .action-row { justify-content: center; }
  .song-body { flex-direction: column; }
}
</style>