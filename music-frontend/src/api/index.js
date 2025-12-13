import axios from "axios";

// ==================== API 地址配置 ====================
// 本地开发使用: "http://127.0.0.1:5000/api"
// 内网穿透使用: 改成你的 cpolar 后端地址
// =====================================================
const API_BASE_URL = "http://127.0.0.1:5000/api";

const api = axios.create({
  baseURL: API_BASE_URL,
});

export default api;
export { API_BASE_URL };