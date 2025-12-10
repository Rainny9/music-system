<template>
  <div>
    <h2>歌曲列表</h2>

    <!-- 搜索 + 筛选区域 -->
<div style="margin-bottom: 12px;">
  <input
    v-model="keyword"
    placeholder="搜索歌名 / 歌手 / 标签"
    style="width: 260px; margin-right: 8px;"
  />

  <select v-model="selectedGenre" style="margin-right: 8px;">
    <option value="">全部分类</option>
    <option v-for="g in genres" :key="g" :value="g">
      {{ g }}
    </option>
  </select>

  <input
    v-model="tag"
    placeholder="标签（如：伤感）"
    style="width: 140px; margin-right: 8px;"
  />

  <button @click="loadSongs">搜索/筛选</button>
</div>

    <button @click="checkLogin">检查是否已登录</button>
    <p>当前用户ID：{{ userId || "未登录" }}</p>

    <!-- 简单上传功能 -->
    <div style="margin: 16px 0; border: 1px solid #ccc; padding: 8px;">
      <h3>上传歌曲（测试功能）</h3>
      <input v-model="uploadTitle" placeholder="歌曲名称" />
      <input v-model="uploadArtist" placeholder="歌手" />
      <input v-model="uploadGenre" placeholder="分类（如：流行）" />
      <input v-model="uploadTags" placeholder="标签（逗号分隔，如：伤感,中文）" />
      <input type="file" @change="onFileChange" />
      <button @click="uploadSong">上传</button>
      <p>{{ uploadMsg }}</p>
    </div>

    <ul>
      <li v-for="song in songs" :key="song.id">
        <span @click="goDetail(song.id)" style="cursor: pointer;">
          {{ song.title }} - {{ song.artist }}
        </span>
        <button @click="play(song)">播放</button>
        <button @click="toggleFavorite(song)">收藏/取消收藏</button>
        <button @click="goDetail(song.id)">评论</button>
        <a :href="song.download_url" target="_blank">下载</a>
      </li>
    </ul>

    <div v-if="currentSong">
      <h3>正在播放：{{ currentSong.title }} - {{ currentSong.artist }}</h3>
      <audio :src="currentSong.play_url" controls autoplay></audio>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import api from "../api";
import { useRouter } from "vue-router";

const router = useRouter();
const songs = ref([]);
const currentSong = ref(null);
const userId = ref(null);

// 搜索与筛选
const keyword = ref("");
const tag = ref("");
const genres = ref([]);      // 分类列表（下拉框用）
const selectedGenre = ref(""); // 当前选择的分类

// 上传相关
const uploadTitle = ref("");
const uploadArtist = ref("");
const uploadFile = ref(null);
const uploadMsg = ref("");
const uploadGenre = ref("");
const uploadTags = ref("");

const loadSongs = async () => {
  const res = await api.get("/songs", {
    params: {
      keyword: keyword.value || undefined,
      genre: selectedGenre.value || undefined,
      tag: tag.value || undefined,
    },
  });
  songs.value = res.data;
};

//新建函数，加载分类列表
const loadGenres = async () => {
  try {
    const res = await api.get("/genres");
    genres.value = res.data;
  } catch (e) {
    console.error("加载分类失败", e);
  }
};

const play = (song) => {
  currentSong.value = song;
};

const checkLogin = () => {
  const id = localStorage.getItem("user_id");
  if (id) {
    userId.value = id;
  } else {
    alert("还未登录，将跳转到登录页面");
    router.push("/login");
  }
};

const goDetail = (id) => {
  router.push(`/songs/${id}`);
};

const toggleFavorite = async (song) => {
  const id = localStorage.getItem("user_id");
  if (!id) {
    alert("请先登录");
    router.push("/login");
    return;
  }
  await api.post(`/songs/${song.id}/favorite`, {
    user_id: Number(id), // TODO: 以后用 token 中的用户信息
  });
  alert("收藏状态已切换");
};

const onFileChange = (e) => {
  uploadFile.value = e.target.files[0];
};

const uploadSong = async () => {
  const id = localStorage.getItem("user_id");
  if (!id) {
    alert("请先登录再上传");
    router.push("/login");
    return;
  }
  if (!uploadTitle.value || !uploadFile.value) {
    uploadMsg.value = "歌曲名称和文件不能为空";
    return;
  }

  const formData = new FormData();
  formData.append("title", uploadTitle.value);
  formData.append("artist", uploadArtist.value); // TODO: 你可以改成必填
  formData.append("upload_user_id", id);
  formData.append("file", uploadFile.value);
  formData.append("genre", uploadGenre.value);
  formData.append("tags", uploadTags.value);

  try {
    const res = await api.post("/songs", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    uploadMsg.value = res.data.msg || "上传成功";
    uploadTitle.value = "";
    uploadArtist.value = "";
    uploadFile.value = null;
    uploadGenre.value = "";
    uploadTags.value = "";
    loadSongs(); // 刷新列表
  } catch (e) {
    uploadMsg.value = e.response?.data?.msg || "上传失败";
  }
};

onMounted(() => {
  userId.value = localStorage.getItem("user_id");
  loadGenres(); // 加载分类下拉
  loadSongs();  // 加载歌曲列表
});
</script>