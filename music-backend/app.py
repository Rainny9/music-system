import os
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from mutagen import File as MutagenFile

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*", "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"], "allow_headers": ["Content-Type", "Authorization"]}})

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:123456@127.0.0.1:3306/music_db?charset=utf8mb4"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# ========== 模型 ==========
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    avatar_path = db.Column(db.String(300), nullable=True)  # 头像路径
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    artist = db.Column(db.String(200))
    album = db.Column(db.String(200))
    duration = db.Column(db.Integer)
    genre = db.Column(db.String(100))
    tags = db.Column(db.String(200))
    lyrics = db.Column(db.Text)
    cover_path = db.Column(db.String(300))
    release_date = db.Column(db.String(20))
    file_path = db.Column(db.String(300), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    song_id = db.Column(db.Integer, db.ForeignKey("song.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    song_id = db.Column(db.Integer, db.ForeignKey("song.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Announcement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    expire_at = db.Column(db.DateTime, nullable=True)  # 过期时间，为空表示永不过期
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


def create_tables_and_seed():
    db.create_all()
    if Song.query.count() == 0:
        test_file = os.path.join(UPLOAD_FOLDER, "颜人中-嗜好.mp3")
        if os.path.exists(test_file):
            song = Song(title="嗜好", artist="颜人中", genre="流行", tags="中文,伤感", file_path=test_file)
            db.session.add(song)
            db.session.commit()
    if not User.query.filter_by(is_admin=True).first():
        admin = User(username="admin", password="admin123", is_admin=True)
        db.session.add(admin)
        db.session.commit()


def song_to_dict(song: Song, base_url: str):
    cover_url = None
    if song.cover_path and os.path.exists(song.cover_path):
        cover_url = f"{base_url}/api/songs/{song.id}/cover"
    return {
        "id": song.id,
        "title": song.title,
        "artist": song.artist,
        "album": song.album,
        "duration": song.duration,
        "genre": song.genre,
        "tags": song.tags,
        "lyrics": song.lyrics,
        "cover_url": cover_url,
        "release_date": song.release_date,
        "play_url": f"{base_url}/api/songs/{song.id}/play",
        "download_url": f"{base_url}/api/songs/{song.id}/download",
    }


def require_admin():
    admin_user_id = request.args.get("admin_user_id") or (
        request.json.get("admin_user_id") if request.is_json else None
    )
    if not admin_user_id:
        return jsonify({"msg": "admin_user_id required"}), 401
    admin = User.query.filter_by(id=int(admin_user_id), is_admin=True).first()
    if not admin:
        return jsonify({"msg": "admin privileges required"}), 403
    return None


@app.route("/api/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"msg": "username and password required"}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({"msg": "username already exists"}), 400
    user = User(username=username, password=password)
    db.session.add(user)
    db.session.commit()
    return jsonify({"msg": "register success", "user_id": user.id})


@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    user = User.query.filter_by(username=username, password=password).first()
    if not user:
        return jsonify({"msg": "invalid username or password"}), 401
    base_url = request.host_url.strip("/")
    avatar_url = f"{base_url}/api/users/{user.id}/avatar" if user.avatar_path and os.path.exists(user.avatar_path) else None
    return jsonify({
        "msg": "login success", 
        "user_id": user.id, 
        "is_admin": user.is_admin,
        "username": user.username,
        "avatar_url": avatar_url
    })


@app.route("/api/songs", methods=["GET"])
def list_songs():
    keyword = request.args.get("keyword", "").strip()
    genre = request.args.get("genre", "").strip()
    tag = request.args.get("tag", "").strip()
    query = Song.query
    if keyword:
        like = f"%{keyword}%"
        query = query.filter(db.or_(Song.title.like(like), Song.artist.like(like), Song.tags.like(like)))
    if genre:
        query = query.filter(Song.genre.like(f"%{genre}%"))
    if tag:
        query = query.filter(db.or_(Song.tags.like(f"%{tag}%"), Song.genre.like(f"%{tag}%")))
    songs = query.order_by(Song.created_at.desc()).all()
    base_url = request.host_url.strip("/")
    return jsonify([song_to_dict(s, base_url) for s in songs])


@app.route("/api/songs/<int:song_id>/play", methods=["GET"])
def play_song(song_id):
    song = Song.query.get_or_404(song_id)
    if not os.path.exists(song.file_path):
        return jsonify({"msg": "audio file not found"}), 404
    directory, filename = os.path.split(song.file_path)
    return send_from_directory(directory, filename)


@app.route("/api/songs/<int:song_id>", methods=["GET"])
def get_song_detail(song_id):
    song = Song.query.get_or_404(song_id)
    base_url = request.host_url.strip("/")
    data = song_to_dict(song, base_url)
    return jsonify(data)


@app.route("/api/songs/<int:song_id>/cover", methods=["GET"])
def get_song_cover(song_id):
    song = Song.query.get_or_404(song_id)
    if not song.cover_path or not os.path.exists(song.cover_path):
        return jsonify({"msg": "cover not found"}), 404
    directory, filename = os.path.split(song.cover_path)
    return send_from_directory(directory, filename)


@app.route("/api/admin/songs", methods=["GET"])
def admin_list_songs():
    auth_resp = require_admin()
    if auth_resp is not None:
        return auth_resp
    songs = Song.query.order_by(Song.created_at.desc()).all()
    base_url = request.host_url.strip("/")
    return jsonify([song_to_dict(s, base_url) for s in songs])


@app.route("/api/admin/songs/<int:song_id>", methods=["PUT"])
def admin_update_song(song_id):
    auth_resp = require_admin()
    if auth_resp is not None:
        return auth_resp
    song = Song.query.get_or_404(song_id)
    data = request.json or {}
    if data.get("title") is not None:
        song.title = data.get("title")
    if data.get("artist") is not None:
        song.artist = data.get("artist")
    if data.get("genre") is not None:
        song.genre = data.get("genre")
    if data.get("tags") is not None:
        song.tags = data.get("tags")
    if data.get("album") is not None:
        song.album = data.get("album")
    if data.get("lyrics") is not None:
        song.lyrics = data.get("lyrics")
    if data.get("release_date") is not None:
        song.release_date = data.get("release_date")
    db.session.commit()
    base_url = request.host_url.strip("/")
    return jsonify({"msg": "updated", "song": song_to_dict(song, base_url)})


@app.route("/api/admin/songs/<int:song_id>/cover", methods=["POST"])
def admin_upload_cover(song_id):
    auth_resp = require_admin()
    if auth_resp is not None:
        return auth_resp
    song = Song.query.get_or_404(song_id)
    file = request.files.get("cover")
    if not file:
        return jsonify({"msg": "cover file required"}), 400
    filename = f"cover_{song_id}_{file.filename}"
    save_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(save_path)
    song.cover_path = save_path
    db.session.commit()
    base_url = request.host_url.strip("/")
    return jsonify({"msg": "cover uploaded", "cover_url": f"{base_url}/api/songs/{song_id}/cover"})


@app.route("/api/admin/songs/<int:song_id>", methods=["DELETE"])
def admin_delete_song(song_id):
    auth_resp = require_admin()
    if auth_resp is not None:
        return auth_resp
    song = Song.query.get_or_404(song_id)
    try:
        Favorite.query.filter_by(song_id=song_id).delete()
        Comment.query.filter_by(song_id=song_id).delete()
        if song.file_path and os.path.exists(song.file_path):
            try:
                os.remove(song.file_path)
            except Exception as e:
                print("删除文件失败:", e)
        db.session.delete(song)
        db.session.commit()
        return jsonify({"msg": "deleted"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": f"删除失败: {str(e)}"}), 500


@app.route("/api/songs/<int:song_id>/download", methods=["GET"])
def download_song(song_id):
    song = Song.query.get_or_404(song_id)
    directory, filename = os.path.split(song.file_path)
    return send_from_directory(directory, filename, as_attachment=True)


@app.route("/api/songs/<int:song_id>/comments", methods=["GET"])
def list_comments(song_id):
    comments = Comment.query.filter_by(song_id=song_id).order_by(Comment.created_at.desc()).all()
    return jsonify([{"id": c.id, "song_id": c.song_id, "user_id": c.user_id, "content": c.content, "created_at": c.created_at.isoformat()} for c in comments])


@app.route("/api/songs/<int:song_id>/comments", methods=["POST"])
def add_comment(song_id):
    data = request.json
    user_id = data.get("user_id")
    content = data.get("content")
    if not user_id or not content:
        return jsonify({"msg": "user_id and content required"}), 400
    comment = Comment(song_id=song_id, user_id=user_id, content=content)
    db.session.add(comment)
    db.session.commit()
    return jsonify({"msg": "comment added"})


@app.route("/api/songs/<int:song_id>/favorite", methods=["POST"])
def toggle_favorite(song_id):
    data = request.json
    user_id = data.get("user_id")
    if not user_id:
        return jsonify({"msg": "user_id required"}), 400
    fav = Favorite.query.filter_by(song_id=song_id, user_id=user_id).first()
    if fav:
        db.session.delete(fav)
        db.session.commit()
        return jsonify({"msg": "unfavorited"})
    else:
        fav = Favorite(song_id=song_id, user_id=user_id)
        db.session.add(fav)
        db.session.commit()
        return jsonify({"msg": "favorited"})


@app.route("/api/users/<int:user_id>/favorites", methods=["GET"])
def list_favorites(user_id):
    base_url = request.host_url.strip("/")
    favs = Favorite.query.filter_by(user_id=user_id).all()
    song_ids = [f.song_id for f in favs]
    if not song_ids:
        return jsonify([])
    songs = Song.query.filter(Song.id.in_(song_ids)).all()
    return jsonify([song_to_dict(s, base_url) for s in songs])


@app.route("/api/genres", methods=["GET"])
def list_genres():
    genres = db.session.query(Song.genre).filter(Song.genre.isnot(None), Song.genre != "").distinct().all()
    return jsonify([g[0] for g in genres])


# ========== 用户头像 API ==========
@app.route("/api/users/<int:user_id>/avatar", methods=["GET"])
def get_user_avatar(user_id):
    """获取用户头像"""
    user = User.query.get_or_404(user_id)
    if not user.avatar_path or not os.path.exists(user.avatar_path):
        return jsonify({"msg": "avatar not found"}), 404
    directory, filename = os.path.split(user.avatar_path)
    return send_from_directory(directory, filename)


@app.route("/api/users/<int:user_id>/avatar", methods=["POST"])
def upload_user_avatar(user_id):
    """上传用户头像"""
    user = User.query.get_or_404(user_id)
    file = request.files.get("avatar")
    if not file:
        return jsonify({"msg": "avatar file required"}), 400
    # 保存头像
    filename = f"avatar_{user_id}_{file.filename}"
    save_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(save_path)
    user.avatar_path = save_path
    db.session.commit()
    base_url = request.host_url.strip("/")
    return jsonify({"msg": "avatar uploaded", "avatar_url": f"{base_url}/api/users/{user_id}/avatar"})


@app.route("/api/users/<int:user_id>/info", methods=["GET"])
def get_user_info(user_id):
    """获取用户信息"""
    user = User.query.get_or_404(user_id)
    base_url = request.host_url.strip("/")
    avatar_url = f"{base_url}/api/users/{user.id}/avatar" if user.avatar_path and os.path.exists(user.avatar_path) else None
    return jsonify({
        "id": user.id,
        "username": user.username,
        "is_admin": user.is_admin,
        "avatar_url": avatar_url,
        "created_at": user.created_at.isoformat() if user.created_at else None
    })


# ========== 用户管理 API ==========
@app.route("/api/admin/users", methods=["GET"])
def admin_list_users():
    auth_resp = require_admin()
    if auth_resp is not None:
        return auth_resp
    users = User.query.order_by(User.created_at.desc()).all()
    return jsonify([{
        "id": u.id,
        "username": u.username,
        "is_admin": u.is_admin,
        "created_at": u.created_at.isoformat() if u.created_at else None
    } for u in users])


@app.route("/api/admin/users", methods=["POST"])
def admin_create_user():
    auth_resp = require_admin()
    if auth_resp is not None:
        return auth_resp
    data = request.json
    username = data.get("username")
    password = data.get("password")
    is_admin = data.get("is_admin", False)
    if not username or not password:
        return jsonify({"msg": "username and password required"}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({"msg": "username already exists"}), 400
    user = User(username=username, password=password, is_admin=is_admin)
    db.session.add(user)
    db.session.commit()
    return jsonify({"msg": "user created", "user_id": user.id})


@app.route("/api/admin/users/<int:user_id>", methods=["PUT"])
def admin_update_user(user_id):
    auth_resp = require_admin()
    if auth_resp is not None:
        return auth_resp
    user = User.query.get_or_404(user_id)
    data = request.json or {}
    if data.get("username") is not None:
        existing = User.query.filter_by(username=data.get("username")).first()
        if existing and existing.id != user_id:
            return jsonify({"msg": "username already exists"}), 400
        user.username = data.get("username")
    if data.get("password") is not None and data.get("password").strip():
        user.password = data.get("password")
    if data.get("is_admin") is not None:
        user.is_admin = data.get("is_admin")
    db.session.commit()
    return jsonify({"msg": "user updated"})


@app.route("/api/admin/users/<int:user_id>", methods=["DELETE"])
def admin_delete_user(user_id):
    auth_resp = require_admin()
    if auth_resp is not None:
        return auth_resp
    user = User.query.get_or_404(user_id)
    # 不允许删除自己
    admin_user_id = request.args.get("admin_user_id") or (
        request.json.get("admin_user_id") if request.is_json else None
    )
    if str(user_id) == str(admin_user_id):
        return jsonify({"msg": "cannot delete yourself"}), 400
    try:
        # 删除用户相关的收藏和评论
        Favorite.query.filter_by(user_id=user_id).delete()
        Comment.query.filter_by(user_id=user_id).delete()
        db.session.delete(user)
        db.session.commit()
        return jsonify({"msg": "user deleted"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": f"删除失败: {str(e)}"}), 500


def get_audio_duration(file_path):
    try:
        audio = MutagenFile(file_path)
        if audio is not None and audio.info is not None:
            return int(audio.info.length)
    except Exception as e:
        print(f"获取音频时长失败: {e}")
    return None


# ========== 公告管理 API ==========
@app.route("/api/announcements", methods=["GET"])
def list_announcements():
    """获取所有启用且未过期的公告（前台展示）"""
    now = datetime.now()  # 使用本地时间
    # 过滤：is_active=True 且 (expire_at为空 或 expire_at > 当前时间)
    announcements = Announcement.query.filter(
        Announcement.is_active == True,
        db.or_(Announcement.expire_at.is_(None), Announcement.expire_at > now)
    ).order_by(Announcement.created_at.desc()).all()
    return jsonify([{
        "id": a.id,
        "title": a.title,
        "content": a.content,
        "created_at": a.created_at.isoformat() if a.created_at else None,
        "expire_at": a.expire_at.isoformat() if a.expire_at else None
    } for a in announcements])


@app.route("/api/admin/announcements", methods=["GET"])
def admin_list_announcements():
    """获取所有公告（后台管理）"""
    auth_resp = require_admin()
    if auth_resp is not None:
        return auth_resp
    now = datetime.now()  # 使用本地时间
    announcements = Announcement.query.order_by(Announcement.created_at.desc()).all()
    result = []
    for a in announcements:
        is_expired = a.expire_at and a.expire_at <= now
        result.append({
            "id": a.id,
            "title": a.title,
            "content": a.content,
            "is_active": a.is_active,
            "expire_at": a.expire_at.isoformat() if a.expire_at else None,
            "is_expired": is_expired,
            "created_at": a.created_at.isoformat() if a.created_at else None,
            "updated_at": a.updated_at.isoformat() if a.updated_at else None
        })
    return jsonify(result)


@app.route("/api/admin/announcements", methods=["POST"])
def admin_create_announcement():
    """创建公告"""
    auth_resp = require_admin()
    if auth_resp is not None:
        return auth_resp
    data = request.json
    title = data.get("title")
    content = data.get("content")
    is_active = data.get("is_active", True)
    expire_at = None
    if data.get("expire_at"):
        try:
            expire_at = datetime.fromisoformat(data.get("expire_at").replace('Z', '+00:00').replace('+00:00', ''))
        except:
            pass
    if not title or not content:
        return jsonify({"msg": "title and content required"}), 400
    announcement = Announcement(title=title, content=content, is_active=is_active, expire_at=expire_at)
    db.session.add(announcement)
    db.session.commit()
    return jsonify({"msg": "announcement created", "id": announcement.id})


@app.route("/api/admin/announcements/<int:ann_id>", methods=["PUT"])
def admin_update_announcement(ann_id):
    """更新公告"""
    auth_resp = require_admin()
    if auth_resp is not None:
        return auth_resp
    announcement = Announcement.query.get_or_404(ann_id)
    data = request.json or {}
    if data.get("title") is not None:
        announcement.title = data.get("title")
    if data.get("content") is not None:
        announcement.content = data.get("content")
    if data.get("is_active") is not None:
        announcement.is_active = data.get("is_active")
    if "expire_at" in data:
        if data.get("expire_at"):
            try:
                announcement.expire_at = datetime.fromisoformat(data.get("expire_at").replace('Z', '+00:00').replace('+00:00', ''))
            except:
                pass
        else:
            announcement.expire_at = None
    db.session.commit()
    return jsonify({"msg": "announcement updated"})


@app.route("/api/admin/announcements/<int:ann_id>", methods=["DELETE"])
def admin_delete_announcement(ann_id):
    """删除公告"""
    auth_resp = require_admin()
    if auth_resp is not None:
        return auth_resp
    announcement = Announcement.query.get_or_404(ann_id)
    db.session.delete(announcement)
    db.session.commit()
    return jsonify({"msg": "announcement deleted"})


@app.route("/api/songs", methods=["POST"])
def upload_song():
    title = request.form.get("title")
    artist = request.form.get("artist")
    album = request.form.get("album")
    genre = request.form.get("genre")
    tags = request.form.get("tags")
    file = request.files.get("file")
    if not file or not title:
        return jsonify({"msg": "title and file required"}), 400
    filename = file.filename
    save_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(save_path)
    duration = get_audio_duration(save_path)
    song = Song(title=title, artist=artist, album=album, duration=duration, genre=genre, tags=tags, file_path=save_path)
    db.session.add(song)
    db.session.commit()
    base_url = request.host_url.strip("/")
    return jsonify({"msg": "upload success", "song": song_to_dict(song, base_url)})


if __name__ == "__main__":
    with app.app_context():
        create_tables_and_seed()
    app.run(host="0.0.0.0", port=5000, debug=True)
