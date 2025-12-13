<template>
  <div class="admin-container">
    <!-- 后台导航标签 -->
    <div class="admin-tabs">
      <router-link to="/admin/songs" class="tab-item" :class="{ active: $route.path === '/admin/songs' }">
        <svg viewBox="0 0 24 24" width="18" height="18">
          <path fill="currentColor" d="M12 3v10.55c-.59-.34-1.27-.55-2-.55-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4V7h4V3h-6z"/>
        </svg>
        歌曲管理
      </router-link>
      <router-link to="/admin/users" class="tab-item" :class="{ active: $route.path === '/admin/users' }">
        <svg viewBox="0 0 24 24" width="18" height="18">
          <path fill="currentColor" d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"/>
        </svg>
        用户管理
      </router-link>
      <router-link to="/admin/announcements" class="tab-item" :class="{ active: $route.path === '/admin/announcements' }">
        <svg viewBox="0 0 24 24" width="18" height="18">
          <path fill="currentColor" d="M20 2H4c-1.1 0-1.99.9-1.99 2L2 22l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-7 9h-2V5h2v6zm0 4h-2v-2h2v2z"/>
        </svg>
        公告管理
      </router-link>
    </div>

    <div class="admin-header">
      <h2>后台歌曲管理</h2>
      <span class="admin-info">当前管理员ID：{{ adminUserId }}</span>
    </div>

    <div v-if="!adminUserId" class="no-auth">
      <svg viewBox="0 0 24 24" width="48" height="48">
        <path fill="#ff6b6b" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
      </svg>
      <p>请先以管理员账号登录</p>
    </div>

    <div v-else class="admin-content">
      <!-- 统计信息 + 添加按钮 -->
      <div class="stats-bar">
        <div class="stat-item">
          <span class="stat-value">{{ songs.length }}</span>
          <span class="stat-label">歌曲总数</span>
        </div>
        <button class="btn-add" @click="showUploadModal = true">
          <svg viewBox="0 0 24 24" width="18" height="18">
            <path fill="currentColor" d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
          </svg>
          添加歌曲
        </button>
      </div>

      <!-- 上传歌曲弹窗 -->
      <div v-if="showUploadModal" class="modal-overlay" @click.self="closeUploadModal">
        <div class="modal-content">
          <div class="modal-header">
            <h3>上传新歌曲</h3>
            <button class="modal-close" @click="closeUploadModal">×</button>
          </div>
          <div class="modal-body">
            <div class="form-group">
              <label>歌曲名称 <span class="required">*</span></label>
              <input v-model="uploadForm.title" class="form-input" placeholder="请输入歌曲名称" />
            </div>
            <div class="form-group">
              <label>歌手</label>
              <input v-model="uploadForm.artist" class="form-input" placeholder="请输入歌手名称" />
            </div>
            <!-- 多分类选择 -->
            <div class="form-group">
              <label>流派</label>
              <div class="tag-selector">
                <span 
                  v-for="g in categoryOptions.genre" 
                  :key="g" 
                  class="tag-item"
                  :class="{ selected: uploadForm.genres.includes(g) }"
                  @click="toggleUploadTag('genres', g)"
                >{{ g }}</span>
              </div>
            </div>
            <div class="form-group">
              <label>语种</label>
              <div class="tag-selector">
                <span 
                  v-for="lang in categoryOptions.language" 
                  :key="lang" 
                  class="tag-item"
                  :class="{ selected: uploadForm.languages.includes(lang) }"
                  @click="toggleUploadTag('languages', lang)"
                >{{ lang }}</span>
              </div>
            </div>
            <div class="form-group">
              <label>主题</label>
              <div class="tag-selector">
                <span 
                  v-for="theme in categoryOptions.theme" 
                  :key="theme" 
                  class="tag-item"
                  :class="{ selected: uploadForm.themes.includes(theme) }"
                  @click="toggleUploadTag('themes', theme)"
                >{{ theme }}</span>
              </div>
            </div>
            <div class="form-group">
              <label>场景</label>
              <div class="tag-selector">
                <span 
                  v-for="scene in categoryOptions.scene" 
                  :key="scene" 
                  class="tag-item"
                  :class="{ selected: uploadForm.scenes.includes(scene) }"
                  @click="toggleUploadTag('scenes', scene)"
                >{{ scene }}</span>
              </div>
            </div>
            <div class="form-group">
              <label>心情</label>
              <div class="tag-selector">
                <span 
                  v-for="mood in categoryOptions.mood" 
                  :key="mood" 
                  class="tag-item"
                  :class="{ selected: uploadForm.moods.includes(mood) }"
                  @click="toggleUploadTag('moods', mood)"
                >{{ mood }}</span>
              </div>
            </div>
            <div class="form-group">
              <label>音频文件 <span class="required">*</span></label>
              <div class="file-upload" :class="{ 'has-file': uploadForm.file }">
                <input type="file" accept="audio/*" @change="onFileChange" ref="fileInput" />
                <div class="file-upload-content">
                  <svg v-if="!uploadForm.file" viewBox="0 0 24 24" width="40" height="40">
                    <path fill="#31c27c" d="M9 16h6v-6h4l-7-7-7 7h4zm-4 2h14v2H5z"/>
                  </svg>
                  <p v-if="!uploadForm.file">点击或拖拽文件到此处上传</p>
                  <p v-else class="file-name">
                    <svg viewBox="0 0 24 24" width="20" height="20">
                      <path fill="#31c27c" d="M12 3v10.55c-.59-.34-1.27-.55-2-.55-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4V7h4V3h-6z"/>
                    </svg>
                    {{ uploadForm.file.name }}
                  </p>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn-cancel" @click="closeUploadModal">取消</button>
            <button class="btn-submit" @click="uploadSong" :disabled="uploading">
              {{ uploading ? '上传中...' : '确认上传' }}
            </button>
          </div>
        </div>
      </div>

      <!-- 歌曲表格 -->
      <div class="table-wrapper">
        <table class="admin-table">
          <thead>
            <tr>
              <th class="col-id">ID</th>
              <th class="col-title">歌名</th>
              <th class="col-artist">歌手</th>
              <th class="col-genre">分类</th>
              <th class="col-tags">标签</th>
              <th class="col-actions">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="song in songs" :key="song.id">
              <td class="col-id">{{ song.id }}</td>
              <td class="col-title">
                <input v-model="song.editTitle" class="edit-input" />
              </td>
              <td class="col-artist">
                <input v-model="song.editArtist" class="edit-input" />
              </td>
              <td class="col-genre">
                <button class="tag-edit-btn" @click="openTagEditor(song)">
                  {{ song.editGenre || '点击选择' }}
                </button>
              </td>
              <td class="col-tags">
                <button class="tag-edit-btn" @click="openTagEditor(song)">
                  {{ song.editTags || '点击选择' }}
                </button>
              </td>
              <td class="col-actions">
                <div class="action-btns">
                  <button class="action-btn detail" @click="openDetailEditor(song)" title="编辑详情">
                    <svg viewBox="0 0 24 24" width="16" height="16"><path fill="currentColor" d="M14 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V8l-6-6zm-1 9h-2v2H9v-2H7v-2h2V7h2v2h2v2zm-1-8.5L17.5 8H12V3.5z"/></svg>
                  </button>
                  <button class="action-btn save" @click="saveSong(song)" title="保存">
                    <svg viewBox="0 0 24 24" width="16" height="16"><path fill="currentColor" d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>
                  </button>
                  <button class="action-btn delete" @click="deleteSong(song)" title="删除">
                    <svg viewBox="0 0 24 24" width="16" height="16"><path fill="currentColor" d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/></svg>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="songs.length === 0" class="empty-state">
        <p>暂无歌曲数据</p>
      </div>

      <div v-if="msg" class="message" :class="msgType">
        {{ msg }}
      </div>

      <!-- 详情编辑弹窗 -->
      <div v-if="showDetailEditor" class="modal-overlay" @click.self="closeDetailEditor">
        <div class="modal-content detail-editor-modal">
          <div class="modal-header">
            <h3>编辑歌曲详情 - {{ detailForm.title }}</h3>
            <button class="modal-close" @click="closeDetailEditor">×</button>
          </div>
          <div class="modal-body">
            <div class="detail-layout">
              <div class="cover-section">
                <label>封面图片</label>
                <div class="cover-preview" @click="triggerCoverUpload">
                  <img v-if="detailForm.cover_url || detailForm.coverPreview" :src="detailForm.coverPreview || detailForm.cover_url" alt="封面" />
                  <div v-else class="cover-placeholder">
                    <svg viewBox="0 0 24 24" width="40" height="40">
                      <path fill="#ccc" d="M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5z"/>
                    </svg>
                    <span>点击上传封面</span>
                  </div>
                </div>
                <input type="file" ref="coverInput" accept="image/*" @change="onCoverChange" style="display:none" />
              </div>
              <div class="info-section">
                <div class="form-group">
                  <label>专辑</label>
                  <input v-model="detailForm.album" class="form-input" placeholder="请输入专辑名称" />
                </div>
                <div class="form-group">
                  <label>发行时间</label>
                  <input v-model="detailForm.release_date" type="date" class="form-input" />
                </div>
              </div>
            </div>
            <div class="form-group">
              <label>歌词</label>
              <textarea v-model="detailForm.lyrics" class="form-textarea" rows="10" placeholder="请输入歌词，每行一句"></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn-cancel" @click="closeDetailEditor">取消</button>
            <button class="btn-submit" @click="saveDetail" :disabled="savingDetail">
              {{ savingDetail ? '保存中...' : '保存详情' }}
            </button>
          </div>
        </div>
      </div>

      <!-- 分类编辑弹窗 -->
      <div v-if="showTagEditor" class="modal-overlay" @click.self="closeTagEditor">
        <div class="modal-content tag-editor-modal">
          <div class="modal-header">
            <h3>编辑分类标签 - {{ editingSong?.editTitle }}</h3>
            <button class="modal-close" @click="closeTagEditor">×</button>
          </div>
          <div class="modal-body">
            <div class="form-group">
              <label>流派</label>
              <div class="tag-selector">
                <span 
                  v-for="g in categoryOptions.genre" 
                  :key="g" 
                  class="tag-item"
                  :class="{ selected: editingTags.genres.includes(g) }"
                  @click="toggleEditTag('genres', g)"
                >{{ g }}</span>
              </div>
            </div>
            <div class="form-group">
              <label>语种</label>
              <div class="tag-selector">
                <span 
                  v-for="lang in categoryOptions.language" 
                  :key="lang" 
                  class="tag-item"
                  :class="{ selected: editingTags.languages.includes(lang) }"
                  @click="toggleEditTag('languages', lang)"
                >{{ lang }}</span>
              </div>
            </div>
            <div class="form-group">
              <label>主题</label>
              <div class="tag-selector">
                <span 
                  v-for="theme in categoryOptions.theme" 
                  :key="theme" 
                  class="tag-item"
                  :class="{ selected: editingTags.themes.includes(theme) }"
                  @click="toggleEditTag('themes', theme)"
                >{{ theme }}</span>
              </div>
            </div>
            <div class="form-group">
              <label>场景</label>
              <div class="tag-selector">
                <span 
                  v-for="scene in categoryOptions.scene" 
                  :key="scene" 
                  class="tag-item"
                  :class="{ selected: editingTags.scenes.includes(scene) }"
                  @click="toggleEditTag('scenes', scene)"
                >{{ scene }}</span>
              </div>
            </div>
            <div class="form-group">
              <label>心情</label>
              <div class="tag-selector">
                <span 
                  v-for="mood in categoryOptions.mood" 
                  :key="mood" 
                  class="tag-item"
                  :class="{ selected: editingTags.moods.includes(mood) }"
                  @click="toggleEditTag('moods', mood)"
                >{{ mood }}</span>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn-cancel" @click="closeTagEditor">取消</button>
            <button class="btn-submit" @click="applyTags">确认</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import api from "../../api";
import { useRouter } from "vue-router";

const router = useRouter();
const songs = ref([]);
const msg = ref("");
const msgType = ref("success");
const adminUserId = ref(null);

// 上传相关
const showUploadModal = ref(false);
const uploading = ref(false);
const fileInput = ref(null);
const uploadForm = ref({
  title: "",
  artist: "",
  genres: [],
  languages: [],
  themes: [],
  scenes: [],
  moods: [],
  file: null,
});

// 分类选项
const categoryOptions = {
  genre: ['流行', '电子', '轻音乐', '民谣', '说唱', '摇滚', '爵士', '节奏布鲁斯', '布鲁斯', '古典风格', '后摇', '古风', '中国风', '乡村', '金属', '新世纪', '世界音乐', '中国传统'],
  language: ['国语', '粤语', '英语', '拉丁', '韩语', '拉丁语'],
  theme: ['经典老歌', '网络歌曲', '影视原声', 'KTV金曲', '现场音乐', '官方歌单', 'AI歌单', '私藏'],
  scene: ['夜店', '学习工作', '运动', '睡觉前', '咖啡馆', '旅行', '派对'],
  mood: ['伤感', '快乐', '励志','治愈', '安静', '思念', '甜蜜', '寂寞'],
};

// 分类编辑弹窗
const showTagEditor = ref(false);
const editingSong = ref(null);
const editingTags = ref({
  genres: [],
  languages: [],
  themes: [],
  scenes: [],
  moods: [],
});

// 详情编辑弹窗
const showDetailEditor = ref(false);
const savingDetail = ref(false);
const coverInput = ref(null);
const detailForm = ref({
  id: null,
  title: "",
  album: "",
  release_date: "",
  lyrics: "",
  cover_url: "",
  coverPreview: "",
  coverFile: null,
});

// 切换上传表单标签
const toggleUploadTag = (field, value) => {
  const arr = uploadForm.value[field];
  const idx = arr.indexOf(value);
  if (idx > -1) {
    arr.splice(idx, 1);
  } else {
    arr.push(value);
  }
};

// 切换编辑标签
const toggleEditTag = (field, value) => {
  const arr = editingTags.value[field];
  const idx = arr.indexOf(value);
  if (idx > -1) {
    arr.splice(idx, 1);
  } else {
    arr.push(value);
  }
};

// 打开分类编辑器
const openTagEditor = (song) => {
  editingSong.value = song;
  // 解析现有的 genre 和 tags
  const genreArr = song.editGenre ? song.editGenre.split(',').map(s => s.trim()) : [];
  const tagsArr = song.editTags ? song.editTags.split(',').map(s => s.trim()) : [];
  const allTags = [...genreArr, ...tagsArr];
  
  editingTags.value = {
    genres: allTags.filter(t => categoryOptions.genre.includes(t)),
    languages: allTags.filter(t => categoryOptions.language.includes(t)),
    themes: allTags.filter(t => categoryOptions.theme.includes(t)),
    scenes: allTags.filter(t => categoryOptions.scene.includes(t)),
    moods: allTags.filter(t => categoryOptions.mood.includes(t)),
  };
  showTagEditor.value = true;
};

// 关闭分类编辑器
const closeTagEditor = () => {
  showTagEditor.value = false;
  editingSong.value = null;
};

// 应用分类标签
const applyTags = () => {
  if (editingSong.value) {
    // 流派作为 genre
    editingSong.value.editGenre = editingTags.value.genres.join(',');
    // 其他作为 tags
    const otherTags = [
      ...editingTags.value.languages,
      ...editingTags.value.themes,
      ...editingTags.value.scenes,
      ...editingTags.value.moods,
    ];
    editingSong.value.editTags = otherTags.join(',');
  }
  closeTagEditor();
};

// 打开详情编辑器
const openDetailEditor = (song) => {
  detailForm.value = {
    id: song.id,
    title: song.title,
    album: song.album || "",
    release_date: song.release_date || "",
    lyrics: song.lyrics || "",
    cover_url: song.cover_url || "",
    coverPreview: "",
    coverFile: null,
  };
  showDetailEditor.value = true;
};

// 关闭详情编辑器
const closeDetailEditor = () => {
  showDetailEditor.value = false;
  detailForm.value = {
    id: null,
    title: "",
    album: "",
    release_date: "",
    lyrics: "",
    cover_url: "",
    coverPreview: "",
    coverFile: null,
  };
};

// 触发封面上传
const triggerCoverUpload = () => {
  coverInput.value?.click();
};

// 封面文件选择
const onCoverChange = (e) => {
  const file = e.target.files[0];
  if (file) {
    detailForm.value.coverFile = file;
    detailForm.value.coverPreview = URL.createObjectURL(file);
  }
};

// 保存详情
const saveDetail = async () => {
  savingDetail.value = true;
  try {
    // 先保存基本信息
    await api.put(`/admin/songs/${detailForm.value.id}?admin_user_id=${adminUserId.value}`, {
      album: detailForm.value.album,
      release_date: detailForm.value.release_date,
      lyrics: detailForm.value.lyrics,
      admin_user_id: adminUserId.value,
    });
    
    // 如果有封面文件，上传封面
    if (detailForm.value.coverFile) {
      const formData = new FormData();
      formData.append("cover", detailForm.value.coverFile);
      await api.post(`/admin/songs/${detailForm.value.id}/cover?admin_user_id=${adminUserId.value}`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
    }
    
    msg.value = "详情保存成功";
    msgType.value = "success";
    closeDetailEditor();
    loadSongs();
  } catch (e) {
    msg.value = e.response?.data?.msg || "保存失败";
    msgType.value = "error";
  } finally {
    savingDetail.value = false;
  }
};

// 文件选择
const onFileChange = (e) => {
  const file = e.target.files[0];
  if (file) {
    uploadForm.value.file = file;
  }
};

// 关闭上传弹窗
const closeUploadModal = () => {
  showUploadModal.value = false;
  uploadForm.value = {
    title: "",
    artist: "",
    genres: [],
    languages: [],
    themes: [],
    scenes: [],
    moods: [],
    file: null,
  };
  if (fileInput.value) {
    fileInput.value.value = "";
  }
};

// 上传歌曲
const uploadSong = async () => {
  if (!uploadForm.value.title) {
    msg.value = "请输入歌曲名称";
    msgType.value = "error";
    return;
  }
  if (!uploadForm.value.file) {
    msg.value = "请选择音频文件";
    msgType.value = "error";
    return;
  }

  uploading.value = true;
  const formData = new FormData();
  formData.append("title", uploadForm.value.title);
  formData.append("artist", uploadForm.value.artist);
  // 流派作为 genre
  formData.append("genre", uploadForm.value.genres.join(','));
  // 其他分类作为 tags
  const allTags = [
    ...uploadForm.value.languages,
    ...uploadForm.value.themes,
    ...uploadForm.value.scenes,
    ...uploadForm.value.moods,
  ];
  formData.append("tags", allTags.join(','));
  formData.append("upload_user_id", adminUserId.value);
  formData.append("file", uploadForm.value.file);

  try {
    await api.post("/songs", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    msg.value = "上传成功";
    msgType.value = "success";
    closeUploadModal();
    loadSongs();
  } catch (e) {
    msg.value = e.response?.data?.msg || "上传失败";
    msgType.value = "error";
  } finally {
    uploading.value = false;
  }
};

const loadSongs = async () => {
  if (!adminUserId.value) {
    msg.value = "请先以管理员身份登录";
    msgType.value = "error";
    return;
  }
  try {
    const res = await api.get("/admin/songs", {
      params: {
        admin_user_id: adminUserId.value,
      },
    });
    songs.value = res.data.map((s) => ({
      ...s,
      editTitle: s.title,
      editArtist: s.artist,
      editGenre: s.genre || "",
      editTags: s.tags || "",
    }));
    msg.value = "";
  } catch (e) {
    msg.value = e.response?.data?.msg || "加载歌曲失败";
    msgType.value = "error";
  }
};

const saveSong = async (song) => {
  try {
    await api.put(`/admin/songs/${song.id}?admin_user_id=${adminUserId.value}`, {
      title: song.editTitle,
      artist: song.editArtist,
      genre: song.editGenre,
      tags: song.editTags,
      admin_user_id: adminUserId.value,
    });
    msg.value = "保存成功";
    msgType.value = "success";
    loadSongs();
  } catch (e) {
    msg.value = e.response?.data?.msg || "保存失败";
    msgType.value = "error";
  }
};

const deleteSong = async (song) => {
  if (!window.confirm(`确定要删除歌曲「${song.title}」吗？`)) {
    return;
  }
  try {
    await api.delete(`/admin/songs/${song.id}?admin_user_id=${adminUserId.value}`);
    msg.value = "删除成功";
    msgType.value = "success";
    loadSongs();
  } catch (e) {
    msg.value = e.response?.data?.msg || "删除失败";
    msgType.value = "error";
  }
};

onMounted(() => {
  const uid = localStorage.getItem("user_id");
  const isAdminFlag =
    localStorage.getItem("is_admin") === "1" ||
    localStorage.getItem("is_admin") === "true";

  if (!uid || !isAdminFlag) {
    alert("请先用管理员账号登录");
    router.push("/login");
    return;
  }
  adminUserId.value = uid;
  loadSongs();
});
</script>

<style scoped>
.admin-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  min-height: 100vh;
}

.admin-tabs {
  display: flex;
  gap: 4px;
  margin-bottom: 20px;
  background: #fff;
  padding: 6px;
  border-radius: 10px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
}

.tab-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 14px;
  color: #666;
  text-decoration: none;
  transition: all 0.2s;
}

.tab-item:hover {
  background: #f5f5f5;
  color: #333;
}

.tab-item.active {
  background: #31c27c;
  color: #fff;
}

.admin-header {
  display: flex;
  align-items: baseline;
  gap: 20px;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 2px solid #31c27c;
}

.admin-header h2 {
  margin: 0;
  font-size: 24px;
  color: #333;
}

.admin-info {
  font-size: 14px;
  color: #666;
}

.no-auth {
  text-align: center;
  padding: 60px 20px;
  background: #fff;
  border-radius: 8px;
}

.no-auth p {
  color: #ff6b6b;
  font-size: 16px;
  margin-top: 15px;
}

.admin-content {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

/* 统计信息 */
.stats-bar {
  display: flex;
  gap: 30px;
  padding: 20px;
  background: linear-gradient(135deg, #31c27c 0%, #28a86d 100%);
  border-radius: 8px 8px 0 0;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #fff;
}

.stat-label {
  font-size: 13px;
  color: rgba(255,255,255,0.8);
  margin-top: 4px;
}

/* 表格 */
.table-wrapper {
  overflow-x: auto;
}

.admin-table {
  width: 100%;
  border-collapse: collapse;
}

.admin-table th {
  background: #f8f9fa;
  padding: 14px 12px;
  text-align: left;
  font-size: 13px;
  color: #666;
  font-weight: 500;
  border-bottom: 1px solid #e9ecef;
}

.admin-table td {
  padding: 12px;
  border-bottom: 1px solid #f0f0f0;
  vertical-align: middle;
}

.admin-table tr:hover {
  background: #fafafa;
}

.col-id {
  width: 60px;
  text-align: center;
}

.col-title {
  width: 200px;
}

.col-artist {
  width: 150px;
}

.col-genre {
  width: 120px;
}

.col-tags {
  width: 150px;
}

.col-actions {
  width: 120px;
  text-align: center;
}

.action-btns {
  display: flex;
  justify-content: center;
  gap: 8px;
}

.action-btn {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.action-btn.detail {
  background: #e6f7ff;
  color: #1890ff;
}

.action-btn.detail:hover {
  background: #1890ff;
  color: #fff;
}

.action-btn.save {
  background: #f6ffed;
  color: #52c41a;
}

.action-btn.save:hover {
  background: #52c41a;
  color: #fff;
}

.action-btn.delete {
  background: #fff1f0;
  color: #ff4d4f;
}

.action-btn.delete:hover {
  background: #ff4d4f;
  color: #fff;
}

.edit-input {
  width: 100%;
  padding: 8px 10px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  font-size: 13px;
  transition: border-color 0.2s;
}

.edit-input:focus {
  outline: none;
  border-color: #31c27c;
}



.empty-state {
  padding: 40px;
  text-align: center;
  color: #999;
}

.message {
  padding: 12px 20px;
  margin: 15px;
  border-radius: 4px;
  font-size: 14px;
}

.message.success {
  background: #e8f5e9;
  color: #2e7d32;
}

.message.error {
  background: #ffebee;
  color: #c62828;
}

/* 添加按钮 */
.btn-add {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 20px;
  background: #fff;
  color: #31c27c;
  border: none;
  border-radius: 20px;
  font-size: 14px;
  cursor: pointer;
  margin-left: auto;
  transition: all 0.2s;
}

.btn-add:hover {
  background: #f0fff0;
}

/* 弹窗样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: #fff;
  border-radius: 12px;
  width: 500px;
  max-width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px;
  border-bottom: 1px solid #f0f0f0;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  color: #333;
}

.modal-close {
  width: 32px;
  height: 32px;
  border: none;
  background: #f5f5f5;
  border-radius: 50%;
  font-size: 20px;
  cursor: pointer;
  color: #666;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-close:hover {
  background: #e0e0e0;
}

.modal-body {
  padding: 20px;
}

.form-group {
  margin-bottom: 18px;
}

.form-group label {
  display: block;
  font-size: 14px;
  color: #333;
  margin-bottom: 8px;
  font-weight: 500;
}

.required {
  color: #ff6b6b;
}

.form-input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.2s;
  box-sizing: border-box;
}

.form-input:focus {
  outline: none;
  border-color: #31c27c;
}

.form-row {
  display: flex;
  gap: 15px;
}

.form-group.half {
  flex: 1;
}

/* 文件上传区域 */
.file-upload {
  position: relative;
  border: 2px dashed #e0e0e0;
  border-radius: 8px;
  padding: 30px;
  text-align: center;
  transition: all 0.2s;
  cursor: pointer;
}

.file-upload:hover {
  border-color: #31c27c;
  background: #f9fff9;
}

.file-upload.has-file {
  border-color: #31c27c;
  background: #f0fff0;
}

.file-upload input[type="file"] {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
}

.file-upload-content p {
  margin: 10px 0 0;
  font-size: 14px;
  color: #666;
}

.file-name {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: #31c27c !important;
  font-weight: 500;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 15px 20px;
  border-top: 1px solid #f0f0f0;
  background: #fafafa;
  border-radius: 0 0 12px 12px;
}

.btn-cancel {
  padding: 10px 24px;
  background: #fff;
  color: #666;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
}

.btn-cancel:hover {
  background: #f5f5f5;
}

.btn-submit {
  padding: 10px 24px;
  background: #31c27c;
  color: #fff;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
}

.btn-submit:hover:not(:disabled) {
  background: #28a86d;
}

.btn-submit:disabled {
  background: #ccc;
  cursor: not-allowed;
}

/* 标签选择器 */
.tag-selector {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-item {
  padding: 6px 14px;
  background: #f5f5f5;
  border: 1px solid #e0e0e0;
  border-radius: 16px;
  font-size: 13px;
  color: #666;
  cursor: pointer;
  transition: all 0.2s;
}

.tag-item:hover {
  border-color: #31c27c;
  color: #31c27c;
}

.tag-item.selected {
  background: #31c27c;
  border-color: #31c27c;
  color: #fff;
}

/* 标签编辑按钮 */
.tag-edit-btn {
  width: 100%;
  padding: 8px 10px;
  background: #f9f9f9;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  font-size: 12px;
  color: #666;
  cursor: pointer;
  text-align: left;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.tag-edit-btn:hover {
  border-color: #31c27c;
  color: #31c27c;
}

/* 分类编辑弹窗 */
.tag-editor-modal {
  width: 600px;
}

.tag-editor-modal .form-group {
  margin-bottom: 15px;
}

.tag-editor-modal .form-group label {
  font-size: 13px;
  color: #666;
  margin-bottom: 6px;
}

/* 详情编辑弹窗 */
.detail-editor-modal {
  width: 700px;
}

.detail-layout {
  display: flex;
  gap: 30px;
  margin-bottom: 20px;
}

.cover-section {
  flex-shrink: 0;
}

.cover-section label {
  display: block;
  font-size: 14px;
  color: #333;
  margin-bottom: 8px;
  font-weight: 500;
}

.cover-preview {
  width: 180px;
  height: 180px;
  border: 2px dashed #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.2s;
}

.cover-preview:hover {
  border-color: #31c27c;
}

.cover-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cover-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  color: #999;
  font-size: 13px;
}

.info-section {
  flex: 1;
}

.form-textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  font-size: 14px;
  line-height: 1.6;
  resize: vertical;
  box-sizing: border-box;
  font-family: inherit;
}

.form-textarea:focus {
  outline: none;
  border-color: #31c27c;
}


</style>
