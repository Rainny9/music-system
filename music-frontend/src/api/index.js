import axios from "axios";

const api = axios.create({
  // TODO: 如果后端端口或地址变化，请改这里
  baseURL: "http://127.0.0.1:5000/api",
});

export default api;