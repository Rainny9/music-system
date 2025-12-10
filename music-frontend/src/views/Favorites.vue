<template>
  <div>
    <h2>我的收藏</h2>
    <ul>
      <li v-for="song in songs" :key="song.id">
        {{ song.title }} - {{ song.artist }}
        <button @click="play(song)">播放</button>
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

const loadFavorites = async () => {
  const userId = localStorage.getItem("user_id");
  if (!userId) {
    alert("请先登录");
    router.push("/login");
    return;
  }
  const res = await api.get(`/users/${userId}/favorites`);
  songs.value = res.data;
};

const play = (song) => {
  currentSong.value = song;
};

onMounted(loadFavorites);
</script>