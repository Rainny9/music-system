<template>
  <div>
    <h2>后台歌曲管理</h2>
    <p>当前管理员ID：{{ adminUserId }}</p>

    <div v-if="!adminUserId" style="color: red;">
      请先以管理员账号登录（用户名 admin / 密码 admin123，TODO: 上线前修改）
    </div>

    <table border="1" cellspacing="0" cellpadding="4" style="margin-top: 12px; width: 100%;">
      <thead>
        <tr>
          <th>ID</th>
          <th>歌名</th>
          <th>歌手</th>
          <th>分类(genre)</th>
          <th>标签(tags)</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="song in songs" :key="song.id">
          <td>{{ song.id }}</td>
          <td>
            <input v-model="song.editTitle" />
          </td>
          <td>
            <input v-model="song.editArtist" />
          </td>
          <td>
            <input v-model="song.editGenre" />
          </td>
          <td>
            <input v-model="song.editTags" />
          </td>
          <td>
            <button @click="saveSong(song)">保存</button>
            <button @click="deleteSong(song)">删除</button>
          </td>
        </tr>
      </tbody>
    </table>

    <p>{{ msg }}</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import api from "../../api";
import { useRouter } from "vue-router";

const router = useRouter();
const songs = ref([]);
const msg = ref("");
const adminUserId = ref(null);

const loadSongs = async () => {
  if (!adminUserId.value) {
    msg.value = "请先以管理员身份登录";
    return;
  }
  try {
    const res = await api.get("/admin/songs", {
      params: {
        admin_user_id: adminUserId.value, // TODO: 以后改为从 token 中获取
      },
    });
    // 给每条歌加上可编辑字段副本
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
  }
};

const saveSong = async (song) => {
  try {
    await api.put(
      `/admin/songs/${song.id}`,
      {
        title: song.editTitle,
        artist: song.editArtist,
        genre: song.editGenre,
        tags: song.editTags,
      },
      {
        params: {
          admin_user_id: adminUserId.value,
        },
      }
    );
    msg.value = "保存成功";
    loadSongs();
  } catch (e) {
    msg.value = e.response?.data?.msg || "保存失败";
  }
};

const deleteSong = async (song) => {
  if (!window.confirm(`确定要删除歌曲「${song.title}」吗？`)) {
    return;
  }
  try {
    await api.delete(`/admin/songs/${song.id}`, {
      params: {
        admin_user_id: adminUserId.value,
      },
    });
    msg.value = "删除成功";
    loadSongs();
  } catch (e) {
    msg.value = e.response?.data?.msg || "删除失败";
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