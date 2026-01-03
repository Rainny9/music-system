<template>
  <div class="artists-container">
    <div class="page-header">
      <h2>🎤 歌手</h2>
      <div class="search-box">
        <input v-model="keyword" placeholder="搜索歌手" @keyup.enter="loadArtists" />
        <button @click="loadArtists">搜索</button>
      </div>
    </div>

    <div class="artists-grid">
      <div v-for="artist in artists" :key="artist.id" class="artist-card" @click="goDetail(artist.id)">
        <div class="artist-avatar">
          <img v-if="artist.avatar_url" :src="artist.avatar_url" alt="" />
          <span v-else class="avatar-placeholder">{{ artist.name?.charAt(0) }}</span>
        </div>
        <div class="artist-info">
          <div class="artist-name">{{ artist.name }}</div>
          <div class="artist-stats">
            <span>{{ artist.song_count || 0 }} 首歌曲</span>
            <span>{{ artist.follower_count || 0 }} 粉丝</span>
          </div>
        </div>
        <button 
          class="follow-btn" 
          :class="{ followed: artist.is_followed }"
          @click.stop="toggleFollow(artist)"
        >
          {{ artist.is_followed ? '已关注' : '+ 关注' }}
        </button>
      </div>
    </div>

    <div v-if="artists.length === 0" class="empty-state">
      暂无歌手数据
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import api from '../api';

const router = useRouter();
const artists = ref([]);
const keyword = ref('');

const loadArtists = async () => {
  try {
    const userId = localStorage.getItem('user_id');
    const res = await api.get('/artists', { 
      params: { 
        keyword: keyword.value || undefined,
        user_id: userId || undefined
      } 
    });
    // 检查每个歌手的关注状态
    if (userId) {
      const followRes = await api.get(`/users/${userId}/following`);
      const followedIds = new Set(followRes.data.map(a => a.id));
      artists.value = res.data.map(a => ({
        ...a,
        is_followed: followedIds.has(a.id)
      }));
    } else {
      artists.value = res.data;
    }
  } catch (e) {
    console.error('加载歌手失败', e);
  }
};

const toggleFollow = async (artist) => {
  const userId = localStorage.getItem('user_id');
  if (!userId) {
    alert('请先登录');
    router.push('/login');
    return;
  }
  try {
    const res = await api.post(`/artists/${artist.id}/follow`, { user_id: Number(userId) });
    artist.is_followed = res.data.is_followed;
    artist.follower_count = res.data.follower_count;
  } catch (e) {
    console.error('关注失败', e);
  }
};

const goDetail = (id) => {
  router.push(`/artists/${id}`);
};

onMounted(() => {
  loadArtists();
});
</script>

<style scoped>
.artists-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(212, 168, 75, 0.2);
}

.page-header h2 {
  font-size: 24px;
  color: #2d5a5a;
  margin: 0;
  letter-spacing: 2px;
}

.search-box {
  display: flex;
  gap: 8px;
}

.search-box input {
  padding: 8px 14px;
  border: 1px solid rgba(45, 90, 90, 0.3);
  border-radius: 4px;
  font-size: 14px;
  width: 200px;
  outline: none;
}

.search-box input:focus {
  border-color: #d4a84b;
}

.search-box button {
  padding: 8px 16px;
  background: linear-gradient(135deg, #2d5a5a, #3d7a7a);
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.search-box button:hover {
  background: linear-gradient(135deg, #3d7a7a, #4d8a8a);
}

.artists-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.artist-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: linear-gradient(135deg, #fffef9, #f5f5f0);
  border: 1px solid rgba(212, 168, 75, 0.15);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.artist-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(45, 90, 90, 0.12);
  border-color: rgba(45, 90, 90, 0.3);
}

.artist-avatar {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  overflow: hidden;
  background: linear-gradient(135deg, #8BA8A8, #7a9999);
  flex-shrink: 0;
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
  font-size: 24px;
  color: #fff;
  font-weight: 600;
}

.artist-info {
  flex: 1;
  min-width: 0;
}

.artist-name {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 6px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.artist-stats {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: #999;
}

.follow-btn {
  padding: 6px 16px;
  border: 1px solid #d4a84b;
  background: transparent;
  color: #d4a84b;
  border-radius: 20px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.3s;
  white-space: nowrap;
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

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #999;
  font-size: 14px;
}
</style>
