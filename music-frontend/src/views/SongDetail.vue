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
        <div v-else class="cover-placeholder">♪</div>
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
              {{ c.username }} · {{ c.created_at }}<span v-if="c.location" class="comment-location"> · IP属地：{{ c.location }}</span>
            </div>
            <div class="comment-content">{{ c.content }}</div>
            <div class="comment-actions">
              <span class="action-btn like-btn" :class="{ liked: c.is_liked }" @click="toggleLike(c)">
                <svg viewBox="0 0 24 24" width="14" height="14"><path fill="currentColor" d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/></svg>
                {{ c.like_count || 0 }}
              </span>
              <span class="action-btn reply-btn" @click="showReplyInput(c)">
                <svg viewBox="0 0 24 24" width="14" height="14"><path fill="currentColor" d="M10 9V5l-7 7 7 7v-4.1c5 0 8.5 1.6 11 5.1-1-5-4-10-11-11z"/></svg>
                回复 {{ c.reply_count || 0 }}
              </span>
              <span v-if="canDeleteComment(c)" class="action-btn delete-btn" @click="deleteComment(c)">
                <svg viewBox="0 0 24 24" width="14" height="14"><path fill="currentColor" d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/></svg>
                删除
              </span>
            </div>
            <!-- 回复输入框 -->
            <div v-if="replyingTo === c.id" class="reply-input-box">
              <textarea v-model="replyText" :placeholder="'回复 ' + c.username + '……'" rows="2"></textarea>
              <div class="reply-btns">
                <button class="btn small" @click="cancelReply">取消</button>
                <button class="btn small primary" @click="submitReply(c)">发送</button>
              </div>
            </div>
            <!-- 回复列表 -->
            <div v-if="c.replies && c.replies.length > 0" class="replies-list">
              <div v-for="r in c.replies" :key="r.id" class="reply-item">
                <div class="reply-meta">
                  {{ r.username }} · {{ r.created_at }}<span v-if="r.location" class="comment-location"> · IP属地：{{ r.location }}</span>
                </div>
                <div class="reply-content">{{ r.content }}</div>
                <div class="comment-actions">
                  <span class="action-btn like-btn" :class="{ liked: r.is_liked }" @click="toggleLike(r)">
                    <svg viewBox="0 0 24 24" width="14" height="14"><path fill="currentColor" d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/></svg>
                    {{ r.like_count || 0 }}
                  </span>
                  <span v-if="canDeleteComment(r)" class="action-btn delete-btn" @click="deleteComment(r)">
                    <svg viewBox="0 0 24 24" width="14" height="14"><path fill="currentColor" d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/></svg>
                    删除
                  </span>
                </div>
              </div>
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
import { playerState, playSong, formatDuration, pauseSong, resumeSong } from "../stores/player";

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

// 回复相关
const replyingTo = ref(null);
const replyText = ref("");

// 当前用户信息
const currentUserId = ref(null);
const isAdmin = ref(false);

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
  const userId = localStorage.getItem("user_id");
  const url = userId ? `/songs/${songId}/comments?user_id=${userId}` : `/songs/${songId}/comments`;
  const res = await api.get(url);
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
      pauseSong();
    } else {
      resumeSong();
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

// 点赞评论
const toggleLike = async (comment) => {
  const userId = localStorage.getItem("user_id");
  if (!userId) {
    alert("请先登录");
    router.push("/login");
    return;
  }
  try {
    const res = await api.post(`/comments/${comment.id}/like`, { user_id: Number(userId) });
    comment.is_liked = res.data.is_liked;
    comment.like_count = comment.is_liked ? (comment.like_count || 0) + 1 : Math.max(0, (comment.like_count || 1) - 1);
  } catch (e) {
    console.error("点赞失败", e);
  }
};

// 显示回复输入框
const showReplyInput = (comment) => {
  const userId = localStorage.getItem("user_id");
  if (!userId) {
    alert("请先登录");
    router.push("/login");
    return;
  }
  replyingTo.value = comment.id;
  replyText.value = "";
};

// 取消回复
const cancelReply = () => {
  replyingTo.value = null;
  replyText.value = "";
};

// 提交回复
const submitReply = async (parentComment) => {
  const userId = localStorage.getItem("user_id");
  if (!userId) {
    alert("请先登录");
    router.push("/login");
    return;
  }
  if (!replyText.value.trim()) {
    alert("回复内容不能为空");
    return;
  }
  try {
    await api.post(`/songs/${songId}/comments`, {
      user_id: Number(userId),
      content: replyText.value,
      parent_id: parentComment.id
    });
    replyingTo.value = null;
    replyText.value = "";
    loadComments();
  } catch (e) {
    const data = e.response?.data;
    if (data?.reason) {
      alert(`${data.msg}：${data.reason}`);
    } else {
      alert(data?.msg || "回复失败");
    }
  }
};

// 判断是否可以删除评论
const canDeleteComment = (comment) => {
  if (!currentUserId.value) return false;
  return comment.user_id === currentUserId.value || isAdmin.value;
};

// 删除评论
const deleteComment = async (comment) => {
  if (!confirm("确定要删除这条评论吗？")) return;
  try {
    await api.delete(`/comments/${comment.id}?user_id=${currentUserId.value}`);
    loadComments();
  } catch (e) {
    alert(e.response?.data?.msg || "删除失败");
  }
};

onMounted(() => {
  // 滚动到页面顶部
  window.scrollTo(0, 0);
  // 获取当前用户信息
  currentUserId.value = Number(localStorage.getItem("user_id")) || null;
  isAdmin.value = localStorage.getItem("is_admin") === "1";
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
  border-radius: 8px;
  overflow: hidden;
  background: linear-gradient(135deg, rgba(255,255,255,0.4) 0%, #8BA8A8 50%, #7a9999 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid #d4a84b;
  box-shadow: 0 8px 25px rgba(139, 168, 168, 0.3);
  flex-shrink: 0;
  position: relative;
}

.cover-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cover-placeholder {
  font-size: 48px;
  color: #2d5a5a;
}

/* 无封面时显示音符图标 */
.cover-box:not(:has(.cover-img)) .cover-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
}

.cover-box:not(:has(.cover-img))::before {
  content: '♪';
  position: absolute;
  font-size: 48px;
  color: #2d5a5a;
  opacity: 0.8;
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
  padding: 10px 24px;
  border-radius: 20px;
  border: 1px solid #d4a84b;
  background: rgba(255, 255, 255, 0.9);
  color: #2d5a5a;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.3s;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  letter-spacing: 1px;
}

.btn:hover {
  background: #fff;
  box-shadow: 0 2px 8px rgba(212, 168, 75, 0.3);
}

.btn.primary {
  background: rgba(255, 255, 255, 0.9);
  border-color: #d4a84b;
  color: #2d5a5a;
}

.btn.primary:hover {
  background: #fff;
  box-shadow: 0 2px 8px rgba(212, 168, 75, 0.3);
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

.comment-location {
  color: #2d5a5a;
  font-size: 11px;
  margin-left: 2px;
}

.comment-content {
  font-size: 14px;
  color: #333;
  line-height: 1.6;
}

.comment-actions {
  display: flex;
  gap: 16px;
  margin-top: 8px;
}

.action-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #999;
  cursor: pointer;
  transition: all 0.3s;
}

.action-btn:hover {
  color: #666;
}

.like-btn.liked {
  color: #e74c3c;
}

.like-btn.liked svg {
  fill: #e74c3c;
}

.delete-btn:hover {
  color: #e74c3c;
}

.reply-input-box {
  margin-top: 10px;
  padding: 10px;
  background: rgba(45, 90, 90, 0.03);
  border-radius: 4px;
}

.reply-input-box textarea {
  width: 100%;
  padding: 8px;
  font-size: 13px;
  border: 1px solid rgba(212, 168, 75, 0.3);
  border-radius: 4px;
  resize: none;
  box-sizing: border-box;
  font-family: inherit;
}

.reply-input-box textarea:focus {
  outline: none;
  border-color: #d4a84b;
}

.reply-btns {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 8px;
}

.btn.small {
  padding: 5px 12px;
  font-size: 12px;
}

.replies-list {
  margin-top: 10px;
  padding-left: 16px;
  border-left: 2px solid rgba(212, 168, 75, 0.2);
}

.reply-item {
  padding: 8px 0;
  border-bottom: 1px dashed rgba(212, 168, 75, 0.1);
}

.reply-item:last-child {
  border-bottom: none;
}

.reply-meta {
  font-size: 11px;
  color: #999;
  margin-bottom: 4px;
}

.reply-content {
  font-size: 13px;
  color: #444;
  line-height: 1.5;
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