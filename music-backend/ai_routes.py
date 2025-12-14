# AI功能API路由
from datetime import datetime
from flask import request, jsonify
from ai_service import (
    get_personalized_recommendations,
    auto_generate_tags,
    content_moderation,
    generate_playlist_recommendations,
    fetch_song_info,
    smart_sort_songs
)
from audio_recognition import recognize_by_description


def register_ai_routes(app, db, Song, User, Favorite, PlayHistory, song_to_dict):
    """注册AI相关API路由"""

    # ========== 1. 智能推荐 API ==========
    @app.route("/api/ai/recommendations", methods=["GET"])
    def ai_recommendations():
        """获取AI个性化推荐"""
        user_id = request.args.get("user_id")
        limit = int(request.args.get("limit", 10))
        base_url = request.host_url.strip("/")
        
        if not user_id:
            # 无用户ID，返回热门歌曲
            songs = Song.query.order_by(Song.play_count.desc()).limit(limit).all()
            return jsonify({
                "type": "popular",
                "songs": [song_to_dict(s, base_url) for s in songs]
            })
        
        # 获取用户历史
        from sqlalchemy import desc
        histories = PlayHistory.query.filter_by(user_id=user_id)\
            .order_by(desc(PlayHistory.played_at)).limit(30).all()
        
        user_history = []
        for h in histories:
            song = Song.query.get(h.song_id)
            if song:
                user_history.append({
                    "id": song.id,
                    "title": song.title,
                    "artist": song.artist,
                    "genre": song.genre,
                    "tags": song.tags
                })
        
        # 获取所有歌曲
        all_songs = Song.query.all()
        all_songs_data = [{
            "id": s.id,
            "title": s.title,
            "artist": s.artist,
            "genre": s.genre,
            "tags": s.tags
        } for s in all_songs]
        
        # 调用AI推荐
        recommended_ids = get_personalized_recommendations(user_history, all_songs_data, limit)
        
        if recommended_ids:
            songs = Song.query.filter(Song.id.in_(recommended_ids)).all()
            # 按推荐顺序排序
            songs_dict = {s.id: s for s in songs}
            ordered_songs = [songs_dict[sid] for sid in recommended_ids if sid in songs_dict]
            return jsonify({
                "type": "personalized",
                "songs": [song_to_dict(s, base_url) for s in ordered_songs]
            })
        else:
            # AI推荐失败，返回热门歌曲
            songs = Song.query.order_by(Song.play_count.desc()).limit(limit).all()
            return jsonify({
                "type": "popular",
                "songs": [song_to_dict(s, base_url) for s in songs]
            })

    # ========== 2. 智能排序 API ==========
    @app.route("/api/ai/smart-sort", methods=["GET"])
    def ai_smart_sort():
        """根据用户偏好智能排序歌曲"""
        user_id = request.args.get("user_id")
        genre = request.args.get("genre", "")
        tag = request.args.get("tag", "")
        sort_type = request.args.get("sort", "smart")  # smart=智能排序, latest=最新上传
        limit = request.args.get("limit", type=int)
        base_url = request.host_url.strip("/")
        
        from sqlalchemy import desc
        
        # 构建查询条件
        query = Song.query
        if genre:
            query = query.filter(Song.genre.contains(genre))
        if tag:
            # 支持多个标签，用逗号分隔
            for t in tag.split(','):
                t = t.strip()
                if t:
                    query = query.filter(
                        db.or_(Song.tags.contains(t), Song.genre.contains(t))
                    )
        
        # 最新上传排序 - 按创建时间降序
        if sort_type == "latest":
            songs = query.order_by(desc(Song.created_at)).all()
            if limit:
                songs = songs[:limit]
            return jsonify([song_to_dict(s, base_url) for s in songs])
        
        # 智能排序
        songs = query.all()
        songs_data = [{
            "id": s.id,
            "title": s.title,
            "artist": s.artist,
            "genre": s.genre,
            "tags": s.tags,
            "play_count": s.play_count or 0
        } for s in songs]
        
        if not user_id:
            # 无用户ID，按播放次数排序
            songs_data.sort(key=lambda x: x['play_count'], reverse=True)
            sorted_ids = [s['id'] for s in songs_data]
        else:
            # 获取用户播放历史
            histories = PlayHistory.query.filter_by(user_id=user_id)\
                .order_by(desc(PlayHistory.played_at)).limit(50).all()
            
            user_history = []
            for h in histories:
                song = Song.query.get(h.song_id)
                if song:
                    user_history.append({
                        "id": song.id,
                        "title": song.title,
                        "artist": song.artist,
                        "genre": song.genre,
                        "tags": song.tags
                    })
            
            # 获取用户收藏
            favorites = Favorite.query.filter_by(user_id=user_id).all()
            favorite_ids = [f.song_id for f in favorites]
            
            # 智能排序
            sorted_ids = smart_sort_songs(songs_data, user_history, favorite_ids)
        
        # 按排序后的ID顺序返回歌曲
        songs_dict = {s.id: s for s in songs}
        result = []
        for sid in sorted_ids:
            if sid in songs_dict:
                result.append(song_to_dict(songs_dict[sid], base_url))
        
        if limit:
            result = result[:limit]
        
        return jsonify(result)

    # ========== 3. 自动打标签 API ==========
    @app.route("/api/ai/auto-tags", methods=["POST"])
    def ai_auto_tags():
        """自动为歌曲生成标签"""
        data = request.json
        title = data.get("title", "")
        artist = data.get("artist", "")
        lyrics = data.get("lyrics", "")
        genre = data.get("genre", "")
        
        if not title:
            return jsonify({"msg": "title required"}), 400
        
        result = auto_generate_tags(title, artist, lyrics, genre)
        return jsonify(result)

    @app.route("/api/ai/songs/<int:song_id>/auto-tags", methods=["POST"])
    def ai_song_auto_tags(song_id):
        """为指定歌曲自动生成并更新标签"""
        song = Song.query.get_or_404(song_id)
        
        result = auto_generate_tags(song.title, song.artist, song.lyrics, song.genre)
        
        # 更新歌曲标签
        if result.get("genre"):
            song.genre = result["genre"]
        if result.get("tags"):
            song.tags = ",".join(result["tags"]) if isinstance(result["tags"], list) else result["tags"]
        
        db.session.commit()
        
        base_url = request.host_url.strip("/")
        return jsonify({
            "msg": "tags updated",
            "result": result,
            "song": song_to_dict(song, base_url)
        })

    # ========== 3. 内容审核 API ==========
    @app.route("/api/ai/moderation", methods=["POST"])
    def ai_moderation():
        """内容审核"""
        data = request.json
        content = data.get("content", "")
        content_type = data.get("type", "comment")  # comment, lyrics, description
        
        if not content:
            return jsonify({"msg": "content required"}), 400
        
        result = content_moderation(content, content_type)
        return jsonify(result)

    @app.route("/api/ai/moderation/comment", methods=["POST"])
    def ai_moderate_comment():
        """评论审核 - 在发表评论前调用"""
        data = request.json
        content = data.get("content", "")
        
        if not content:
            return jsonify({"msg": "content required"}), 400
        
        result = content_moderation(content, "comment")
        return jsonify(result)

    # ========== 4. 歌单推荐 API ==========
    @app.route("/api/ai/playlist-themes", methods=["GET"])
    def ai_playlist_themes():
        """获取推荐的歌单主题"""
        user_id = request.args.get("user_id")
        
        if not user_id:
            return jsonify({"themes": [
                {"name": "热门金曲", "description": "当下最火的歌曲"},
                {"name": "经典老歌", "description": "那些年我们听过的歌"},
                {"name": "轻音乐", "description": "放松心情的纯音乐"}
            ]})
        
        # 获取用户收藏
        from sqlalchemy import desc
        favorites = Favorite.query.filter_by(user_id=user_id).all()
        user_favorites = []
        for f in favorites[:20]:
            song = Song.query.get(f.song_id)
            if song:
                user_favorites.append({
                    "title": song.title,
                    "artist": song.artist,
                    "genre": song.genre
                })
        
        # 获取用户历史
        histories = PlayHistory.query.filter_by(user_id=user_id)\
            .order_by(desc(PlayHistory.played_at)).limit(20).all()
        user_history = []
        for h in histories:
            song = Song.query.get(h.song_id)
            if song:
                user_history.append({
                    "title": song.title,
                    "artist": song.artist,
                    "genre": song.genre
                })
        
        result = generate_playlist_recommendations(user_favorites, user_history)
        return jsonify(result)

    # ========== 5. 听歌识曲 API ==========
    @app.route("/api/ai/recognize", methods=["POST"])
    def ai_recognize_song():
        """听歌识曲 - 通过描述识别"""
        data = request.json
        description = data.get("description", "")
        
        if not description:
            return jsonify({"msg": "description required"}), 400
        
        # 获取所有歌曲
        all_songs = Song.query.all()
        all_songs_data = [{
            "id": s.id,
            "title": s.title,
            "artist": s.artist,
            "genre": s.genre,
            "tags": s.tags,
            "lyrics": s.lyrics[:200] if s.lyrics else ""
        } for s in all_songs]
        
        result = recognize_by_description(description, all_songs_data)
        
        # 如果匹配成功，返回完整歌曲信息
        if result.get("matched") and result.get("song_id"):
            song = Song.query.get(result["song_id"])
            if song:
                base_url = request.host_url.strip("/")
                result["song"] = song_to_dict(song, base_url)
        
        return jsonify(result)

    @app.route("/api/ai/recognize/audio", methods=["POST"])
    def ai_recognize_audio():
        """听歌识曲 - 通过音频文件识别"""
        if "audio" not in request.files:
            return jsonify({"msg": "audio file required"}), 400
        
        audio_file = request.files["audio"]
        audio_data = audio_file.read()
        
        # 获取所有歌曲
        all_songs = Song.query.all()
        all_songs_data = [{
            "id": s.id,
            "title": s.title,
            "artist": s.artist,
            "file_path": s.file_path
        } for s in all_songs]
        
        from audio_recognition import recognize_from_recording
        result = recognize_from_recording(audio_data, all_songs_data)
        
        # 如果匹配成功，返回完整歌曲信息
        if result.get("matched") and result.get("song_id"):
            song = Song.query.get(result["song_id"])
            if song:
                base_url = request.host_url.strip("/")
                result["song"] = song_to_dict(song, base_url)
        
        return jsonify(result)

    # ========== 6. AI获取歌曲信息 API ==========
    @app.route("/api/ai/fetch-song-info", methods=["POST"])
    def ai_fetch_song_info():
        """AI联网搜索获取歌曲详细信息"""
        data = request.json
        title = data.get("title", "")
        artist = data.get("artist", "")
        
        if not title:
            return jsonify({"success": False, "error": "歌曲名称不能为空"}), 400
        
        result = fetch_song_info(title, artist)
        return jsonify(result)

    @app.route("/api/ai/songs/<int:song_id>/fetch-info", methods=["POST"])
    def ai_fetch_and_update_song_info(song_id):
        """AI获取歌曲信息并自动更新到数据库"""
        song = Song.query.get_or_404(song_id)
        
        result = fetch_song_info(song.title, song.artist)
        
        if result.get("success") and result.get("data"):
            info = result["data"]
            
            # 更新歌曲信息
            if info.get("album"):
                song.album = info["album"]
            if info.get("release_date"):
                song.release_date = info["release_date"]
            if info.get("lyrics"):
                song.lyrics = info["lyrics"]
            if info.get("genre") and not song.genre:
                song.genre = info["genre"]
            
            try:
                db.session.commit()
                base_url = request.host_url.strip("/")
                return jsonify({
                    "success": True,
                    "msg": "歌曲信息已更新",
                    "data": info,
                    "song": song_to_dict(song, base_url)
                })
            except Exception as e:
                db.session.rollback()
                return jsonify({"success": False, "error": f"保存失败: {str(e)}"}), 500
        
        return jsonify(result)

    # ========== 7. 排行榜 API ==========
    @app.route("/api/ai/ranking", methods=["GET"])
    def ai_ranking():
        """获取实时排行榜，包含排名变化"""
        from datetime import date, timedelta
        
        try:
            limit = int(request.args.get("limit", 20))
            base_url = request.host_url.strip("/")
            
            # 获取当前排行（按播放次数降序）
            songs = Song.query.order_by(Song.play_count.desc()).limit(limit).all()
            
            # 尝试获取RankHistory模型
            try:
                from app import RankHistory
                today = date.today()
                yesterday = today - timedelta(days=1)
        
                # 获取昨天的排名记录
                yesterday_ranks = {}
                yesterday_records = RankHistory.query.filter_by(record_date=yesterday).all()
                for record in yesterday_records:
                    yesterday_ranks[record.song_id] = record.rank
                
                # 构建排行榜数据
                ranking_data = []
                for idx, song in enumerate(songs):
                    current_rank = idx + 1
                    prev_rank = yesterday_ranks.get(song.id)
                    
                    rank_change = None
                    if prev_rank is not None:
                        rank_change = prev_rank - current_rank
                    
                    song_data = song_to_dict(song, base_url)
                    song_data["current_rank"] = current_rank
                    song_data["prev_rank"] = prev_rank
                    song_data["rank_change"] = rank_change
                    song_data["is_new"] = prev_rank is None
                    ranking_data.append(song_data)
                
                # 更新今天的排名记录
                for idx, song in enumerate(songs):
                    existing = RankHistory.query.filter_by(song_id=song.id, record_date=today).first()
                    if existing:
                        existing.rank = idx + 1
                        existing.play_count = song.play_count
                    else:
                        new_record = RankHistory(
                            song_id=song.id,
                            rank=idx + 1,
                            play_count=song.play_count,
                            record_date=today
                        )
                        db.session.add(new_record)
                
                try:
                    db.session.commit()
                except:
                    db.session.rollback()
                
                return jsonify({
                    "ranking": ranking_data,
                    "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
            except Exception as e:
                # RankHistory表不存在或其他错误，返回简化排行榜
                print(f"排行榜历史记录错误: {e}")
                ranking_data = []
                for idx, song in enumerate(songs):
                    song_data = song_to_dict(song, base_url)
                    song_data["current_rank"] = idx + 1
                    song_data["prev_rank"] = None
                    song_data["rank_change"] = None
                    song_data["is_new"] = True
                    ranking_data.append(song_data)
                
                return jsonify({
                    "ranking": ranking_data,
                    "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
        except Exception as e:
            print(f"排行榜API错误: {e}")
            return jsonify({"ranking": [], "updated_at": "", "error": str(e)}), 500

    return app
