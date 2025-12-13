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

      <!-- 推荐歌曲 -->
      <div class="section">
        <div class="section-header">
          <h3>推荐歌曲</h3>
          <span class="more" @click="activeSubNav = 'category'">更多 ›</span>
        </div>
        <div class="song-grid">
          <div v-for="song in songs.slice(0, 8)" :key="song.id" class="song-card" @click="play(song)">
            <div class="card-cover">
              <img v-if="song.cover_url" :src="song.cover_url" alt="" />
              <div v-else class="cover-placeholder">♪</div>
              <div class="play-overlay">
                <svg viewBox="0 0 24 24" width="32" height="32">
                  <path fill="#fff" d="M8 5v14l11-7z"/>
                </svg>
              </div>
            </div>
            <div class="card-info">
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
          <div v-for="(song, index) in songs.slice(0, 10)" :key="song.id" class="song-row" @click="play(song)">
            <span class="row-index" :class="{ top: index < 3 }">{{ index + 1 }}</span>
            <span class="row-title">{{ song.title }}</span>
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
            <button class="icon-btn" :class="{ favorited: favoriteIds.has(song.id) }" @click="toggleFavorite(song)">
              <svg viewBox="0 0 24 24" width="18" height="18"><path fill="currentColor" d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/></svg>
            </button>
            <a class="icon-btn" :href="song.download_url" target="_blank"><svg viewBox="0 0 24 24" width="18" height="18"><path fill="currentColor" d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/></svg></a>
          </span>
        </div>
        <div v-if="songs.length === 0" class="empty-state">暂无歌曲</div>
      </div>
    </template>

    <!-- 排行榜 -->
    <template v-if="activeSubNav === 'rank'">
      <div class="rank-section">
        <div class="rank-list">
          <div v-for="(song, index) in songs.slice(0, 20)" :key="song.id" class="rank-item" @click="play(song)">
            <span class="rank-num" :class="{ top: index < 3 }">{{ index + 1 }}</span>
            <div class="rank-info">
              <div class="rank-title">{{ song.title }}</div>
              <div class="rank-artist">{{ song.artist || '未知歌手' }}</div>
            </div>
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
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from "vue";
import api from "../api";
import { useRouter } from "vue-router";
import { playerState, playSong, formatDuration } from "../stores/player";

const router = useRouter();
const songs = ref([]);
const favoriteIds = ref(new Set());

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
  const tags = [selectedLanguage.value, selectedTheme.value, selectedScene.value, selectedMood.value].filter(Boolean).join(',');
  const res = await api.get("/songs", { params: { genre: selectedGenre.value || undefined, tag: tags || undefined } });
  songs.value = res.data;
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

onMounted(() => {
  loadSongs();
  loadFavorites();
  loadAnnouncements();
  startCarousel();
});
onUnmounted(() => { stopCarousel(); });
</script>

<style scoped>
.home-container { max-width: 1200px; margin: 0 auto; }

/* 细分导航 */
.sub-nav {
  display: flex;
  gap: 30px;
  padding: 15px 0;
  border-bottom: 1px solid #eee;
  margin-bottom: 20px;
}
.sub-nav-item {
  font-size: 15px;
  color: #666;
  cursor: pointer;
  padding-bottom: 10px;
  border-bottom: 2px solid transparent;
  margin-bottom: -16px;
}
.sub-nav-item:hover { color: #31c27c; }
.sub-nav-item.active { color: #31c27c; font-weight: 500; border-color: #31c27c; }

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

/* 公告区域 */
.announcement-section {
  background: linear-gradient(135deg, #fff9e6, #fff3cd);
  border: 1px solid #ffe58f;
  border-radius: 10px;
  padding: 14px 18px;
  margin-bottom: 20px;
}
.ann-header {
  display: flex;
  align-items: center;
  gap: 6px;
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
.ann-item:hover { color: #31c27c; }
.ann-dot { color: #31c27c; }
.ann-text { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

/* 区块 */
.section { margin-bottom: 30px; }
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.section-header h3 { font-size: 18px; font-weight: 600; color: #333; margin: 0; }
.more { font-size: 13px; color: #999; cursor: pointer; }
.more:hover { color: #31c27c; }

/* 歌曲卡片网格 */
.song-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}
.song-card {
  background: #fff;
  border-radius: 10px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}
.song-card:hover { transform: translateY(-4px); box-shadow: 0 8px 20px rgba(0,0,0,0.1); }
.card-cover {
  position: relative;
  aspect-ratio: 1;
  background: linear-gradient(135deg, #667eea, #764ba2);
}
.card-cover img { width: 100%; height: 100%; object-fit: cover; }
.cover-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 48px;
  color: rgba(255,255,255,0.8);
}
.play-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0,0,0,0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s;
}
.song-card:hover .play-overlay { opacity: 1; }
.card-info { padding: 12px; }
.card-title { font-size: 14px; font-weight: 500; color: #333; margin-bottom: 4px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.card-artist { font-size: 12px; color: #999; }

/* 简单歌曲列表 */
.song-list-simple { background: #fff; border-radius: 10px; overflow: hidden; }
.song-row {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #f5f5f5;
  cursor: pointer;
  transition: background 0.2s;
}
.song-row:hover { background: #f9f9f9; }
.song-row:last-child { border-bottom: none; }
.row-index { width: 30px; font-size: 14px; color: #999; text-align: center; }
.row-index.top { color: #ff4d4f; font-weight: 600; }
.row-title { flex: 1; font-size: 14px; color: #333; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; margin-right: 15px; }
.row-artist { width: 120px; font-size: 13px; color: #999; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.row-duration { width: 50px; font-size: 13px; color: #999; text-align: right; }
.row-fav { width: 30px; border: none; background: none; color: #ccc; cursor: pointer; }
.row-fav:hover { color: #ff4d4f; }
.row-fav.active { color: #ff4d4f; }

/* 分类区域 */
.category-section {
  background: #fff;
  border-radius: 10px;
  padding: 20px;
  margin-bottom: 20px;
}
.category-row {
  display: flex;
  align-items: flex-start;
  padding: 12px 0;
  border-bottom: 1px solid #f5f5f5;
}
.category-row:last-child { border-bottom: none; }
.category-label { width: 60px; font-size: 14px; color: #333; font-weight: 500; flex-shrink: 0; }
.category-tags { display: flex; flex-wrap: wrap; gap: 8px 20px; flex: 1; }
.tag { font-size: 13px; color: #666; cursor: pointer; padding: 4px 0; }
.tag:hover { color: #31c27c; }
.tag.active { color: #31c27c; font-weight: 500; }

/* 操作栏 */
.action-bar { padding: 15px 0; display: flex; align-items: center; gap: 15px; }
.action-btn { display: flex; align-items: center; gap: 6px; padding: 8px 20px; border-radius: 20px; font-size: 13px; cursor: pointer; border: 1px solid #ddd; background: #fff; }
.action-btn.primary { background: #31c27c; color: #fff; border-color: #31c27c; }
.action-btn.primary:hover { background: #28a86d; }
.song-total { font-size: 13px; color: #999; }

/* 歌曲列表 */
.song-list-header { display: flex; align-items: center; padding: 12px 15px; background: #f5f5f5; border-radius: 4px; font-size: 13px; color: #888; margin-bottom: 5px; }
.song-list { background: #fff; border-radius: 4px; }
.song-item { display: flex; align-items: center; padding: 12px 15px; border-bottom: 1px solid #f0f0f0; }
.song-item:hover { background: #f9f9f9; }
.song-item:hover .index-number { display: none; }
.song-item:hover .play-btn { display: flex; }
.song-item.playing { background: #f0fff0; }
.song-item.playing .col-title { color: #31c27c; }
.col-index { width: 50px; text-align: center; color: #999; }
.index-number { font-size: 14px; }
.play-btn { display: none; align-items: center; justify-content: center; width: 28px; height: 28px; border: none; background: transparent; cursor: pointer; color: #31c27c; }
.col-title { flex: 2; font-size: 14px; color: #333; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; cursor: pointer; }
.col-title:hover { color: #31c27c; }
.col-artist, .col-album { flex: 1.5; font-size: 13px; color: #666; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.col-duration { width: 60px; text-align: right; font-size: 13px; color: #999; }
.col-actions { width: 80px; display: flex; justify-content: flex-end; gap: 8px; }
.icon-btn { width: 28px; height: 28px; border: none; background: transparent; cursor: pointer; color: #999; display: flex; align-items: center; justify-content: center; text-decoration: none; }
.icon-btn:hover { color: #31c27c; }
.icon-btn.favorited { color: #ff4d4f; }
.empty-state { padding: 60px; text-align: center; color: #999; }

/* 排行榜 */
.rank-section { background: #fff; border-radius: 10px; padding: 20px; }
.rank-list { display: flex; flex-direction: column; }
.rank-item { display: flex; align-items: center; padding: 14px 10px; border-bottom: 1px solid #f5f5f5; cursor: pointer; }
.rank-item:hover { background: #f9f9f9; }
.rank-num { width: 40px; font-size: 18px; font-weight: 600; color: #999; text-align: center; }
.rank-num.top { color: #ff4d4f; }
.rank-info { flex: 1; }
.rank-title { font-size: 14px; color: #333; margin-bottom: 4px; }
.rank-artist { font-size: 12px; color: #999; }
.rank-duration { font-size: 13px; color: #999; }

/* 弹窗 */
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.ann-modal { background: #fff; border-radius: 10px; width: 380px; max-width: 90%; }
.ann-modal-header { display: flex; justify-content: space-between; align-items: center; padding: 14px 18px; border-bottom: 1px solid #f0f0f0; }
.ann-modal-header h3 { font-size: 16px; font-weight: 600; color: #333; margin: 0; }
.close-btn { width: 28px; height: 28px; border: none; background: none; font-size: 20px; color: #999; cursor: pointer; }
.ann-modal-body { padding: 18px; }
.ann-content { font-size: 14px; line-height: 1.8; color: #333; white-space: pre-wrap; margin: 0 0 12px; }
.ann-time { font-size: 12px; color: #999; margin: 0; }
</style>
