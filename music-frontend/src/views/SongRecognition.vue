<template>
  <div class="search-page">
    <div class="page-header">
      <h2>歌曲检索</h2>
      <p class="subtitle">通过关键词或描述，AI帮你找歌</p>
    </div>

    <!-- 搜索区域 -->
    <div class="search-card">
      <div class="search-section">
        <h3>🔍 智能检索</h3>
        <p class="section-desc">输入歌曲名、歌手、歌词片段或描述特征</p>
        <textarea 
          v-model="searchQuery" 
          placeholder="请输入检索内容，例如：&#10;- 歌曲名：'不将就'&#10;- 歌手名：'李荣浩'&#10;- 歌词片段：'我们一起学猫叫'&#10;- 特征描述：'女声，很甜，抖音很火'"
          rows="4"
          @keydown.enter.ctrl="searchSongs"
        ></textarea>
        <button class="btn-search" @click="searchSongs" :disabled="loading || !searchQuery.trim()">
          <span v-if="loading" class="loading-icon">⏳</span>
          <span v-else>🎵</span>
          {{ loading ? 'AI检索中...' : '开始检索' }}
        </button>
      </div>
    </div>

    <!-- 检索结果 -->
    <div v-if="result" class="search-card result-card">
      <div v-if="result.matched" class="result-success">
        <div class="result-header">
          <span class="success-icon">✓</span>
          <span>找到匹配歌曲！</span>
          <span class="confidence">置信度: {{ result.confidence }}%</span>
        </div>
        <div class="song-card" v-if="result.song">
          <div class="song-cover" @click="playSong(result.song)">
            <img v-if="result.song.cover_url" :src="result.song.cover_url" alt="封面" />
            <div v-else class="cover-placeholder">♪</div>
            <div class="play-overlay">
              <svg viewBox="0 0 24 24" width="32" height="32">
                <path fill="#fff" d="M8 5v14l11-7z"/>
              </svg>
            </div>
          </div>
          <div class="song-info">
            <div class="song-title">{{ result.song.title }}</div>
            <div class="song-artist">{{ result.song.artist || '未知歌手' }}</div>
            <div class="song-meta">{{ result.song.genre }} · {{ result.song.tags }}</div>
          </div>
          <div class="song-actions">
            <button class="btn-action" @click="playSong(result.song)">播放</button>
            <button class="btn-action secondary" @click="goToDetail(result.song.id)">详情</button>
          </div>
        </div>
        <div v-if="result.reason" class="match-reason">
          <strong>匹配原因：</strong>{{ result.reason }}
        </div>
      </div>
      <div v-else class="result-fail">
        <div class="fail-icon">😔</div>
        <p>{{ result.message || '未找到匹配的歌曲' }}</p>
        <p class="tip">试试提供更多信息，如歌词、歌手名等</p>
      </div>
    </div>

    <!-- 使用提示 -->
    <div class="tips-section">
      <h3>💡 检索技巧</h3>
      <ul>
        <li>输入歌曲名或歌手名可以精确匹配</li>
        <li>提供歌词片段是最有效的检索方式</li>
        <li>描述歌手的声音特点（男声/女声、沙哑/清亮等）</li>
        <li>说明歌曲的风格（流行、摇滚、民谣、古风等）</li>
        <li>按 Ctrl+Enter 快速检索</li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import api from '../api';
import { playSong as playGlobalSong } from '../stores/player';

const router = useRouter();
const searchQuery = ref('');
const loading = ref(false);
const result = ref(null);

// 检索歌曲
const searchSongs = async () => {
  if (!searchQuery.value.trim()) return;
  
  loading.value = true;
  result.value = null;
  
  try {
    const res = await api.post('/ai/recognize', {
      description: searchQuery.value
    });
    result.value = res.data;
  } catch (e) {
    result.value = { matched: false, message: '检索服务暂时不可用，请稍后再试' };
  } finally {
    loading.value = false;
  }
};

const playSong = (song) => {
  playGlobalSong(song);
};

const goToDetail = (songId) => {
  router.push(`/songs/${songId}`);
};
</script>


<style scoped>
.search-page {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  min-height: calc(100vh - 140px);
  background: rgba(255, 254, 249, 0.85);
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
}

.page-header h2 {
  font-size: 28px;
  color: #1a1a1a;
  margin-bottom: 8px;
  letter-spacing: 2px;
}

.subtitle {
  color: #999;
  font-size: 14px;
}

.search-card {
  background: linear-gradient(135deg, #E6F4EA 0%, #fffef9 100%);
  border-radius: 12px;
  padding: 24px;
  border: 1px solid rgba(212, 168, 75, 0.2);
  border: 1px solid rgba(212, 168, 75, 0.2);
  margin-bottom: 20px;
}

.search-section h3 {
  font-size: 16px;
  color: #1a1a1a;
  margin-bottom: 8px;
  padding-left: 12px;
  position: relative;
}

.search-section h3::before {
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

.section-desc {
  font-size: 13px;
  color: #999;
  margin-bottom: 16px;
  padding-left: 12px;
}

.search-section textarea {
  width: 100%;
  padding: 14px;
  border: 1px solid rgba(212, 168, 75, 0.3);
  border-radius: 8px;
  font-size: 14px;
  line-height: 1.6;
  resize: vertical;
  box-sizing: border-box;
  font-family: inherit;
  background: #fff;
  transition: all 0.3s;
}

.search-section textarea:focus {
  outline: none;
  border-color: #d4a84b;
  box-shadow: 0 0 0 3px rgba(212, 168, 75, 0.1);
}

.btn-search {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  margin-top: 16px;
  padding: 14px 24px;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid #d4a84b;
  border-radius: 20px;
  color: #2d5a5a;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-search:hover:not(:disabled) {
  background: #fff;
  box-shadow: 0 2px 8px rgba(212, 168, 75, 0.3);
}

.btn-search:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.loading-icon {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.result-card {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.result-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  font-size: 16px;
  color: #2e7d32;
}

.success-icon {
  width: 24px;
  height: 24px;
  background: #2e7d32;
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
}

.confidence {
  margin-left: auto;
  font-size: 13px;
  color: #d4a84b;
  background: rgba(212, 168, 75, 0.1);
  padding: 4px 10px;
  border-radius: 12px;
}

.song-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: linear-gradient(135deg, rgba(212, 168, 75, 0.05), transparent);
  border-radius: 8px;
  border: 1px solid rgba(212, 168, 75, 0.15);
}

.song-cover {
  width: 80px;
  height: 80px;
  border-radius: 8px;
  overflow: hidden;
  position: relative;
  cursor: pointer;
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
  background: linear-gradient(135deg, #2d5a5a, #1e3d3d);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #d4a84b;
  font-size: 32px;
}

.play-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s;
}

.song-cover:hover .play-overlay {
  opacity: 1;
}

.song-info {
  flex: 1;
  min-width: 0;
}

.song-title {
  font-size: 16px;
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 4px;
}

.song-artist {
  font-size: 14px;
  color: #666;
  margin-bottom: 4px;
}

.song-meta {
  font-size: 12px;
  color: #999;
}

.song-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.btn-action {
  padding: 8px 20px;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid #d4a84b;
  border-radius: 20px;
  color: #2d5a5a;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-action:hover {
  background: #fff;
  box-shadow: 0 2px 8px rgba(212, 168, 75, 0.3);
}

.btn-action.secondary {
  background: transparent;
  border-color: rgba(212, 168, 75, 0.3);
  color: #8b7355;
}

.btn-action.secondary:hover {
  border-color: #d4a84b;
  color: #d4a84b;
}

.match-reason {
  margin-top: 12px;
  padding: 12px;
  background: rgba(212, 168, 75, 0.05);
  border-radius: 6px;
  font-size: 13px;
  color: #666;
}

.result-fail {
  text-align: center;
  padding: 30px;
}

.fail-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.result-fail p {
  color: #666;
  margin: 0;
}

.result-fail .tip {
  margin-top: 8px;
  font-size: 13px;
  color: #999;
}

.tips-section {
  background: linear-gradient(135deg, #fffef9 0%, #E6F4EA 100%);
  border-radius: 12px;
  padding: 20px 24px;
  border: 1px solid rgba(212, 168, 75, 0.2);
  border: 1px solid rgba(212, 168, 75, 0.15);
}

.tips-section h3 {
  font-size: 15px;
  color: #1a1a1a;
  margin-bottom: 12px;
}

.tips-section ul {
  margin: 0;
  padding-left: 20px;
}

.tips-section li {
  font-size: 13px;
  color: #666;
  line-height: 1.8;
}
</style>
