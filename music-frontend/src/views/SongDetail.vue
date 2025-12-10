<template>
  <div>
    <button @click="$router.back()">返回</button>
    <h2>歌曲详情</h2>
    <p>歌曲ID：{{ songId }}</p>

    <h3>评论</h3>
    <ul>
      <li v-for="c in comments" :key="c.id">
        [{{ c.created_at }}] 用户{{ c.user_id }}：{{ c.content }}
      </li>
    </ul>

    <div>
      <textarea v-model="commentText" placeholder="写下你的评论"></textarea>
      <br />
      <button @click="addComment">发表评论</button>
      <p>{{ msg }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import api from "../api";

const route = useRoute();
const router = useRouter();
const songId = Number(route.params.id);
const comments = ref([]);
const commentText = ref("");
const msg = ref("");

const loadComments = async () => {
  const res = await api.get(`/songs/${songId}/comments`);
  comments.value = res.data;
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
      user_id: Number(userId), // TODO: 以后改为从 token 中解析
      content: commentText.value,
    });
    commentText.value = "";
    msg.value = "评论成功";
    loadComments();
  } catch (e) {
    msg.value = e.response?.data?.msg || "评论失败";
  }
};

onMounted(loadComments);
</script>