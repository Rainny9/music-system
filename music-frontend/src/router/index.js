import { createRouter, createWebHistory } from "vue-router";
import Home from "../views/Home.vue";
import Login from "../views/Login.vue";
import SongDetail from "../views/SongDetail.vue";
import Favorites from "../views/Favorites.vue";
import AdminSongs from "../views/admin/AdminSongs.vue";//新建后台页面

const routes = [
  { path: "/", name: "Home", component: Home },
  { path: "/login", name: "Login", component: Login },
  { path: "/songs/:id", name: "SongDetail", component: SongDetail },
  { path: "/favorites", name: "Favorites", component: Favorites },
  { path: "/admin/songs", name: "AdminSongs", component: AdminSongs },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;