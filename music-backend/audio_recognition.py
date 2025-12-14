# 听歌识曲服务 - 基于音频指纹匹配
import os
import hashlib
import json
import tempfile
from typing import Optional, Dict, List

# 尝试导入音频处理库
try:
    from pydub import AudioSegment
    import numpy as np
    AUDIO_LIBS_AVAILABLE = True
except ImportError:
    AUDIO_LIBS_AVAILABLE = False
    print("警告: pydub/numpy未安装，听歌识曲功能将使用简化模式")


def extract_audio_features(audio_path: str) -> Optional[Dict]:
    """提取音频特征用于匹配"""
    if not os.path.exists(audio_path):
        return None
    
    features = {
        "file_hash": "",
        "duration": 0,
        "sample_rate": 0,
        "channels": 0,
        "loudness": 0
    }
    
    with open(audio_path, "rb") as f:
        features["file_hash"] = hashlib.md5(f.read()).hexdigest()
    
    if AUDIO_LIBS_AVAILABLE:
        try:
            audio = AudioSegment.from_file(audio_path)
            features["duration"] = len(audio) / 1000
            features["sample_rate"] = audio.frame_rate
            features["channels"] = audio.channels
            features["loudness"] = audio.dBFS
        except Exception as e:
            print(f"音频分析失败: {e}")
    
    return features


def extract_audio_fingerprint(audio_path: str) -> Optional[List]:
    """提取音频指纹 - 简化版本，基于音频的频谱特征"""
    if not AUDIO_LIBS_AVAILABLE:
        return None
    
    try:
        audio = AudioSegment.from_file(audio_path)
        audio = audio.set_channels(1)
        samples = np.array(audio.get_array_of_samples())
        
        chunk_size = len(samples) // 10
        if chunk_size == 0:
            return None
        
        fingerprint = []
        for i in range(10):
            start = i * chunk_size
            end = start + chunk_size
            chunk = samples[start:end]
            energy = np.sqrt(np.mean(chunk.astype(float) ** 2))
            fingerprint.append(float(energy))
        
        return fingerprint
    except Exception as e:
        print(f"指纹提取失败: {e}")
        return None


def compare_fingerprints(fp1: List, fp2: List) -> float:
    """比较两个音频指纹的相似度，返回0-1之间的相似度分数"""
    if not fp1 or not fp2 or len(fp1) != len(fp2):
        return 0.0
    
    try:
        fp1 = np.array(fp1)
        fp2 = np.array(fp2)
        
        if np.max(fp1) > 0:
            fp1 = fp1 / np.max(fp1)
        if np.max(fp2) > 0:
            fp2 = fp2 / np.max(fp2)
        
        dot_product = np.dot(fp1, fp2)
        norm1 = np.linalg.norm(fp1)
        norm2 = np.linalg.norm(fp2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = dot_product / (norm1 * norm2)
        return float(similarity)
    except:
        return 0.0


def match_audio_simple(uploaded_features: Dict, song_features_list: List[Dict]) -> Optional[Dict]:
    """简化的音频匹配 - 基于时长和响度相似度"""
    if not uploaded_features or not song_features_list:
        return None
    
    uploaded_duration = uploaded_features.get("duration", 0)
    uploaded_loudness = uploaded_features.get("loudness", -100)
    
    if uploaded_duration == 0:
        return None
    
    best_match = None
    best_score = 0
    
    for song in song_features_list:
        song_duration = song.get("duration", 0)
        song_loudness = song.get("loudness", -100)
        
        if song_duration == 0:
            continue
        
        duration_diff = abs(uploaded_duration - song_duration)
        duration_score = max(0, 1 - (duration_diff / max(uploaded_duration, song_duration)))
        
        loudness_diff = abs(uploaded_loudness - song_loudness)
        loudness_score = max(0, 1 - (loudness_diff / 60))
        
        score = duration_score * 0.3 + loudness_score * 0.7
        
        if score > best_score:
            best_score = score
            best_match = song
    
    if best_match and best_score > 0.3:
        return {
            "matched": True,
            "song_id": best_match.get("id"),
            "title": best_match.get("title"),
            "artist": best_match.get("artist"),
            "confidence": round(best_score * 100, 1)
        }
    
    return {"matched": False, "message": "未找到匹配的歌曲"}


def recognize_from_recording(audio_data: bytes, all_songs: List[Dict]) -> Dict:
    """从录音识别歌曲，支持webm、wav、mp3等格式"""
    temp_path = None
    converted_path = None
    
    try:
        with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as f:
            f.write(audio_data)
            temp_path = f.name
        
        if AUDIO_LIBS_AVAILABLE:
            try:
                audio = AudioSegment.from_file(temp_path)
                converted_path = temp_path.replace(".webm", ".wav")
                audio.export(converted_path, format="wav")
                process_path = converted_path
            except Exception as e:
                print(f"音频转换失败: {e}")
                # 如果是ffmpeg相关错误，给出提示
                if "ffmpeg" in str(e).lower() or "ffprobe" in str(e).lower():
                    return {"matched": False, "message": "服务器未安装ffmpeg，无法处理录音。请使用描述识别功能。"}
                process_path = temp_path
        else:
            process_path = temp_path
        
        uploaded_features = extract_audio_features(process_path)
        uploaded_fingerprint = extract_audio_fingerprint(process_path) if AUDIO_LIBS_AVAILABLE else None
        
        if not uploaded_features:
            return {"matched": False, "message": "无法分析上传的音频"}
        
        song_features = []
        for song in all_songs:
            file_path = song.get("file_path")
            if file_path and os.path.exists(file_path):
                features = extract_audio_features(file_path)
                if features:
                    features["id"] = song["id"]
                    features["title"] = song.get("title", "")
                    features["artist"] = song.get("artist", "")
                    if uploaded_fingerprint:
                        features["fingerprint"] = extract_audio_fingerprint(file_path)
                    song_features.append(features)
        
        if not song_features:
            return {"matched": False, "message": "曲库中没有可匹配的歌曲"}
        
        if uploaded_fingerprint:
            best_match = None
            best_score = 0
            for song in song_features:
                if song.get("fingerprint"):
                    score = compare_fingerprints(uploaded_fingerprint, song["fingerprint"])
                    if score > best_score:
                        best_score = score
                        best_match = song
            
            if best_match and best_score > 0.5:
                return {
                    "matched": True,
                    "song_id": best_match["id"],
                    "title": best_match["title"],
                    "artist": best_match["artist"],
                    "confidence": round(best_score * 100, 1)
                }
        
        result = match_audio_simple(uploaded_features, song_features)
        return result or {"matched": False, "message": "未找到匹配的歌曲，请尝试描述识别"}
        
    except Exception as e:
        print(f"识别处理失败: {e}")
        return {"matched": False, "message": f"处理失败: {str(e)}"}
    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass
        if converted_path and os.path.exists(converted_path):
            try:
                os.remove(converted_path)
            except:
                pass


def recognize_by_description(description: str, all_songs: List[Dict]) -> Dict:
    """通过描述识别歌曲 - 用户描述歌曲特征，AI匹配"""
    from ai_service import call_qwen_api
    
    songs_info = []
    for s in all_songs[:100]:
        songs_info.append(f"ID:{s['id']} 《{s.get('title', '')}》- {s.get('artist', '')} 风格:{s.get('genre', '')} 标签:{s.get('tags', '')}")
    
    system_prompt = """你是一个音乐识别专家。用户会描述一首歌的特征（如旋律、歌词片段、歌手声音等），
你需要从歌曲列表中找出最可能匹配的歌曲。
返回JSON格式:
- matched: 是否找到匹配(true/false)
- song_id: 匹配的歌曲ID(如果找到)
- confidence: 置信度(0-100)
- reason: 匹配原因
只返回JSON，不要其他内容。"""
    
    prompt = f"""用户描述: "{description}"

歌曲列表:
{chr(10).join(songs_info)}

请找出最可能匹配的歌曲:"""
    
    result = call_qwen_api(prompt, system_prompt)
    
    try:
        result = result.strip()
        if result.startswith("```"):
            result = result.split("```")[1]
            if result.startswith("json"):
                result = result[4:]
        data = json.loads(result)
        
        if data.get("matched") and data.get("song_id"):
            song = next((s for s in all_songs if s["id"] == data["song_id"]), None)
            if song:
                data["title"] = song.get("title", "")
                data["artist"] = song.get("artist", "")
        
        return data
    except:
        return {"matched": False, "message": "识别失败"}
