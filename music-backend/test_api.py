#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
API 测试脚本
用于验证新增的 API 端点是否正常工作
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5000/api"

def test_playlists():
    """测试歌单API"""
    print("=" * 50)
    print("测试歌单API")
    print("=" * 50)
    
    # 测试获取歌单列表
    print("\n1. 获取歌单列表...")
    response = requests.get(f"{BASE_URL}/playlists?user_id=1")
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    else:
        print(f"错误: {response.text}")

def test_history():
    """测试播放历史API"""
    print("\n" + "=" * 50)
    print("测试播放历史API")
    print("=" * 50)
    
    # 测试获取播放历史
    print("\n1. 获取播放历史...")
    response = requests.get(f"{BASE_URL}/users/1/history")
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    else:
        print(f"错误: {response.text}")

def test_stats():
    """测试用户统计API"""
    print("\n" + "=" * 50)
    print("测试用户统计API")
    print("=" * 50)
    
    # 测试获取用户统计
    print("\n1. 获取用户统计...")
    response = requests.get(f"{BASE_URL}/users/1/stats")
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    else:
        print(f"错误: {response.text}")

def test_ranking():
    """测试排行榜API"""
    print("\n" + "=" * 50)
    print("测试排行榜API")
    print("=" * 50)
    
    # 测试获取排行榜
    print("\n1. 获取排行榜...")
    response = requests.get(f"{BASE_URL}/songs/ranking")
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"返回歌曲数: {len(data)}")
        if data:
            print(f"第一首歌: {json.dumps(data[0], indent=2, ensure_ascii=False)}")
    else:
        print(f"错误: {response.text}")

if __name__ == "__main__":
    print("开始测试 API...")
    print("请确保后端服务正在运行 (python app.py)")
    print()
    
    try:
        test_playlists()
        test_history()
        test_stats()
        test_ranking()
        print("\n" + "=" * 50)
        print("测试完成！")
        print("=" * 50)
    except requests.exceptions.ConnectionError:
        print("\n错误: 无法连接到后端服务")
        print("请确保后端服务正在运行: python app.py")
    except Exception as e:
        print(f"\n错误: {e}")
