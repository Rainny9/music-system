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
    msg.value = e.response?.data?.msg || "评论失败";
  }
};

onMounted(() => {
  // 滚动到页面顶部
  window.scrollTo(0, 0);
  loadSongDetail();
  loadComments();
});
</script>

<style scoped>
.song-detail-page {
  padding: 24px 0;
}

.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  margin-top: 0;
  margin-bottom: 16px;
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 20px;
  font-size: 14px;
  color: #666;
  cursor: pointer;
  transition: all 0.2s;
}

.back-btn:hover {
  background: #f5f5f5;
  color: #31c27c;
  border-color: #31c27c;
}

.song-header {
  display: flex;
  gap: 24px;
  background: #ffffff;
  padding: 20px 24px;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
}

.cover-box {
  width: 220px;
  height: 220px;
  border-radius: 4px;
  overflow: hidden;
  background: #f0f2f5;
  display: flex;
  align-items: center;
  justify-content: center;
}

.cover-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cover-placeholder {
  font-size: 42px;
  color: #999;
}

.info-box {
  flex: 1;
}

.song-title {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 8px;
}

.song-artist {
  font-size: 14px;
  color: #666;
  margin-bottom: 4px;
}

.song-meta {
  font-size: 13px;
  color: #999;
  margin-bottom: 4px;
}

.action-row {
  margin: 16px 0 8px;
  display: flex;
  gap: 12px;
}

.btn {
  padding: 6px 16px;
  border-radius: 16px;
  border: 1px solid #dcdfe6;
  background: #ffffff;
  color: #606266;
  font-size: 13px;
  cursor: pointer;
}

.btn.primary {
  background: #409eff;
  border-color: #409eff;
  color: #fff;
}

.now-playing-info {
  margin-top: 12px;
  padding: 10px 16px;
  background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
  color: #2e7d32;
}

.playing-icon {
  font-size: 16px;
  animation: pulse 1s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.playing-time {
  margin-left: auto;
  font-family: monospace;
}

.song-body {
  display: flex;
  gap: 24px;
  margin-top: 20px;
}

/* 左侧歌词 */
.lyrics-box {
  flex: 2;
  background: #ffffff;
  padding: 16px 20px;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
}

.lyrics-container {
  margin-top: 8px;
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
  color: #31c27c;
  font-weight: 500;
  font-size: 15px;
  background: #f0fff0;
}

.no-lyrics {
  text-align: center;
  color: #999;
  padding: 40px 0;
}

/* 右侧评论 */
.comments-box {
  flex: 3;
  background: #ffffff;
  padding: 16px 20px;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
}

.comment-list {
  list-style: none;
  padding: 0;
  margin: 8px 0 12px;
}

.comment-item {
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.comment-meta {
  font-size: 12px;
  color: #999;
  margin-bottom: 2px;
}

.comment-content {
  font-size: 13px;
  color: #333;
}

.comment-form textarea {
  width: 100%;
  min-height: 60px;
  margin-top: 8px;
  padding: 6px 8px;
  font-size: 13px;
  border-radius: 4px;
  border: 1px solid #dcdfe6;
  resize: vertical;
  box-sizing: border-box;
}

.comment-form .btn {
  margin-top: 8px;
}

.comment-msg {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}
</style>