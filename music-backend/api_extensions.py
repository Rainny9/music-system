# API 扩展 - 新增功能
from flask import request, jsonify
from datetime import datetime, timedelta
from sqlalchemy import func, desc


def register_extensions(app, db, Song, User, require_admin, Favorite, Playlist, PlaylistSong, PlayHistory, SongLike, SearchHistory, song_to_dict):
    """注册扩展API - 所有模型通过参数传入，避免循环导入"""

    # ========== 1. 歌曲点赞 API ==========
    @app.route("/api/songs/<int:song_id>/like", methods=["POST"])
    def toggle_like(song_id):
        """点赞/取消点赞"""
        data = request.json
        user_id = data.get("user_id")
        if not user_id:
            return jsonify({"msg": "user_id required"}), 400

        song = Song.query.get_or_404(song_id)
        like = SongLike.query.filter_by(song_id=song_id, user_id=user_id).first()

        if like:
            db.session.delete(like)
            song.like_count = max(0, (song.like_count or 0) - 1)
            db.session.commit()
            return jsonify({"msg": "unliked", "like_count": song.like_count})
        else:
            like = SongLike(song_id=song_id, user_id=user_id)
            db.session.add(like)
            song.like_count = (song.like_count or 0) + 1
            db.session.commit()
            return jsonify({"msg": "liked", "like_count": song.like_count})

    @app.route("/api/songs/<int:song_id>/play_count", methods=["POST"])
    def increment_play_count(song_id):
        """增加播放次数"""
        song = Song.query.get_or_404(song_id)
        song.play_count = (song.play_count or 0) + 1
        db.session.commit()
        return jsonify({"msg": "play count updated", "play_count": song.play_count})

    @app.route("/api/songs/ranking", methods=["GET"])
    def get_ranking():
        """获取排行榜"""
        base_url = request.host_url.strip("/")
        songs = Song.query.order_by(desc(Song.play_count)).limit(50).all()
        return jsonify([song_to_dict(s, base_url) for s in songs])

    # ========== 2. 歌单管理 API ==========
    @app.route("/api/playlists", methods=["GET"])
    def list_playlists():
        """获取歌单列表"""
        user_id = request.args.get("user_id")
        base_url = request.host_url.strip("/")

        if user_id:
            playlists = Playlist.query.filter_by(user_id=user_id).all()
        else:
            playlists = Playlist.query.filter_by(is_public=True).all()

        result = []
        for p in playlists:
            song_count = PlaylistSong.query.filter_by(playlist_id=p.id).count()
            result.append({
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "cover_url": f"{base_url}/api/playlists/{p.id}/cover" if p.cover_path else None,
                "user_id": p.user_id,
                "song_count": song_count,
                "is_public": p.is_public,
                "created_at": p.created_at.isoformat() if p.created_at else None
            })
        return jsonify(result)

    @app.route("/api/playlists", methods=["POST"])
    def create_playlist():
        """创建歌单"""
        data = request.json
        user_id = data.get("user_id")
        name = data.get("name")
        description = data.get("description", "")

        if not user_id or not name:
            return jsonify({"msg": "user_id and name required"}), 400

        # AI内容审核 - 审核歌单名称和描述
        from ai_service import content_moderation
        content_to_check = f"歌单名称：{name}"
        if description:
            content_to_check += f"\n歌单描述：{description}"
        
        moderation_result = content_moderation(content_to_check, "description")
        if not moderation_result.get("passed", True):
            return jsonify({
                "msg": "歌单内容审核未通过",
                "reason": moderation_result.get("reason", "内容包含违规信息"),
                "risk_level": moderation_result.get("risk_level", "medium")
            }), 400

        existing = Playlist.query.filter_by(user_id=user_id, name=name).first()
        if existing:
            return jsonify({"msg": "playlist name already exists"}), 400

        playlist = Playlist(
            user_id=user_id,
            name=name,
            description=description,
            is_public=data.get("is_public", True)
        )
        db.session.add(playlist)
        db.session.commit()
        return jsonify({"msg": "playlist created", "id": playlist.id})

    @app.route("/api/playlists/<int:playlist_id>", methods=["GET"])
    def get_playlist(playlist_id):
        """获取歌单详情"""
        playlist = Playlist.query.get_or_404(playlist_id)
        base_url = request.host_url.strip("/")

        playlist_songs = PlaylistSong.query.filter_by(playlist_id=playlist_id).all()
        song_ids = [ps.song_id for ps in playlist_songs]
        songs = Song.query.filter(Song.id.in_(song_ids)).all() if song_ids else []

        return jsonify({
            "id": playlist.id,
            "name": playlist.name,
            "description": playlist.description,
            "user_id": playlist.user_id,
            "songs": [song_to_dict(s, base_url) for s in songs],
            "created_at": playlist.created_at.isoformat() if playlist.created_at else None
        })

    @app.route("/api/playlists/<int:playlist_id>", methods=["PUT"])
    def update_playlist(playlist_id):
        """更新歌单"""
        playlist = Playlist.query.get_or_404(playlist_id)
        data = request.json
        
        name = data.get("name")
        description = data.get("description")
        
        # AI内容审核 - 审核歌单名称和描述
        if name or description:
            from ai_service import content_moderation
            content_to_check = ""
            if name:
                content_to_check += f"歌单名称：{name}\n"
            if description:
                content_to_check += f"歌单描述：{description}"
            
            if content_to_check.strip():
                moderation_result = content_moderation(content_to_check, "description")
                if not moderation_result.get("passed", True):
                    return jsonify({
                        "msg": "歌单内容审核未通过",
                        "reason": moderation_result.get("reason", "内容包含违规信息"),
                        "risk_level": moderation_result.get("risk_level", "medium")
                    }), 400

        if name:
            playlist.name = name
        if "description" in data:
            playlist.description = description
        if "is_public" in data:
            playlist.is_public = data.get("is_public")

        db.session.commit()
        return jsonify({"msg": "playlist updated"})

    @app.route("/api/playlists/<int:playlist_id>", methods=["DELETE"])
    def delete_playlist(playlist_id):
        """删除歌单"""
        playlist = Playlist.query.get_or_404(playlist_id)

        PlaylistSong.query.filter_by(playlist_id=playlist_id).delete()
        db.session.delete(playlist)
        db.session.commit()
        return jsonify({"msg": "playlist deleted"})

    @app.route("/api/playlists/<int:playlist_id>/songs", methods=["POST"])
    def add_song_to_playlist(playlist_id):
        """添加歌曲到歌单"""
        playlist = Playlist.query.get_or_404(playlist_id)
        data = request.json
        song_id = data.get("song_id")

        if not song_id:
            return jsonify({"msg": "song_id required"}), 400

        # 检查歌曲是否存在
        song = Song.query.get(song_id)
        if not song:
            return jsonify({"msg": "song not found"}), 404

        # 检查是否已在歌单中
        existing = PlaylistSong.query.filter_by(playlist_id=playlist_id, song_id=song_id).first()
        if existing:
            return jsonify({"msg": "song already in playlist"}), 400

        playlist_song = PlaylistSong(playlist_id=playlist_id, song_id=song_id)
        db.session.add(playlist_song)
        db.session.commit()
        return jsonify({"msg": "song added to playlist"})

    @app.route("/api/playlists/<int:playlist_id>/songs/<int:song_id>", methods=["DELETE"])
    def remove_song_from_playlist(playlist_id, song_id):
        """从歌单移除歌曲"""
        playlist_song = PlaylistSong.query.filter_by(playlist_id=playlist_id, song_id=song_id).first()
        if playlist_song:
            db.session.delete(playlist_song)
            db.session.commit()
        return jsonify({"msg": "song removed from playlist"})

    # ========== 3. 播放历史 API ==========
    @app.route("/api/users/<int:user_id>/history", methods=["GET"])
    def get_play_history(user_id):
        """获取播放历史"""
        base_url = request.host_url.strip("/")
        histories = PlayHistory.query.filter_by(user_id=user_id)\
            .order_by(desc(PlayHistory.played_at)).limit(100).all()

        result = []
        for h in histories:
            song = Song.query.get(h.song_id)
            if song:
                song_data = song_to_dict(song, base_url)
                song_data["history_id"] = h.id
                song_data["play_progress"] = h.play_progress
                song_data["played_at"] = h.played_at.isoformat() if h.played_at else None
                result.append(song_data)

        return jsonify(result)

    @app.route("/api/users/<int:user_id>/history", methods=["POST"])
    def add_play_history(user_id):
        """添加播放历史并更新播放次数"""
        data = request.json
        song_id = data.get("song_id")
        progress = data.get("progress", 0)

        if not song_id:
            return jsonify({"msg": "song_id required"}), 400

        # 查找歌曲
        song = Song.query.get(song_id)
        if not song:
            return jsonify({"msg": "song not found"}), 404

        history = PlayHistory.query.filter_by(user_id=user_id, song_id=song_id).first()

        if history:
            # 如果是同一首歌的重复播放（距离上次播放超过30秒才算新的播放）
            time_diff = (datetime.now() - history.played_at).total_seconds() if history.played_at else 9999
            if time_diff > 30:
                # 增加播放次数
                song.play_count = (song.play_count or 0) + 1
            history.play_progress = progress
            history.played_at = datetime.now()
        else:
            # 新的播放记录，增加播放次数
            song.play_count = (song.play_count or 0) + 1
            history = PlayHistory(user_id=user_id, song_id=song_id, play_progress=progress)
            history.played_at = datetime.now()
            db.session.add(history)

        db.session.commit()
        return jsonify({"msg": "history updated", "play_count": song.play_count})

    @app.route("/api/users/<int:user_id>/history/<int:history_id>", methods=["DELETE"])
    def delete_play_history(user_id, history_id):
        """删除播放历史"""
        history = PlayHistory.query.filter_by(id=history_id, user_id=user_id).first()
        if history:
            db.session.delete(history)
            db.session.commit()
        return jsonify({"msg": "history deleted"})

    @app.route("/api/users/<int:user_id>/history/clear", methods=["DELETE"])
    def clear_play_history(user_id):
        """清空播放历史"""
        PlayHistory.query.filter_by(user_id=user_id).delete()
        db.session.commit()
        return jsonify({"msg": "history cleared"})

    # ========== 4. 个人中心 API ==========
    @app.route("/api/users/<int:user_id>/stats", methods=["GET"])
    def get_user_stats(user_id):
        """获取用户统计信息"""
        user = User.query.get_or_404(user_id)

        favorite_count = Favorite.query.filter_by(user_id=user_id).count()
        playlist_count = Playlist.query.filter_by(user_id=user_id).count()

        total_play_time = 0
        week_play_count = 0

        histories = PlayHistory.query.filter_by(user_id=user_id).all()
        for h in histories:
            song = Song.query.get(h.song_id)
            if song and song.duration:
                total_play_time += song.duration

        week_ago = datetime.now() - timedelta(days=7)  # 使用本地时间
        week_play_count = PlayHistory.query.filter(
            PlayHistory.user_id == user_id,
            PlayHistory.played_at >= week_ago
        ).count()

        return jsonify({
            "user_id": user_id,
            "username": user.username,
            "favorite_count": favorite_count,
            "playlist_count": playlist_count,
            "total_play_time": total_play_time,
            "week_play_count": week_play_count,
            "created_at": user.created_at.isoformat() if user.created_at else None
        })

    @app.route("/api/users/<int:user_id>/profile", methods=["PUT"])
    def update_profile(user_id):
        """更新用户资料"""
        user = User.query.get_or_404(user_id)
        data = request.json

        if data.get("username"):
            existing = User.query.filter_by(username=data.get("username")).first()
            if existing and existing.id != user_id:
                return jsonify({"msg": "username already exists"}), 400
            user.username = data.get("username")

        if "gender" in data:
            user.gender = data.get("gender")
        if "birthday" in data:
            user.birthday = data.get("birthday")
        if "region" in data:
            user.region = data.get("region")

        db.session.commit()
        return jsonify({"msg": "profile updated"})

    @app.route("/api/users/<int:user_id>/password", methods=["PUT"])
    def change_password(user_id):
        """修改密码"""
        user = User.query.get_or_404(user_id)
        data = request.json

        old_password = data.get("old_password")
        new_password = data.get("new_password")

        if not old_password or not new_password:
            return jsonify({"msg": "old_password and new_password required"}), 400

        if user.password != old_password:
            return jsonify({"msg": "old password incorrect"}), 401

        user.password = new_password
        db.session.commit()
        return jsonify({"msg": "password changed"})

    return app
