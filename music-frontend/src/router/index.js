import { createRouter, createWebHistory } from "vue-router";
import Home from "../views/Home.vue";
import Login from "../views/Login.vue";
import Register from "../views/Register.vue";
import SongDetail from "../views/SongDetail.vue";
import Favorites from "../views/Favorites.vue";
import AdminSongs from "../views/admin/AdminSongs.vue";
import AdminUsers from "../views/admin/AdminUsers.vue";
import AdminAnnouncements from "../views/admin/AdminAnnouncements.vue";
import SearchResult from "../views/SearchResult.vue";

const routes = [
  { path: "/", name: "Home", component: Home },
  { path: "/login", name: "Login", component: Login },
  { path: "/register", name: "Register", component: Register },
  { path: "/songs/:id", name: "SongDetail", component: SongDetail },
  { path: "/favorites", name: "Favorites", component: Favorites },
  { path: "/admin/songs", name: "AdminSongs", component: AdminSongs },
  { path: "/admin/users", name: "AdminUsers", component: AdminUsers },
  { path: "/admin/announcements", name: "AdminAnnouncements", component: AdminAnnouncements },
  { path: "/search", name: "SearchResult", component: SearchResult },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;