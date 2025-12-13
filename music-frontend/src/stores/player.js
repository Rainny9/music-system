import { reactive, ref } from 'vue';
import api from '../api';

// 播放模式：order=顺序播放, loop=列表循环, single=单曲循环, random=随机播放
export const PLAY_MODES = {
  ORDER: 'order',
  LOOP: 'loop',
  SINGLE: 'single',
  RANDOM: 'random',
};

// 全局播放器状态
export const playerState = reactive({
  currentSong: null,
  isPlaying: false,
  currentTime: 0,
  duration: 0,
  volume: 0.8,
  playMode: PLAY_MODES.LOOP,
  playlist: [], // 播放列表
  currentIndex: -1, // 当前播放索引
});

// 播放器实例引用
export const audioRef = ref(null);

// 设置播放列表
export const setPlaylist = (songs, index = 0) => {
  playerState.playlist = songs;
  playerState.currentIndex = index;
};

// 播放歌曲
export const playSong = (song, songs = null) => {
  if (songs) {
    playerState.playlist = songs;
    playerState.currentIndex = songs.findIndex(s => s.id === song.id);
  } else if (playerState.playlist.length === 0) {
    playerState.playlist = [song];
    playerState.currentIndex = 0;
  } else {
    const idx = playerState.playlist.findIndex(s => s.id === song.id);
    if (idx > -1) {
      playerState.currentIndex = idx;
    } else {
      playerState.playlist.push(song);
      playerState.currentIndex = playerState.playlist.length - 1;
    }
  }
  playerState.currentSong = song;
  playerState.isPlaying = true;
};

// 播放上一首
export const playPrev = () => {
  if (playerState.playlist.length === 0) return;
  let newIndex;
  if (playerState.playMode === PLAY_MODES.RANDOM) {
    newIndex = Math.floor(Math.random() * playerState.playlist.length);
  } else {
    newIndex = playerState.currentIndex - 1;
    if (newIndex < 0) {
      newIndex = playerState.playlist.length - 1;
    }
  }
  playerState.currentIndex = newIndex;
  playerState.currentSong = playerState.playlist[newIndex];
  playerState.isPlaying = true;
};

// 播放下一首
export const playNext = () => {
  if (playerState.playlist.length === 0) return;
  let newIndex;
  if (playerState.playMode === PLAY_MODES.RANDOM) {
    newIndex = Math.floor(Math.random() * playerState.playlist.length);
  } else {
    newIndex = playerState.currentIndex + 1;
    if (newIndex >= playerState.playlist.length) {
      if (playerState.playMode === PLAY_MODES.ORDER) {
        playerState.isPlaying = false;
        return;
      }
      newIndex = 0;
    }
  }
  playerState.currentIndex = newIndex;
  playerState.currentSong = playerState.playlist[newIndex];
  playerState.isPlaying = true;
};

// 切换播放模式
export const togglePlayMode = () => {
  const modes = [PLAY_MODES.LOOP, PLAY_MODES.SINGLE, PLAY_MODES.RANDOM, PLAY_MODES.ORDER];
  const currentIdx = modes.indexOf(playerState.playMode);
  playerState.playMode = modes[(currentIdx + 1) % modes.length];
};

// 设置音量
export const setVolume = (vol) => {
  playerState.volume = Math.max(0, Math.min(1, vol));
  if (audioRef.value) {
    audioRef.value.volume = playerState.volume;
  }
};

// 暂停
export const pauseSong = () => {
  playerState.isPlaying = false;
  if (audioRef.value) {
    audioRef.value.pause();
  }
};

// 继续播放
export const resumeSong = () => {
  playerState.isPlaying = true;
  if (audioRef.value) {
    audioRef.value.play();
  }
};

// 切换播放/暂停
export const togglePlay = () => {
  if (playerState.isPlaying) {
    pauseSong();
  } else {
    resumeSong();
  }
};

// 格式化时长
export const formatDuration = (seconds) => {
  if (!seconds || isNaN(seconds)) return '--:--';
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
};

// 增加播放次数
export const incrementPlayCount = async (songId) => {
  try {
    await api.post(`/songs/${songId}/play_count`);
  } catch (error) {
    console.error('增加播放次数失败:', error);
  }
};
