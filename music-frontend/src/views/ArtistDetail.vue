<template>
  <div class="artist-detail-container">
    <!-- 歌手信息头部 -->
    <div class="artist-header">
      <div class="artist-avatar">
        <img v-if="artist.avatar_url" :src="artist.avatar_url" alt="" />
        <span v-else class="avatar-placeholder">{{ artist.name?.charAt(0) }}</span>
      </div>
      <div class="artist-info">
        <h1 class="artist-name">{{ artist.name }}</h1>
        <div class="artist-stats">
          <span class="stat-item">
            <strong>{{ artist.song_count || 0 }}</strong> 首歌曲
          </span>
          <span class="stat-item">
            <strong>{{ artist.follower_count || 0 }}</strong> 粉丝
          </span>
        </div>
        <p class="artist-desc" v-if="artist.description">{{ artist.description }}</p>
        <button 
          class="follow-btn" 
          :class="{ followed: artist.is_followed }"
          @click="toggleFollow"
        >
          {{ artist.is_followed ? '已关注' : '+ 关注' }}
        </button>
      </div>
    </div>

    <!-- 歌曲列表 -->
    <div class="songs-section">
      <div class="section-header">
        <h3>歌曲列表</h3>
        <button class="play-all-btn" @click="playAll" v-if="songs.length > 0">
          <svg viewBox="0 0 24 24" width="16" height="16">
            <path fill="currentColor" d="M8 5v14l11-7z"/>
          </svg>
          播放全部
        </button>
      </div>

      <div class="song-list">
        <div 
          v-for="(song, index) in songs" 
          :key="song.id" 
          class="song-item"
          @click="playSong(song)"
        >
          <span class="song-index" :class="{ top: index < 3 }">{{ index + 1 }}</span>
          <div class="song-cover">
            <img v-if="song.cover_url" :src="song.cover_url" alt="" />
            <span v-else class="cover-placeholder">♪</span>
          </div>
          <div class="song-info">
            <div class="song-title">{{ song.title }}</div>
            <div class="song-album">{{ song.album || '未知专辑' }}</div>
          </div>
          <span class="song-duration">{{ formatDuration(song.duration) }}</span>
          <span class="song-plays">{{ formatPlayCount(song.play_count) }} 次播放</span>
          <button class="fav-btn" :class="{ active: favoriteIds.has(song.id) }" @click.stop="toggleFavorite(song)">
            <svg viewBox="0 0 24 24" width="18" height="18">
              <path fill="currentColor" d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
            </svg>
          </button>
        </div>
      </div>

      <div v-if="songs.length === 0" class="empty-state">
        该歌手暂无歌曲
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import api from '../api';
import { playSong as playTrack, formatDuration } from '../stores/player';

const route = useRoute();
const router = useRouter();
const artist = ref({});
const songs = ref([]);
const favoriteIds = ref(new Set());

const loadArtist = async () => {
  const artistId = route.params.id;
  const userId = localStorage.getItem('user_id');
  try {
    const res = await api.get(`/artists/${artistId}`, {
      params: { user_id: userId || undefined }
    });
    artist.value = res.data;
    songs.value = res.data.songs || [];
  } catch (e) {
    console.error('加载歌手详情失败', e);
  }
};

const loadFavorites = async () => {
  const userId = localStorage.getItem('user_id');
  if (!userId) return;
  try {
    const res = await api.get(`/users/${userId}/favorites`);
    favoriteIds.value = new Set(res.data.map(s => s.id));
  } catch (e) {
    console.error('加载收藏失败', e);
  }
};

const toggleFollow = async () => {
  const userId = localStorage.getItem('user_id');
  if (!userId) {
    alert('请先登录');
    router.push('/login');
    return;
  }
  try {
    const res = await api.post(`/artists/${artist.value.id}/follow`, { user_id: Number(userId) });
    artist.value.is_followed = res.data.is_followed;
    artist.value.follower_count = res.data.follower_count;
  } catch (e) {
    console.error('关注失败', e);
  }
};

const toggleFavorite = async (song) => {
  const userId = localStorage.getItem('user_id');
  if (!userId) {
    alert('请先登录');
    router.push('/login');
    return;
  }
  try {
    await api.post(`/songs/${song.id}/favorite`, { user_id: Number(userId) });
    if (favoriteIds.value.has(song.id)) {
      favoriteIds.value.delete(song.id);
    } else {
      favoriteIds.value.add(song.id);
    }
    favoriteIds.value = new Set(favoriteIds.value);
  } catch (e) {
    console.error('收藏失败', e);
  }
};

const playSong = (song) => {
  playTrack(song, songs.value);
};

const playAll = () => {
  if (songs.value.length > 0) {
    playTrack(songs.value[0], songs.value);
  }
};

const formatPlayCount = (count) => {
  if (!count) return '0';
  if (count >= 10000) return (count / 10000).toFixed(1) + '万';
  return count.toString();
};

onMounted(() => {
  loadArtist();
  loadFavorites();
});
</script>

<style scoped>
.artist-detail-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}

.artist-header {
  display: flex;
  gap: 32px;
  padding: 32px;
  background: linear-gradient(135deg, #E6F4EA 0%, #fffef9 100%);
  border-radius: 12px;
  margin-bottom: 32px;
  border: 1px solid rgba(212, 168, 75, 0.15);
}

.artist-avatar {
  width: 180px;
  height: 180px;
  border-radius: 50%;
  overflow: hidden;
  background: linear-gradient(135deg, #8BA8A8, #7a9999);
  flex-shrink: 0;
  box-shadow: 0 8px 24px rgba(45, 90, 90, 0.2);
}

.artist-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 64px;
  color: #fff;
  font-weight: 600;
}

.artist-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.artist-name {
  font-size: 32px;
  font-weight: 700;
  color: #2d5a5a;
  margin: 0 0 16px;
  letter-spacing: 2px;
}

.artist-stats {
  display: flex;
  gap: 24px;
  margin-bottom: 16px;
}

.stat-item {
  font-size: 14px;
  color: #666;
}

.stat-item strong {
  font-size: 20px;
  color: #d4a84b;
  margin-right: 4px;
}

.artist-desc {
  font-size: 14px;
  color: #666;
  line-height: 1.6;
  margin: 0 0 20px;
}

.follow-btn {
  width: fit-content;
  padding: 10px 32px;
  border: 2px solid #d4a84b;
  background: transparent;
  color: #d4a84b;
  border-radius: 24px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.follow-btn:hover {
  background: rgba(212, 168, 75, 0.1);
}

.follow-btn.followed {
  background: #d4a84b;
  color: #fff;
}

.follow-btn.followed:hover {
  background: #c49840;
}

.songs-section {
  background: #fffef9;
  border-radius: 12px;
  padding: 24px;
  border: 1px solid rgba(212, 168, 75, 0.15);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(212, 168, 75, 0.15);
}

.section-header h3 {
  font-size: 18px;
  color: #2d5a5a;
  margin: 0;
}

.play-all-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 20px;
  background: linear-gradient(135deg, #2d5a5a, #3d7a7a);
  color: #fff;
  border: none;
  border-radius: 20px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.3s;
}

.play-all-btn:hover {
  background: linear-gradient(135deg, #3d7a7a, #4d8a8a);
  transform: translateY(-2px);
}

.song-list {
  display: flex;
  flex-direction: column;
}

.song-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 16px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.song-item:hover {
  background: rgba(45, 90, 90, 0.05);
}

.song-index {
  width: 28px;
  font-size: 14px;
  color: #999;
  text-align: center;
}

.song-index.top {
  color: #d4a84b;
  font-weight: 700;
}

.song-cover {
  width: 48px;
  height: 48px;
  border-radius: 6px;
  overflow: hidden;
  background: linear-gradient(135deg, #8BA8A8, #7a9999);
  flex-shrink: 0;
}

.song-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cover-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: #fff;
}

.song-info {
  flex: 1;
  min-width: 0;
}

.song-title {
  font-size: 14px;
  color: #333;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.song-album {
  font-size: 12px;
  color: #999;
}

.song-duration {
  width: 50px;
  font-size: 13px;
  color: #999;
  text-align: right;
}

.song-plays {
  width: 80px;
  font-size: 12px;
  color: #999;
  text-align: right;
}

.fav-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: none;
  color: #ccc;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.fav-btn:hover {
  color: #ff6b6b;
}

.fav-btn.active {
  color: #ff6b6b;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #999;
  font-size: 14px;
}
</style>
