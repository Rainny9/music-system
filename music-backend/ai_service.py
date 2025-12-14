# AI服务模块 - 通义千问集成
import os
import json
import requests
from typing import List, Dict, Optional

# 通义千问API配置
DASHSCOPE_API_KEY = "sk-9fc8f687db3c4bf58774e279c5455196"
DASHSCOPE_API_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"


def call_qwen_api(prompt: str, system_prompt: str = None) -> str:
    """调用通义千问API"""
    headers = {
        "Authorization": f"Bearer {DASHSCOPE_API_KEY}",
        "Content-Type": "application/json"
    }
    
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    payload = {
        "model": "qwen-turbo",
        "input": {
            "messages": messages
        },
        "parameters": {
            "result_format": "message",
            "temperature": 0.7,
            "max_tokens": 1500
        }
    }
    
    try:
        response = requests.post(DASHSCOPE_API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        
        if "output" in result and "choices" in result["output"]:
            return result["output"]["choices"][0]["message"]["content"]
        return ""
    except Exception as e:
        print(f"通义千问API调用失败: {e}")
        return ""


def get_personalized_recommendations(user_history: List[Dict], all_songs: List[Dict], limit: int = 10) -> List[int]:
    """
    智能推荐 - 基于用户历史生成个性化推荐
    返回推荐的歌曲ID列表
    """
    if not user_history:
        # 无历史记录，返回热门歌曲
        return []
    
    # 构建用户画像
    history_info = []
    for h in user_history[:20]:  # 最近20首
        history_info.append(f"- {h.get('title', '')} - {h.get('artist', '')} ({h.get('genre', '')})")
    
    # 构建可推荐歌曲列表
    songs_info = []
    for s in all_songs[:50]:  # 限制数量
        songs_info.append(f"ID:{s['id']} 《{s.get('title', '')}》- {s.get('artist', '')} 风格:{s.get('genre', '')} 标签:{s.get('tags', '')}")
    
    system_prompt = """你是一个专业的音乐推荐系统。根据用户的听歌历史，分析用户的音乐偏好，从候选歌曲中推荐最适合的歌曲。
只返回推荐歌曲的ID，用逗号分隔，不要有其他内容。例如: 1,5,8,12,15"""
    
    prompt = f"""用户最近听过的歌曲:
{chr(10).join(history_info)}

候选歌曲列表:
{chr(10).join(songs_info)}

请根据用户偏好，从候选歌曲中选择最适合推荐的{limit}首歌曲，只返回歌曲ID，用逗号分隔:"""
    
    result = call_qwen_api(prompt, system_prompt)
    
    try:
        # 解析返回的ID列表
        ids = [int(x.strip()) for x in result.split(",") if x.strip().isdigit()]
        return ids[:limit]
    except:
        return []


def auto_generate_tags(title: str, artist: str, lyrics: str = None, genre: str = None) -> Dict:
    """
    自动打标签 - 为歌曲生成标签和分类
    """
    system_prompt = """你是一个专业的音乐分类专家。根据歌曲信息生成合适的标签和分类。
返回JSON格式，包含:
- genre: 音乐风格(如:流行、摇滚、民谣、电子、古风、说唱等)
- tags: 标签数组(如:伤感、励志、甜蜜、怀旧、治愈等，最多5个)
- mood: 情绪(如:欢快、忧伤、平静、激昂等)
只返回JSON，不要其他内容。"""
    
    lyrics_part = f"\n歌词片段: {lyrics[:500]}..." if lyrics else ""
    genre_part = f"\n当前风格: {genre}" if genre else ""
    
    prompt = f"""请为以下歌曲生成标签:
歌曲名: {title}
歌手: {artist}{genre_part}{lyrics_part}

返回JSON格式的标签信息:"""
    
    result = call_qwen_api(prompt, system_prompt)
    
    try:
        # 尝试解析JSON
        result = result.strip()
        if result.startswith("```"):
            result = result.split("```")[1]
            if result.startswith("json"):
                result = result[4:]
        return json.loads(result)
    except:
        return {"genre": genre or "流行", "tags": [], "mood": "未知"}


def content_moderation(content: str, content_type: str = "comment") -> Dict:
    """
    内容审核 - 审核评论/歌词/描述的合规性
    content_type: comment(评论), lyrics(歌词), description(描述)
    """
    type_names = {
        "comment": "用户评论",
        "lyrics": "歌词内容",
        "description": "歌单描述"
    }
    
    system_prompt = """你是一个内容审核专家。检查内容是否包含以下违规信息:
1. 色情、低俗内容
2. 暴力、血腥内容
3. 政治敏感内容
4. 广告、垃圾信息
5. 侮辱、歧视性言论
6. 其他违法违规内容

返回JSON格式:
- passed: 是否通过审核(true/false)
- reason: 如果不通过，说明原因
- risk_level: 风险等级(low/medium/high)
只返回JSON，不要其他内容。"""
    
    prompt = f"""请审核以下{type_names.get(content_type, '内容')}:

"{content}"

返回审核结果JSON:"""
    
    result = call_qwen_api(prompt, system_prompt)
    
    try:
        result = result.strip()
        if result.startswith("```"):
            result = result.split("```")[1]
            if result.startswith("json"):
                result = result[4:]
        return json.loads(result)
    except:
        return {"passed": True, "reason": "", "risk_level": "low"}


def generate_playlist_recommendations(user_favorites: List[Dict], user_history: List[Dict]) -> Dict:
    """
    智能歌单推荐 - 根据用户喜好生成推荐歌单主题
    """
    system_prompt = """你是一个音乐策划专家。根据用户的音乐偏好，推荐适合的歌单主题。
返回JSON格式:
- themes: 推荐的歌单主题数组(3-5个)，每个包含name(名称)和description(描述)
只返回JSON，不要其他内容。"""
    
    fav_info = [f"{s.get('title', '')} - {s.get('artist', '')}" for s in user_favorites[:10]]
    history_info = [f"{s.get('title', '')} - {s.get('artist', '')}" for s in user_history[:10]]
    
    prompt = f"""用户收藏的歌曲:
{chr(10).join(fav_info) if fav_info else '暂无收藏'}

用户最近听过:
{chr(10).join(history_info) if history_info else '暂无历史'}

请推荐适合该用户的歌单主题:"""
    
    result = call_qwen_api(prompt, system_prompt)
    
    try:
        result = result.strip()
        if result.startswith("```"):
            result = result.split("```")[1]
            if result.startswith("json"):
                result = result[4:]
        return json.loads(result)
    except:
        return {"themes": [{"name": "每日推荐", "description": "根据你的喜好精选"}]}


def fetch_song_info(title: str, artist: str = None) -> Dict:
    """
    联网搜索歌曲信息 - 使用通义千问联网搜索获取歌曲详细信息
    返回: 专辑、发行时间、歌词等信息
    """
    headers = {
        "Authorization": f"Bearer {DASHSCOPE_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # 构建精确的搜索查询
    if artist:
        search_query = f"{artist} - {title}"
        search_desc = f"歌手「{artist}」演唱的歌曲《{title}》"
    else:
        search_query = title
        search_desc = f"歌曲《{title}》"
    
    messages = [
        {
            "role": "system", 
            "content": """你是一个专业的华语音乐数据库助手，拥有丰富的歌曲信息知识。
请严格按照用户提供的歌曲名和歌手名精确匹配，返回该歌曲的真实信息。

重要提示：
1. 必须精确匹配歌曲名和歌手名，不要混淆同名歌曲
2. 歌词必须是该歌手演唱版本的原版歌词，不要编造或混淆其他歌曲的歌词
3. 如果不确定某首歌的信息，对应字段填null，不要猜测

返回严格的JSON格式:
{
  "album": "专辑名称",
  "release_date": "YYYY-MM-DD格式的发行日期",
  "lyrics": "完整歌词，每行用\\n分隔",
  "genre": "音乐风格",
  "language": "语种"
}

只返回JSON，不要任何其他文字说明。"""
        },
        {
            "role": "user",
            "content": f"""请查询{search_desc}的详细信息。

搜索关键词：{search_query}

请返回这首歌的：
1. 所属专辑名称
2. 发行日期
3. 完整原版歌词（必须是{artist if artist else '原唱'}的版本）
4. 音乐风格
5. 语种

注意：歌词必须准确，是这首歌的真实歌词，不要编造。"""
        }
    ]
    
    payload = {
        "model": "qwen-max",
        "input": {
            "messages": messages
        },
        "parameters": {
            "result_format": "message",
            "temperature": 0.1,
            "max_tokens": 4000
        }
    }
    
    try:
        response = requests.post(DASHSCOPE_API_URL, headers=headers, json=payload, timeout=90)
        response.raise_for_status()
        result = response.json()
        
        if "output" in result and "choices" in result["output"]:
            content = result["output"]["choices"][0]["message"]["content"]
            
            # 解析JSON
            content = content.strip()
            # 处理markdown代码块
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            content = content.strip()
            
            try:
                info = json.loads(content)
                return {
                    "success": True,
                    "data": info
                }
            except json.JSONDecodeError as e:
                return {
                    "success": False,
                    "error": f"解析返回数据失败: {str(e)}",
                    "raw": content
                }
        
        return {"success": False, "error": "API返回格式错误"}
    except requests.exceptions.Timeout:
        return {"success": False, "error": "请求超时，请稍后重试"}
    except Exception as e:
        print(f"获取歌曲信息失败: {e}")
        return {"success": False, "error": str(e)}


def smart_sort_songs(songs: List[Dict], user_history: List[Dict], user_favorites: List[int] = None) -> List[int]:
    """
    智能排序 - 根据用户播放历史和偏好对歌曲进行智能排序
    返回排序后的歌曲ID列表
    """
    if not songs:
        return []
    
    # 如果没有用户历史，按播放次数排序
    if not user_history:
        sorted_songs = sorted(songs, key=lambda x: x.get('play_count', 0), reverse=True)
        return [s['id'] for s in sorted_songs]
    
    # 分析用户偏好
    genre_count = {}
    artist_count = {}
    for h in user_history[:30]:
        genre = h.get('genre', '')
        artist = h.get('artist', '')
        if genre:
            for g in genre.split(','):
                g = g.strip()
                if g:
                    genre_count[g] = genre_count.get(g, 0) + 1
        if artist:
            artist_count[artist] = artist_count.get(artist, 0) + 1
    
    # 计算每首歌的推荐分数
    def calc_score(song):
        score = 0
        # 播放次数基础分
        score += (song.get('play_count', 0) or 0) * 0.5
        
        # 用户偏好的流派加分
        song_genre = song.get('genre', '') or ''
        song_tags = song.get('tags', '') or ''
        all_tags = f"{song_genre},{song_tags}"
        for tag in all_tags.split(','):
            tag = tag.strip()
            if tag in genre_count:
                score += genre_count[tag] * 10
        
        # 用户喜欢的歌手加分
        song_artist = song.get('artist', '')
        if song_artist in artist_count:
            score += artist_count[song_artist] * 15
        
        # 收藏的歌曲加分
        if user_favorites and song.get('id') in user_favorites:
            score += 20
        
        return score
    
    # 按分数排序
    scored_songs = [(s, calc_score(s)) for s in songs]
    scored_songs.sort(key=lambda x: x[1], reverse=True)
    
    return [s[0]['id'] for s in scored_songs]
