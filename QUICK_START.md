# 快速启动指南

## 问题诊断

如果遇到 404 错误，按以下步骤排查：

### 1. 检查后端服务状态

```bash
# 停止现有的后端服务（如果正在运行）
# Windows: Ctrl+C
# 或者关闭运行 python app.py 的终端窗口
```

### 2. 运行数据库迁移

```bash
cd music-backend
mysql -u root -p123456 music_db < migrations.sql
```

### 3. 重新启动后端服务

```bash
cd music-backend
python app.py
```

**重要**: 确保看到类似以下输出：
```
 * Running on http://127.0.0.1:5000
 * Restarting with stat
 * Debugger is active!
```

### 4. 测试 API 是否正常

在新的终端窗口运行：

```bash
cd music-backend
python test_api.py
```

如果看到状态码 200，说明 API 正常工作。

### 5. 启动前端服务

```bash
cd music-frontend
npm run dev
```

### 6. 访问应用

打开浏览器访问: `http://localhost:5173`

## 常见问题

### Q1: 后端启动报错 "ModuleNotFoundError: No module named 'api_extensions'"

**解决方案**: 确保 `api_extensions.py` 文件在 `music-backend` 目录下

### Q2: 前端请求返回 404

**原因**: 
1. 后端服务没有重启
2. 扩展 API 没有正确注册

**解决方案**:
1. 完全停止后端服务
2. 重新运行 `python app.py`
3. 检查终端输出是否有错误

### Q3: 数据库表不存在

**解决方案**:
```bash
mysql -u root -p123456 music_db < migrations.sql
```

### Q4: CORS 错误

**解决方案**: 
- 确保后端 `app.py` 中有 CORS 配置
- 已经配置好了，无需修改

### Q5: 前端页面空白

**解决方案**:
1. 打开浏览器开发者工具 (F12)
2. 查看 Console 标签页的错误信息
3. 查看 Network 标签页的请求状态

## 验证步骤

### 1. 验证后端 API

在浏览器访问以下 URL（需要先登录获取 user_id）:

- 歌单列表: `http://127.0.0.1:5000/api/playlists?user_id=1`
- 播放历史: `http://127.0.0.1:5000/api/users/1/history`
- 用户统计: `http://127.0.0.1:5000/api/users/1/stats`
- 排行榜: `http://127.0.0.1:5000/api/songs/ranking`

如果返回 JSON 数据（即使是空数组 `[]`），说明 API 正常。

### 2. 验证前端路由

在浏览器访问以下 URL:

- 播放历史: `http://localhost:5173/history`
- 我的歌单: `http://localhost:5173/playlists`
- 个人中心: `http://localhost:5173/profile`

如果页面正常显示（不是 404），说明路由配置正确。

## 调试技巧

### 查看后端日志

后端运行时会在终端输出请求日志：
```
127.0.0.1 - - [14/Dec/2025 10:30:45] "GET /api/playlists?user_id=1 HTTP/1.1" 200 -
```

- `200`: 成功
- `404`: 路由不存在
- `500`: 服务器错误

### 查看前端网络请求

1. 打开浏览器开发者工具 (F12)
2. 切换到 Network 标签页
3. 刷新页面
4. 查看请求的状态码和响应内容

### 检查数据库表

```bash
mysql -u root -p123456 music_db

# 查看所有表
SHOW TABLES;

# 查看歌单表结构
DESC playlist;

# 查看播放历史表结构
DESC play_history;

# 退出
EXIT;
```

## 完整重启流程

如果遇到任何问题，按以下步骤完整重启：

```bash
# 1. 停止所有服务
# 关闭所有终端窗口或按 Ctrl+C

# 2. 运行数据库迁移
cd music-backend
mysql -u root -p123456 music_db < migrations.sql

# 3. 启动后端（新终端窗口）
cd music-backend
python app.py

# 4. 测试 API（新终端窗口）
cd music-backend
python test_api.py

# 5. 启动前端（新终端窗口）
cd music-frontend
npm run dev

# 6. 打开浏览器
# 访问 http://localhost:5173
```

## 联系支持

如果以上步骤都无法解决问题，请提供：

1. 后端终端的完整输出
2. 浏览器控制台的错误信息
3. 浏览器 Network 标签页的请求详情
4. 数据库表列表 (`SHOW TABLES;` 的输出)

这样可以更快地定位问题！
