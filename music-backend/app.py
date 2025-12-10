import os
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, "music.db")
# MySQL 连接示例，TODO: 按实际账号密码修改
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:123456@127.0.0.1:3306/music_db?charset=utf8mb4"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# ========== 模型 ==========
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)  # TODO: 这里以后改为密码哈希
    is_admin = db.Column(db.Boolean, default=False)  # 是否管理员
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    artist = db.Column(db.String(200))
    # TODO: 如果你后面想扩展专辑，可以加 album 字段
    genre = db.Column(db.String(100))  # 歌曲分类/风格，如 “流行”“摇滚”
    tags = db.Column(db.String(200))   # 标签字符串，如 "伤感,经典"
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

def create_tables_and_seed():
    """第一次启动时创建表并插入一条测试歌曲"""
    db.create_all()

    # 如果还没有任何歌曲，就插入一条测试数据
    if Song.query.count() == 0:
        # TODO: 如果你改了测试歌曲文件名，请同步修改下面的 test_song.mp3
        test_file = os.path.join(UPLOAD_FOLDER, "颜人中-嗜好.mp3")
        if os.path.exists(test_file):
            print("种子歌曲路径：",test_file) #调试用
            song = Song(
                title="嗜好",           # TODO: 你可以换成你喜欢的歌名
                artist="颜人中",         # TODO: 你可以换成真实歌手名
                genre="流行",              #TODO: 这里是分类/风格
                tags="中文,伤感",            
                file_path=test_file,
            )
            db.session.add(song)
            db.session.commit()
        else:
            print("请在 uploads 目录下放一首名为 颜人中-嗜好.mp3 的测试歌曲")

       # 如果没有管理员用户，则创建一个默认管理员
    if not User.query.filter_by(is_admin=True).first():
        admin = User(
            username="admin",   # TODO: 上线前请修改为你自己的管理员账号
            password="admin123",  # TODO: 上线前请修改为更安全的密码，并使用哈希
            is_admin=True,
        )
        db.session.add(admin)
        db.session.commit()
        print("已创建默认管理员账号：用户名 admin / 密码 admin123")



# ========== 工具函数 ==========
def song_to_dict(song: Song, base_url: str):
    return {
        "id": song.id,
        "title": song.title,
        "artist": song.artist,
        "play_url": f"{base_url}/api/songs/{song.id}/play",
        "download_url": f"{base_url}/api/songs/{song.id}/download",  # TODO: 前端用来做下载按钮
    }


#检查管理员身份
def require_admin():
    """从请求参数中读取 admin_user_id 并校验是否管理员。失败时直接返回响应。"""
    admin_user_id = request.args.get("admin_user_id") or (
        request.json.get("admin_user_id") if request.is_json else None
    )
    if not admin_user_id:
        return jsonify({"msg": "admin_user_id required"}), 401

    admin = User.query.filter_by(id=int(admin_user_id), is_admin=True).first()
    if not admin:
        return jsonify({"msg": "admin privileges required"}), 403

    return None  # 表示通过校验


# ========== 用户接口（注册 + 登录） ==========
@app.route("/api/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"msg": "username and password required"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"msg": "username already exists"}), 400

    user = User(username=username, password=password)  # TODO: 以后改为密码哈希
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

    # TODO: 实际项目请返回 JWT 或 Session，这里为简单只返回 user_id 和 is_admin
    return jsonify(
        {
            "msg": "login success",
            "user_id": user.id,
            "is_admin": user.is_admin,
        }
    )


# ========== 歌曲接口（列表 + 播放） ==========
@app.route("/api/songs", methods=["GET"])
def list_songs():
    """获取歌曲列表，支持关键字搜索与分类/标签筛选"""
    keyword = request.args.get("keyword", "").strip()
    genre = request.args.get("genre", "").strip()
    tag = request.args.get("tag", "").strip()

    query = Song.query

    if keyword:
        like = f"%{keyword}%"
        # 按歌名 / 歌手 / 标签模糊搜索
        query = query.filter(
            db.or_(
                Song.title.like(like),
                Song.artist.like(like),
                Song.tags.like(like),
            )
        )

    if genre:
        query = query.filter(Song.genre == genre)

    if tag:
        # 简单包含匹配：只要 tags 字符串中出现这个词
        like_tag = f"%{tag}%"
        query = query.filter(Song.tags.like(like_tag))

    songs = query.order_by(Song.created_at.desc()).all()
    base_url = request.host_url.strip("/")
    return jsonify([song_to_dict(s, base_url) for s in songs])


@app.route("/api/songs/<int:song_id>/play", methods=["GET"])
def play_song(song_id):
    """为前端 audio 提供播放链接"""
    song = Song.query.get_or_404(song_id)
    print("播放歌曲 ID:", song_id)
    print("数据库中的 file_path:", song.file_path)

    if not os.path.exists(song.file_path):
        print("文件不存在:", song.file_path)
        return jsonify({"msg": "audio file not found"}), 404

    directory, filename = os.path.split(song.file_path)
    print("send_from_directory:", directory, filename)
    return send_from_directory(directory, filename)


# ========== 管理员歌曲管理接口 ==========
@app.route("/api/admin/songs", methods=["GET"])
def admin_list_songs():
    """管理员查看所有歌曲列表"""
    auth_resp = require_admin()
    if auth_resp is not None:
        return auth_resp

    songs = Song.query.order_by(Song.created_at.desc()).all()
    base_url = request.host_url.strip("/")
    return jsonify([song_to_dict(s, base_url) for s in songs])


#管理员更新歌曲信息
@app.route("/api/admin/songs/<int:song_id>", methods=["PUT"])
def admin_update_song(song_id):
    """管理员更新歌曲基本信息（标题、歌手、分类、标签）"""
    auth_resp = require_admin()
    if auth_resp is not None:
        return auth_resp

    song = Song.query.get_or_404(song_id)
    data = request.json or {}

    # TODO: 你可以根据需要增加/减少可编辑字段
    title = data.get("title")
    artist = data.get("artist")
    genre = data.get("genre")
    tags = data.get("tags")

    if title is not None:
        song.title = title
    if artist is not None:
        song.artist = artist
    if genre is not None:
        song.genre = genre
    if tags is not None:
        song.tags = tags

    db.session.commit()

    base_url = request.host_url.strip("/")
    return jsonify({"msg": "updated", "song": song_to_dict(song, base_url)})


#管理员删除歌曲
@app.route("/api/admin/songs/<int:song_id>", methods=["DELETE"])
def admin_delete_song(song_id):
    """管理员删除歌曲（数据库记录 + 可选删除文件）"""
    auth_resp = require_admin()
    if auth_resp is not None:
        return auth_resp

    song = Song.query.get_or_404(song_id)

    # TODO: 如需同时删除磁盘上的文件，取消下面 if 块注释
    if os.path.exists(song.file_path):
        try:
            os.remove(song.file_path)
        except Exception as e:
            print("删除文件失败:", e)

    db.session.delete(song)
    db.session.commit()
    return jsonify({"msg": "deleted"})


# ========== 歌曲下载接口 ==========
@app.route("/api/songs/<int:song_id>/download", methods=["GET"])
def download_song(song_id):
    """下载歌曲文件"""
    song = Song.query.get_or_404(song_id)
    directory, filename = os.path.split(song.file_path)
    # TODO: 你可以自定义下载时展示的文件名
    return send_from_directory(directory, filename, as_attachment=True)


# ========== 评论接口 ==========
@app.route("/api/songs/<int:song_id>/comments", methods=["GET"])
def list_comments(song_id):
    comments = (
        Comment.query.filter_by(song_id=song_id)
        .order_by(Comment.created_at.desc())
        .all()
    )
    return jsonify(
        [
            {
                "id": c.id,
                "song_id": c.song_id,
                "user_id": c.user_id,
                "content": c.content,
                "created_at": c.created_at.isoformat(),
            }
            for c in comments
        ]
    )


@app.route("/api/songs/<int:song_id>/comments", methods=["POST"])
def add_comment(song_id):
    data = request.json
    user_id = data.get("user_id")  # TODO: 以后从 token/Session 中获取
    content = data.get("content")

    if not user_id or not content:
        return jsonify({"msg": "user_id and content required"}), 400

    comment = Comment(song_id=song_id, user_id=user_id, content=content)
    db.session.add(comment)
    db.session.commit()
    return jsonify({"msg": "comment added"})


# ========== 收藏接口 ==========
@app.route("/api/songs/<int:song_id>/favorite", methods=["POST"])
def toggle_favorite(song_id):
    data = request.json
    user_id = data.get("user_id")  # TODO: 以后从登录态中取
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


# ========== 为前端提供下拉框接口（列出所有分类） ==========
@app.route("/api/genres", methods=["GET"])
def list_genres():
    """返回所有非空的歌曲分类列表（去重）"""
    genres = (
        db.session.query(Song.genre)
        .filter(Song.genre.isnot(None), Song.genre != "")
        .distinct()
        .all()
    )
    # [('流行',), ('摇滚',)] -> ['流行','摇滚']
    genre_list = [g[0] for g in genres]
    return jsonify(genre_list)


# ========== 歌曲上传接口 ==========
@app.route("/api/songs", methods=["POST"])
def upload_song():
    """上传歌曲（前端用 form-data 提交）"""
    title = request.form.get("title")
    artist = request.form.get("artist")
    genre = request.form.get("genre")  # TODO: 前端可以用下拉选择
    tags = request.form.get("tags")    # TODO: 前端输入逗号分隔标签
    upload_user_id = request.form.get("upload_user_id")  # TODO: 以后从登录态中取

    file = request.files.get("file")
    if not file or not title:
        return jsonify({"msg": "title and file required"}), 400

    # TODO: 你可以在这里自定义保存文件名（用时间戳/UUID）
    filename = file.filename
    save_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(save_path)

    song = Song(
        title=title,
        artist=artist,
        genre=genre,
        tags=tags,
        file_path=save_path,
    )
    db.session.add(song)
    db.session.commit()

    base_url = request.host_url.strip("/")
    return jsonify({"msg": "upload success", "song": song_to_dict(song, base_url)})


if __name__ == "__main__":
    # 先创建表并插入测试数据
    with app.app_context():
        create_tables_and_seed()

    # TODO: 部署上线时改为 debug=False
    app.run(host="0.0.0.0", port=5000, debug=True)