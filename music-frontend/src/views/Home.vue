<template>
  <div class="home-container">
    <!-- 细分导航 -->
    <div class="sub-nav">
      <span 
        v-for="nav in subNavList" 
        :key="nav.key" 
        class="sub-nav-item"
        :class="{ active: activeSubNav === nav.key }"
        @click="activeSubNav = nav.key"
      >{{ nav.label }}</span>
    </div>

    <!-- 首页内容 -->
    <template v-if="activeSubNav === 'home'">
      <!-- 轮播图 -->
      <!-- 公告 -->
      <div v-if="announcements.length > 0" class="announcement-section">
          <div class="ann-header">
            <svg viewBox="0 0 24 24" width="16" height="16">
              <path fill="#ff9800" d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z"/>
            </svg>
            <span>公告</span>
          </div>
          <div class="ann-list">
            <div v-for="ann in announcements.slice(0, 4)" :key="ann.id" class="ann-item" @click="showAnnouncementDetail(ann)">
              <span class="ann-dot">•</span>
              <span class="ann-text">{{ ann.title }}</span>
            </div>
          </div>
        </div>

      <!-- 为你推荐（AI智能推荐 + 热门歌曲合并） -->
      <div class="section">
        <div class="section-header">
          <h3>🎵 为你推荐</h3>
          <div class="header-right">
            <span v-if="recommendType === 'personalized'" class="ai-badge">AI智能推荐</span>
            <span class="more" @click="activeSubNav = 'category'">更多 ›</span>
          </div>
        </div>
        <div v-if="aiLoading" class="ai-loading">AI正在分析你的喜好...</div>
        <div v-else class="song-grid">
          <div v-for="song in recommendedSongs" :key="song.id" class="song-card" :class="{ 'ai-card': recommendType === 'personalized' }">
            <div class="card-cover" @click="play(song)">
              <img v-if="song.cover_url" :src="song.cover_url" alt="" />
              <div v-else class="cover-placeholder">♪</div>
              <div class="play-overlay">
                <svg viewBox="0 0 24 24" width="32" height="32">
                  <path fill="#fff" d="M8 5v14l11-7z"/>
                </svg>
              </div>
            </div>
            <div class="card-info" @click="goDetail(song.id)">
              <div class="card-title">{{ song.title }}</div>
              <div class="card-artist">{{ song.artist || '未知歌手' }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 最新上传 -->
      <div class="section">
        <div class="section-header">
          <h3>最新上传</h3>
        </div>
        <div class="song-list-simple">
          <div v-for="(song, index) in latestSongs.slice(0, 10)" :key="song.id" class="song-row">
            <span class="row-index" :class="{ top: index < 3 }" @click="play(song)">{{ index + 1 }}</span>
            <span class="row-title clickable" @click="goDetail(song.id)">{{ song.title }}</span>
            <span class="row-artist">{{ song.artist || '未知' }}</span>
            <span class="row-duration">{{ formatDuration(song.duration) }}</span>
            <button class="row-fav" :class="{ active: favoriteIds.has(song.id) }" @click.stop="toggleFavorite(song)">
              <svg viewBox="0 0 24 24" width="16" height="16">
                <path fill="currentColor" d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </template>

    <!-- 歌曲分类 -->
    <template v-if="activeSubNav === 'category'">
      <div class="category-section">
        <div class="category-row">
          <span class="category-label">流派</span>
          <div class="category-tags">
            <span class="tag" :class="{ active: selectedGenre === '' }" @click="selectGenre('')">全部</span>
            <span v-for="g in genreList" :key="g" class="tag" :class="{ active: selectedGenre === g }" @click="selectGenre(g)">{{ g }}</span>
          </div>
        </div>
        <div class="category-row">
          <span class="category-label">语种</span>
          <div class="category-tags">
            <span class="tag" :class="{ active: selectedLanguage === '' }" @click="selectLanguage('')">全部</span>
            <span v-for="lang in languageList" :key="lang" class="tag" :class="{ active: selectedLanguage === lang }" @click="selectLanguage(lang)">{{ lang }}</span>
          </div>
        </div>
        <div class="category-row">
          <span class="category-label">主题</span>
          <div class="category-tags">
            <span class="tag" :class="{ active: selectedTheme === '' }" @click="selectTheme('')">全部</span>
            <span v-for="theme in themeList" :key="theme" class="tag" :class="{ active: selectedTheme === theme }" @click="selectTheme(theme)">{{ theme }}</span>
          </div>
        </div>
        <div class="category-row">
          <span class="category-label">场景</span>
          <div class="category-tags">
            <span class="tag" :class="{ active: selectedScene === '' }" @click="selectScene('')">全部</span>
            <span v-for="scene in sceneList" :key="scene" class="tag" :class="{ active: selectedScene === scene }" @click="selectScene(scene)">{{ scene }}</span>
          </div>
        </div>
        <div class="category-row">
          <span class="category-label">心情</span>
          <div class="category-tags">
            <span class="tag" :class="{ active: selectedMood === '' }" @click="selectMood('')">全部</span>
            <span v-for="mood in moodList" :key="mood" class="tag" :class="{ active: selectedMood === mood }" @click="selectMood(mood)">{{ mood }}</span>
          </div>
        </div>
      </div>

      <!-- 筛选结果 -->
      <div class="action-bar">
        <button class="action-btn primary" @click="playAll">
          <svg viewBox="0 0 24 24" width="16" height="16"><path fill="currentColor" d="M8 5v14l11-7z"/></svg>
          播放全部
        </button>
        <span class="song-total">共 {{ songs.length }} 首</span>
      </div>

      <div class="song-list-header">
        <span class="col-index"></span>
        <span class="col-title">歌曲</span>
        <span class="col-artist">歌手</span>
        <span class="col-album">专辑</span>
        <span class="col-duration">时长</span>
        <span class="col-actions">操作</span>
      </div>

      <div class="song-list">
        <div v-for="(song, index) in songs" :key="song.id" class="song-item" :class="{ playing: playerState.currentSong?.id === song.id }">
          <span class="col-index">
            <span class="index-number">{{ index + 1 }}</span>
            <button class="play-btn" @click="play(song)">
              <svg viewBox="0 0 24 24" width="20" height="20"><path fill="currentColor" d="M8 5v14l11-7z"/></svg>
            </button>
          </span>
          <span class="col-title" @click="goDetail(song.id)">{{ song.title }}</span>
          <span class="col-artist">{{ song.artist || '未知歌手' }}</span>
          <span class="col-album">{{ song.album || '未知专辑' }}</span>
          <span class="col-duration">{{ formatDuration(song.duration) }}</span>
          <span class="col-actions">
            <button class="icon-btn" :class="{ favorited: favoriteIds.has(song.id) }" @click="toggleFavorite(song)" title="收藏">
              <svg viewBox="0 0 24 24" width="18" height="18"><path fill="currentColor" d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/></svg>
            </button>
            <button class="icon-btn" @click.stop="openAddToPlaylist(song)" title="添加到歌单">
              <svg viewBox="0 0 24 24" width="18" height="18"><path fill="currentColor" d="M14 10H2v2h12v-2zm0-4H2v2h12V6zm4 8v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zM2 16h8v-2H2v2z"/></svg>
            </button>
            <a class="icon-btn" :href="song.download_url" target="_blank" title="下载"><svg viewBox="0 0 24 24" width="18" height="18"><path fill="currentColor" d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/></svg></a>
          </span>
        </div>
        <div v-if="songs.length === 0" class="empty-state">暂无歌曲</div>
      </div>
    </template>

    <!-- 排行榜 -->
    <template v-if="activeSubNav === 'rank'">
      <div class="rank-section">
        <div class="rank-header">
          <h3>🏆 热歌榜</h3>
          <span class="rank-update-time" v-if="rankingUpdateTime">更新于 {{ rankingUpdateTime }}</span>
        </div>
        <div class="rank-list">
          <div v-for="song in rankingList" :key="song.id" class="rank-item" @click="play(song)">
            <span class="rank-num" :class="{ top: song.current_rank <= 3 }">{{ song.current_rank }}</span>
            <div class="rank-info">
              <div class="rank-title">{{ song.title }}</div>
              <div class="rank-artist">{{ song.artist || '未知歌手' }}</div>
            </div>
            <div class="rank-change">
              <template v-if="song.is_new">
                <span class="rank-new">NEW</span>
              </template>
              <template v-else-if="song.rank_change > 0">
                <span class="rank-up">▲ {{ song.rank_change }}</span>
              </template>
              <template v-else-if="song.rank_change < 0">
                <span class="rank-down">▼ {{ Math.abs(song.rank_change) }}</span>
              </template>
              <template v-else>
                <span class="rank-same">-</span>
              </template>
            </div>
            <span class="rank-play-count">{{ formatPlayCount(song.play_count) }}次播放</span>
            <span class="rank-duration">{{ formatDuration(song.duration) }}</span>
          </div>
        </div>
      </div>
    </template>

    <!-- 公告弹窗 -->
    <div v-if="showAnnModal" class="modal-overlay" @click.self="showAnnModal = false">
      <div class="ann-modal">
        <div class="ann-modal-header">
          <h3>{{ currentAnn.title }}</h3>
          <button class="close-btn" @click="showAnnModal = false">×</button>
        </div>
        <div class="ann-modal-body">
          <p class="ann-content">{{ currentAnn.content }}</p>
          <p class="ann-time">发布时间：{{ formatAnnDate(currentAnn.created_at) }}</p>
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
import { ref, onMounted, onUnmounted } from "vue";
import { computed } from "vue";
import api from "../api";
import { useRouter } from "vue-router";
import { playerState, playSong, formatDuration } from "../stores/player";

const router = useRouter();
const songs = ref([]);
const favoriteIds = ref(new Set());
const aiRecommendations = ref([]);
const latestSongs = ref([]); // 最新上传歌曲
const aiLoading = ref(false);
const recommendType = ref('popular'); // 'personalized' 或 'popular'

// 推荐歌曲（使用AI智能排序结果）
const recommendedSongs = computed(() => {
  return aiRecommendations.value.slice(0, 8);
});

// 排行榜相关
const rankingList = ref([]);
const rankingUpdateTime = ref('');

// 添加到歌单相关
const showPlaylistModal = ref(false);
const userPlaylists = ref([]);
const selectedSongForPlaylist = ref(null);

// 细分导航
const subNavList = [
  { key: 'home', label: '首页' },
  { key: 'category', label: '歌曲分类' },
  { key: 'rank', label: '排行榜' },
];
const activeSubNav = ref('home');

// ==================== 轮播图配置 ====================
// 修改此数组来更换轮播图内容
// 每个对象包含:
//   - title: 标题文字
//   - desc: 描述文字
//   - icon: 图标(emoji或文字)
//   - bg: 背景样式(可以是渐变色或图片URL)
//        渐变色格式: 'linear-gradient(135deg, #颜色1 0%, #颜色2 100%)'
//        图片格式: 'url(/path/to/image.jpg) center/cover'
//   - image: (可选) 如果设置了image，将显示图片而不是渐变背景
// =====================================================
const carouselSlides = [
  { 
    title: '热门推荐', 
    desc: '精选热门歌曲，每日更新', 
    icon: '🎵', 
    bg: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
    // 如需使用图片，取消下行注释并填入图片路径:
    // image: '/images/banner1.jpg'
  },
  { 
    title: '新歌首发', 
    desc: '最新音乐抢先听', 
    icon: '🎧', 
    bg: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)'
    // image: '/images/banner2.jpg'
  },
  { 
    title: '经典回顾', 
    desc: '那些年我们听过的歌', 
    icon: '🎤', 
    bg: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)'
    // image: '/images/banner3.jpg'
  },
  { 
    title: '私人FM', 
    desc: '根据你的口味推荐', 
    icon: '📻', 
    bg: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)'
    // image: '/images/banner4.jpg'
  },
];
// ==================== 轮播图配置结束 ====================
const carouselIndex = ref(0);
let carouselTimer = null;

const nextSlide = () => {
  carouselIndex.value = (carouselIndex.value + 1) % carouselSlides.length;
};
const prevSlide = () => {
  carouselIndex.value = (carouselIndex.value - 1 + carouselSlides.length) % carouselSlides.length;
};
const startCarousel = () => {
  carouselTimer = setInterval(nextSlide, 4000);
};
const stopCarousel = () => {
  if (carouselTimer) clearInterval(carouselTimer);
};

// 公告
const announcements = ref([]);
const showAnnModal = ref(false);
const currentAnn = ref({});

const loadAnnouncements = async () => {
  try {
    const res = await api.get('/announcements');
    announcements.value = res.data.slice(0, 5);
  } catch (e) { console.log('加载公告失败'); }
};
const formatAnnDate = (dateStr) => {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  return `${d.getMonth() + 1}月${d.getDate()}日`;
};
const showAnnouncementDetail = (ann) => {
  currentAnn.value = ann;
  showAnnModal.value = true;
};

// 分类
const genreList = ['流行', '电子', '轻音乐', '民谣', '说唱', '摇滚', '爵士', '古典风格', '古风', '中国风', '乡村', '金属', '新世纪', '世界音乐'];
const languageList = ['国语', '粤语', '英语', '韩语', '日语'];
const themeList = ['经典老歌', '网络歌曲', '影视原声', 'KTV金曲', '现场音乐'];
const sceneList = ['学习工作', '运动', '睡前', '咖啡馆', '旅行', '派对'];
const moodList = ['伤感', '快乐', '励志', '治愈', '安静', '思念', '甜蜜'];

const selectedGenre = ref('');
const selectedLanguage = ref('');
const selectedTheme = ref('');
const selectedScene = ref('');
const selectedMood = ref('');

const loadSongs = async () => {
  const userId = localStorage.getItem("user_id");
  const tags = [selectedLanguage.value, selectedTheme.value, selectedScene.value, selectedMood.value].filter(Boolean).join(',');
  
  try {
    // 使用AI智能排序API
    const res = await api.get("/ai/smart-sort", { 
      params: { 
        user_id: userId || undefined,
        genre: selectedGenre.value || undefined, 
        tag: tags || undefined 
      } 
    });
    songs.value = res.data;
  } catch (e) {
    // 降级：使用普通API
    console.log('智能排序失败，使用普通排序:', e);
    const res = await api.get("/songs", { params: { genre: selectedGenre.value || undefined, tag: tags || undefined } });
    songs.value = res.data;
  }
};

// AI智能推荐（使用智能排序API）
const loadAIRecommendations = async () => {
  const userId = localStorage.getItem("user_id");
  aiLoading.value = true;
  try {
    const res = await api.get("/ai/smart-sort", { 
      params: { user_id: userId, sort: 'smart', limit: 8 } 
    });
    aiRecommendations.value = res.data || [];
    recommendType.value = userId ? 'personalized' : 'popular';
  } catch (e) {
    console.log('AI推荐加载失败:', e);
    aiRecommendations.value = [];
    recommendType.value = 'popular';
  } finally {
    aiLoading.value = false;
  }
};

// 加载最新上传歌曲
const loadLatestSongs = async () => {
  try {
    const res = await api.get("/ai/smart-sort", { 
      params: { sort: 'latest', limit: 10 } 
    });
    latestSongs.value = res.data || [];
  } catch (e) {
    console.log('最新上传加载失败:', e);
    latestSongs.value = [];
  }
};

// 加载排行榜
const loadRanking = async () => {
  try {
    const res = await api.get("/ai/ranking", { params: { limit: 20 } });
    rankingList.value = res.data.ranking || [];
    rankingUpdateTime.value = res.data.updated_at || '';
  } catch (e) {
    console.log('排行榜加载失败:', e);
    // 降级：使用普通歌曲列表
    rankingList.value = songs.value.slice(0, 20).map((s, idx) => ({
      ...s,
      current_rank: idx + 1,
      rank_change: null,
      is_new: false
    }));
  }
};

// 格式化播放次数
const formatPlayCount = (count) => {
  if (!count) return '0';
  if (count >= 10000) return (count / 10000).toFixed(1) + '万';
  return count.toString();
};

const selectGenre = (g) => { selectedGenre.value = g; loadSongs(); };
const selectLanguage = (l) => { selectedLanguage.value = l; loadSongs(); };
const selectTheme = (t) => { selectedTheme.value = t; loadSongs(); };
const selectScene = (s) => { selectedScene.value = s; loadSongs(); };
const selectMood = (m) => { selectedMood.value = m; loadSongs(); };

const play = (song) => { playSong(song, songs.value); };
const playAll = () => { if (songs.value.length) playSong(songs.value[0], songs.value); };
const goDetail = (id) => { router.push(`/songs/${id}`); };

const loadFavorites = async () => {
  const userId = localStorage.getItem("user_id");
  if (!userId) return;
  try {
    const res = await api.get(`/users/${userId}/favorites`);
    favoriteIds.value = new Set(res.data.map(s => s.id));
  } catch (e) { console.error("加载收藏失败", e); }
};

const toggleFavorite = async (song) => {
  const id = localStorage.getItem("user_id");
  if (!id) { alert("请先登录"); router.push("/login"); return; }
  await api.post(`/songs/${song.id}/favorite`, { user_id: Number(id) });
  if (favoriteIds.value.has(song.id)) favoriteIds.value.delete(song.id);
  else favoriteIds.value.add(song.id);
  favoriteIds.value = new Set(favoriteIds.value);
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

onMounted(() => {
  loadSongs();
  loadFavorites();
  loadAnnouncements();
  loadAIRecommendations();
  loadLatestSongs();
  loadRanking();
  startCarousel();
});
onUnmounted(() => { stopCarousel(); });
</script>

<style scoped>
.home-container { max-width: 1200px; margin: 0 auto; background: rgba(255, 254, 249, 0.85); }

/* AI推荐样式 */
.ai-badge {
  font-size: 12px;
  padding: 4px 10px;
  background: linear-gradient(135deg, #2d5a5a, #d4a84b);
  color: #fff;
  border-radius: 12px;
  margin-left: 10px;
}
.ai-loading {
  text-align: center;
  padding: 40px;
  color: #999;
  font-size: 14px;
}
.ai-card {
  position: relative;
}

/* 细分导航 */
/* 细分导航 - 中华风 */
.sub-nav {
  display: flex;
  gap: 8px;
  padding: 15px 0;
  border-bottom: 1px solid rgba(212, 168, 75, 0.2);
  margin-bottom: 24px;
}
.sub-nav-item {
  font-size: 15px;
  color: #666;
  cursor: pointer;
  padding: 8px 20px;
  border-radius: 4px;
  transition: all 0.3s;
  letter-spacing: 1px;
}
.sub-nav-item:hover { color: #2d5a5a; background: rgba(45, 90, 90, 0.05); }
.sub-nav-item.active { 
  color: #2d5a5a; 
  font-weight: 500; 
  background: rgba(45, 90, 90, 0.1);
  border: 1px solid rgba(45, 90, 90, 0.2);
}

/* 轮播图区域 */
.carousel-section {
  display: flex;
  gap: 20px;
  margin-bottom: 30px;
}
.carousel {
  flex: 1;
  position: relative;
  border-radius: 12px;
  overflow: hidden;
  height: 200px;
}
.carousel-inner {
  display: flex;
  height: 100%;
  transition: transform 0.5s ease;
}
.carousel-slide {
  min-width: 100%;
  height: 100%;
}
.slide-content {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 30px 40px;
  color: #fff;
}
.slide-text h3 { font-size: 28px; margin: 0 0 10px; }
.slide-text p { font-size: 14px; opacity: 0.9; margin: 0; }
.slide-icon { font-size: 60px; }
.carousel-btn {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 36px;
  height: 36px;
  border: none;
  background: rgba(255,255,255,0.3);
  color: #fff;
  font-size: 24px;
  cursor: pointer;
  border-radius: 50%;
  opacity: 0;
  transition: opacity 0.3s;
}
.carousel:hover .carousel-btn { opacity: 1; }
.carousel-btn.prev { left: 15px; }
.carousel-btn.next { right: 15px; }
.carousel-btn:hover { background: rgba(255,255,255,0.5); }
.carousel-dots {
  position: absolute;
  bottom: 15px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 8px;
}
.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: rgba(255,255,255,0.5);
  cursor: pointer;
}
.dot.active { background: #fff; }

/* 公告区域 - 中华风 */
.announcement-section {
  background: linear-gradient(135deg, #fffef9, #faf8f5);
  border: 1px solid rgba(212, 168, 75, 0.3);
  border-radius: 8px;
  padding: 16px 20px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(212, 168, 75, 0.1);
}
.ann-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: #d48806;
  margin-bottom: 12px;
  padding-bottom: 10px;
  border-bottom: 1px solid #f0f0f0;
}
.ann-list { display: flex; flex-direction: column; gap: 10px; }
.ann-item {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 13px;
  color: #666;
}
.ann-item:hover { color: #2d5a5a; }
.ann-dot { color: #2d5a5a; }
.ann-text { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

/* 区块 - 中华风 */
.section { margin-bottom: 32px; }
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(212, 168, 75, 0.15);
}
.section-header h3 { 
  font-size: 20px; 
  font-weight: 600; 
  color: #1a1a1a; 
  margin: 0;
  letter-spacing: 2px;
  position: relative;
  padding-left: 12px;
}
.section-header h3::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 20px;
  background: linear-gradient(180deg, #2d5a5a, #d4a84b);
  border-radius: 2px;
}
.more { font-size: 13px; color: #999; cursor: pointer; }
.more:hover { color: #2d5a5a; }
.header-right { display: flex; align-items: center; gap: 12px; }
.more:hover { color: #2d5a5a; }

/* 歌曲卡片网格 - 中华风 */
.song-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}
.song-card {
  background: linear-gradient(180deg, #fffef9 0%, #E6F4EA 100%);
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s;
  border: 1px solid rgba(212, 168, 75, 0.15);
}
.song-card:hover { 
  transform: translateY(-6px); 
  box-shadow: 0 12px 30px rgba(45, 90, 90, 0.15);
  border-color: rgba(45, 90, 90, 0.3);
}
.card-cover {
  position: relative;
  aspect-ratio: 1;
  background: linear-gradient(135deg, rgba(255,255,255,0.4) 0%, #8BA8A8 50%, #7a9999 100%);
}
.card-cover img { width: 100%; height: 100%; object-fit: cover; }
.cover-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 48px;
  color: #2d5a5a;
}
.play-overlay {
  position: absolute;
  inset: 0;
  background: rgba(26, 26, 26, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s;
}
.song-card:hover .play-overlay { opacity: 1; }
.card-info { padding: 14px; cursor: pointer; }
.card-info:hover .card-title { color: #2d5a5a; }
.card-title { font-size: 14px; font-weight: 500; color: #333; margin-bottom: 4px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; transition: color 0.2s; }
.card-artist { font-size: 12px; color: #999; }

/* 简单歌曲列表 - 中华风 */
.song-list-simple { 
  background: linear-gradient(180deg, #fffef9 0%, #E6F4EA 100%); 
  border-radius: 8px; 
  overflow: hidden;
  border: 1px solid rgba(212, 168, 75, 0.15);
}
.song-row {
  display: flex;
  align-items: center;
  padding: 14px 18px;
  border-bottom: 1px solid rgba(212, 168, 75, 0.1);
  transition: all 0.2s;
}
.song-row:hover { background: rgba(45, 90, 90, 0.03); }
.song-row:last-child { border-bottom: none; }
.row-index { width: 32px; font-size: 15px; color: #999; text-align: center; cursor: pointer; }
.row-index.top { color: #2d5a5a; font-weight: 700; }
.row-title { flex: 1; font-size: 14px; color: #333; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; margin-right: 15px; transition: color 0.2s; }
.row-title.clickable { cursor: pointer; }
.row-title.clickable:hover { color: #2d5a5a; }
.row-artist { width: 120px; font-size: 13px; color: #999; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.row-duration { width: 60px; font-size: 13px; color: #999; text-align: right; margin-right: 15px; }
.row-fav { width: 30px; border: none; background: none; color: #ccc; cursor: pointer; transition: color 0.2s; flex-shrink: 0; }
.row-fav:hover { color: #ff4d4f; }
.row-fav.active { color: #ff4d4f; }

/* 分类区域 - 中华风 */
.category-section {
  background: linear-gradient(135deg, #E6F4EA 0%, #fffef9 100%);
  border-radius: 8px;
  padding: 20px 24px;
  margin-bottom: 24px;
  border: 1px solid rgba(212, 168, 75, 0.15);
}
.category-row {
  display: flex;
  align-items: flex-start;
  padding: 14px 0;
  border-bottom: 1px solid rgba(212, 168, 75, 0.1);
}
.category-row:last-child { border-bottom: none; }
.category-label { width: 60px; font-size: 14px; color: #2d5a5a; font-weight: 600; flex-shrink: 0; }
.category-tags { display: flex; flex-wrap: wrap; gap: 8px 20px; flex: 1; }
.tag { font-size: 13px; color: #666; cursor: pointer; padding: 4px 8px; border-radius: 4px; transition: all 0.2s; }
.tag:hover { color: #2d5a5a; background: rgba(45, 90, 90, 0.05); }
.tag.active { color: #2d5a5a; font-weight: 500; background: rgba(45, 90, 90, 0.1); }

/* 操作栏 - 中华风 */
.action-bar { padding: 16px 0; display: flex; align-items: center; gap: 15px; }
.action-btn { display: flex; align-items: center; gap: 6px; padding: 10px 24px; border-radius: 4px; font-size: 13px; cursor: pointer; border: 1px solid rgba(212, 168, 75, 0.3); background: #fffef9; transition: all 0.3s; }
.action-btn.primary { background: linear-gradient(135deg, rgba(255,255,255,0.4) 0%, #8BA8A8 50%, #7a9999 100%); color: #d4a84b; border-color: #d4a84b; }
.action-btn.primary:hover { background: linear-gradient(135deg, rgba(255,255,255,0.5) 0%, #9ab8b8 50%, #8BA8A8 100%); box-shadow: 0 4px 12px rgba(139, 168, 168, 0.4); }
.song-total { font-size: 13px; color: #999; }

/* 歌曲列表 */
.song-list-header { display: flex; align-items: center; padding: 12px 15px; background: #f5f5f5; border-radius: 4px; font-size: 13px; color: #888; margin-bottom: 5px; }
.song-list { background: #fff; border-radius: 4px; }
.song-item { display: flex; align-items: center; padding: 12px 15px; border-bottom: 1px solid #f0f0f0; }
.song-item:hover { background: #f9f9f9; }
.song-item:hover .index-number { display: none; }
.song-item:hover .play-btn { display: flex; }
.song-item.playing { background: #E6F4EA; }
.song-item.playing .col-title { color: #d4a84b; }
.col-index { width: 50px; text-align: center; color: #999; }
.index-number { font-size: 14px; }
.play-btn { display: none; align-items: center; justify-content: center; width: 28px; height: 28px; border: none; background: transparent; cursor: pointer; color: #d4a84b; }
.col-title { flex: 2; font-size: 14px; color: #333; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; cursor: pointer; }
.col-title:hover { color: #d4a84b; }
.col-artist, .col-album { flex: 1.5; font-size: 13px; color: #666; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.col-duration { width: 70px; text-align: right; font-size: 13px; color: #999; padding-right: 20px; }
.col-actions { width: 100px; display: flex; justify-content: flex-end; gap: 10px; flex-shrink: 0; }
.icon-btn { width: 28px; height: 28px; border: none; background: transparent; cursor: pointer; color: #999; display: flex; align-items: center; justify-content: center; text-decoration: none; }
.icon-btn:hover { color: #d4a84b; }
.icon-btn.favorited { color: #ff4d4f; }
.empty-state { padding: 60px; text-align: center; color: #999; }

/* 排行榜 - 中华风 */
.rank-section { background: #fffef9; border-radius: 10px; padding: 24px; border: 1px solid rgba(212, 168, 75, 0.2); }
.rank-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; padding-bottom: 15px; border-bottom: 1px solid rgba(212, 168, 75, 0.15); }
.rank-header h3 { font-size: 20px; font-weight: 600; color: #1a1a1a; margin: 0; letter-spacing: 2px; }
.rank-update-time { font-size: 12px; color: #999; }
.rank-list { display: flex; flex-direction: column; }
.rank-item { display: flex; align-items: center; padding: 16px 12px; border-bottom: 1px solid rgba(212, 168, 75, 0.1); cursor: pointer; transition: all 0.2s; }
.rank-item:hover { background: rgba(45, 90, 90, 0.03); }
.rank-item:last-child { border-bottom: none; }
.rank-num { width: 45px; font-size: 20px; font-weight: 700; color: #999; text-align: center; flex-shrink: 0; }
.rank-num.top { color: #2d5a5a; font-size: 22px; }
.rank-info { flex: 1; min-width: 0; margin-right: 15px; }
.rank-title { font-size: 15px; color: #333; margin-bottom: 4px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.rank-artist { font-size: 12px; color: #999; }
.rank-change { width: 70px; text-align: center; flex-shrink: 0; }
.rank-up { color: #e53935; font-size: 13px; font-weight: 600; }
.rank-down { color: #43a047; font-size: 13px; font-weight: 600; }
.rank-same { color: #999; font-size: 13px; }
.rank-new { background: linear-gradient(135deg, #2d5a5a, #d4a84b); color: #fff; font-size: 10px; padding: 2px 6px; border-radius: 3px; font-weight: 600; }
.rank-play-count { width: 90px; font-size: 12px; color: #999; text-align: right; margin-right: 15px; flex-shrink: 0; }
.rank-duration { width: 50px; font-size: 13px; color: #999; text-align: right; flex-shrink: 0; }

/* 弹窗 */
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.ann-modal { background: #fff; border-radius: 10px; width: 380px; max-width: 90%; }
.ann-modal-header { display: flex; justify-content: space-between; align-items: center; padding: 14px 18px; border-bottom: 1px solid #f0f0f0; }
.ann-modal-header h3 { font-size: 16px; font-weight: 600; color: #333; margin: 0; }
.close-btn { width: 28px; height: 28px; border: none; background: none; font-size: 20px; color: #999; cursor: pointer; }
.ann-modal-body { padding: 18px; }
.ann-content { font-size: 14px; line-height: 1.8; color: #333; white-space: pre-wrap; margin: 0 0 12px; }
.ann-time { font-size: 12px; color: #999; margin: 0; }

/* 歌单弹窗 */
.playlist-modal { background: #fffef9; border-radius: 10px; width: 360px; max-width: 90%; border: 1px solid rgba(212, 168, 75, 0.3); }
.playlist-modal-header { display: flex; justify-content: space-between; align-items: center; padding: 14px 18px; border-bottom: 1px solid rgba(212, 168, 75, 0.2); background: linear-gradient(90deg, rgba(230, 244, 234, 0.5), transparent); }
.playlist-modal-header h3 { font-size: 16px; font-weight: 600; color: #1a1a1a; margin: 0; }
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
