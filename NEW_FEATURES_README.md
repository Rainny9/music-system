# 新功能使用指南

## 已实现的功能

### 1. 播放历史页面 (`/history`)
- ✅ 查看所有播放过的歌曲
- ✅ 显示播放时间（刚刚、X分钟前、X小时前等）
- ✅ 点击歌曲重新播放
- ✅ 删除单条历史记录
- ✅ 清空所有历史记录

### 2. 歌单管理页面 (`/playlists`)
- ✅ 创建新歌单
- ✅ 编辑歌单信息（名称、简介、公开/私密）
- ✅ 删除歌单
- ✅ 查看歌单列表
- ✅ 显示歌曲数量

### 3. 个人中心页面 (`/profile`)
- ✅ 查看个人信息
- ✅ 上传/更换头像
- ✅ 修改用户名
- ✅ 修改密码
- ✅ 统计数据展示：
  - 收藏歌曲数
  - 创建歌单数
  - 累计听歌时长
  - 本周播放次数

### 4. 顶部导航栏更新
- ✅ 添加"我的歌单"入口
- ✅ 添加"播放历史"入口
- ✅ 添加"个人中心"入口
- ✅ 登录后才显示用户相关功能

## 部署步骤

### 后端部署

1. **运行数据库迁移**
```bash
cd music-backend
mysql -u root -p123456 music_db < migrations.sql
```

2. **确保后端已注册扩展API**
在 `app.py` 末尾应该有：
```python
from api_extensions import register_extensions
register_extensions(app, db, Song, User, require_admin)
```

3. **启动后端服务**
```bash
python app.py
```

### 前端部署

1. **安装依赖**（如果还没安装）
```bash
cd music-frontend
npm install
```

2. **启动开发服务器**
```bash
npm run dev
```

3. **访问应用**
打开浏览器访问 `http://localhost:5173`

## API 端点说明

### 播放历史相关
- `GET /api/users/{user_id}/history` - 获取播放历史
- `POST /api/users/{user_id}/history` - 添加播放记录
- `DELETE /api/users/{user_id}/history/{history_id}` - 删除单条记录
- `DELETE /api/users/{user_id}/history/clear` - 清空历史

### 歌单相关
- `GET /api/playlists?user_id={user_id}` - 获取用户歌单列表
- `POST /api/playlists` - 创建歌单
- `GET /api/playlists/{playlist_id}` - 获取歌单详情
- `PUT /api/playlists/{playlist_id}` - 更新歌单
- `DELETE /api/playlists/{playlist_id}` - 删除歌单
- `POST /api/playlists/{playlist_id}/songs` - 批量添加歌曲到歌单

### 个人中心相关
- `GET /api/users/{user_id}/stats` - 获取用户统计数据
- `PUT /api/users/{user_id}/profile` - 更新用户资料
- `PUT /api/users/{user_id}/password` - 修改密码
- `POST /api/users/{user_id}/avatar` - 上传头像

### 其他功能
- `POST /api/songs/{song_id}/like` - 点赞/取消点赞
- `POST /api/songs/{song_id}/play_count` - 增加播放次数
- `GET /api/songs/{song_id}/recommend` - 获取推荐歌曲
- `GET /api/songs/ranking` - 获取排行榜

## 使用说明

### 播放历史
1. 登录后点击顶部导航栏的"播放历史"
2. 查看所有播放过的歌曲
3. 点击歌曲封面可以重新播放
4. 点击删除按钮可以删除单条记录
5. 点击"清空历史"可以清空所有记录

### 歌单管理
1. 登录后点击顶部导航栏的"我的歌单"
2. 点击"创建歌单"按钮创建新歌单
3. 填写歌单名称和简介
4. 选择是否公开歌单
5. 点击歌单卡片可以查看详情
6. 点击编辑按钮可以修改歌单信息
7. 点击删除按钮可以删除歌单

### 个人中心
1. 登录后点击顶部导航栏的"个人中心"
2. 查看个人统计数据
3. 点击头像可以上传新头像
4. 点击用户名旁的编辑按钮可以修改用户名
5. 点击密码旁的"修改"按钮可以修改密码

## 注意事项

1. **数据库迁移**：首次使用前必须运行 `migrations.sql` 创建新表
2. **登录状态**：所有用户功能都需要登录后才能使用
3. **文件上传**：头像上传会保存到 `music-backend/uploads` 目录
4. **播放历史**：目前播放历史需要手动记录，可以在播放器中集成自动记录功能
5. **歌单歌曲**：添加歌曲到歌单的功能需要在歌曲列表页面集成

## 待实现功能

以下功能已有API支持，但前端页面待完善：

- [ ] 歌单详情页面（查看歌单中的所有歌曲）
- [ ] 歌曲列表页面的"添加到歌单"功能
- [ ] 歌手主页
- [ ] 高级搜索（多条件筛选）
- [ ] 数据统计可视化（管理员端）
- [ ] 搜索历史管理

## 故障排除

### 后端启动失败
- 检查数据库连接配置
- 确保已运行数据库迁移脚本
- 检查 `api_extensions.py` 文件是否存在

### 前端页面空白
- 检查浏览器控制台错误信息
- 确保后端服务正在运行
- 检查 API 地址配置（`src/api/index.js`）

### 功能无法使用
- 确保已登录
- 检查浏览器控制台的网络请求
- 查看后端日志输出

## 技术栈

- **后端**: Flask + SQLAlchemy + MySQL
- **前端**: Vue 3 + Vue Router + Axios
- **样式**: 原生 CSS（Scoped）

## 联系支持

如有问题，请检查：
1. 数据库是否正确迁移
2. 后端服务是否正常运行
3. 前端路由配置是否正确
4. API 地址是否配置正确
