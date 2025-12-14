-- 数据库迁移脚本
-- 添加新功能所需的表和字段

-- 1. 为 Song 表添加新字段
ALTER TABLE song ADD COLUMN IF NOT EXISTS play_count INT DEFAULT 0;
ALTER TABLE song ADD COLUMN IF NOT EXISTS like_count INT DEFAULT 0;
ALTER TABLE song ADD COLUMN IF NOT EXISTS artist_id INT NULL;

-- 2. 为 User 表添加头像字段（如果还没有）
ALTER TABLE user ADD COLUMN IF NOT EXISTS avatar_path VARCHAR(300) NULL;

-- 3. 创建点赞表
CREATE TABLE IF NOT EXISTS song_like (
    id INT AUTO_INCREMENT PRIMARY KEY,
    song_id INT NOT NULL,
    user_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (song_id) REFERENCES song(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    UNIQUE KEY unique_like (song_id, user_id)
);

-- 4. 创建歌单表
CREATE TABLE IF NOT EXISTS playlist (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    cover_path VARCHAR(300),
    is_public BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
);

-- 5. 创建歌单-歌曲关联表
CREATE TABLE IF NOT EXISTS playlist_song (
    id INT AUTO_INCREMENT PRIMARY KEY,
    playlist_id INT NOT NULL,
    song_id INT NOT NULL,
    added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (playlist_id) REFERENCES playlist(id) ON DELETE CASCADE,
    FOREIGN KEY (song_id) REFERENCES song(id) ON DELETE CASCADE,
    UNIQUE KEY unique_playlist_song (playlist_id, song_id)
);

-- 6. 创建歌手表
CREATE TABLE IF NOT EXISTS artist (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    avatar_path VARCHAR(300),
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 7. 创建歌手关注表
CREATE TABLE IF NOT EXISTS artist_follow (
    id INT AUTO_INCREMENT PRIMARY KEY,
    artist_id INT NOT NULL,
    user_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (artist_id) REFERENCES artist(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    UNIQUE KEY unique_follow (artist_id, user_id)
);

-- 8. 创建播放历史表
CREATE TABLE IF NOT EXISTS play_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    song_id INT NOT NULL,
    play_progress INT DEFAULT 0,
    played_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (song_id) REFERENCES song(id) ON DELETE CASCADE,
    INDEX idx_user_played (user_id, played_at)
);

-- 9. 创建搜索历史表
CREATE TABLE IF NOT EXISTS search_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    keyword VARCHAR(200) NOT NULL,
    searched_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    INDEX idx_user_searched (user_id, searched_at)
);

-- 10. 为 User 表添加个人资料字段
ALTER TABLE user ADD COLUMN IF NOT EXISTS gender VARCHAR(10) NULL;
ALTER TABLE user ADD COLUMN IF NOT EXISTS birthday VARCHAR(20) NULL;
ALTER TABLE user ADD COLUMN IF NOT EXISTS region VARCHAR(100) NULL;

-- 完成！
SELECT 'Migration completed successfully!' AS status;


-- 排行榜历史记录表
CREATE TABLE IF NOT EXISTS rank_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    song_id INT NOT NULL,
    `rank` INT NOT NULL,
    play_count INT DEFAULT 0,
    record_date DATE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (song_id) REFERENCES song(id) ON DELETE CASCADE,
    UNIQUE KEY unique_song_date (song_id, record_date)
);
