<template>
  <div class="profile-page">
    <div class="profile-header">
      <div class="avatar-section">
        <div class="avatar" @click="triggerAvatarUpload">
          <img v-if="userInfo.avatar_url" :src="userInfo.avatar_url" alt="头像" />
          <div v-else class="avatar-placeholder">{{ userInfo.username?.charAt(0)?.toUpperCase() || 'U' }}</div>
          <div class="avatar-overlay">
            <svg viewBox="0 0 24 24" width="24" height="24">
              <path fill="#fff" d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/>
            </svg>
          </div>
        </div>
        <input type="file" ref="avatarInput" accept="image/*" @change="uploadAvatar" style="display:none" />
      </div>
      <div class="user-info">
        <h2>{{ userInfo.username }}</h2>
        <p class="join-date">加入于 {{ formatDate(userInfo.created_at) }}</p>
      </div>
    </div>

    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-value">{{ stats.favorite_count }}</div>
        <div class="stat-label">收藏歌曲</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ stats.playlist_count }}</div>
        <div class="stat-label">创建歌单</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ formatDuration(stats.total_play_time) }}</div>
        <div class="stat-label">累计听歌</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ stats.week_play_count }}</div>
        <div class="stat-label">本周播放</div>
      </div>
    </div>

    <div class="settings-section">
      <h3>账号设置</h3>
      <div class="setting-item">
        <div class="setting-label">用户名</div>
        <div class="setting-value">
          <input v-if="editingUsername" v-model="newUsername" @blur="saveUsername" @keyup.enter="saveUsername" />
          <span v-else>{{ userInfo.username }}</span>
          <button class="btn-edit" @click="editUsername">
            <svg viewBox="0 0 24 24" width="16" height="16">
              <path fill="currentColor" d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/>
            </svg>
          </button>
        </div>
      </div>
      <div class="setting-item">
        <div class="setting-label">密码</div>
        <div class="setting-value">
          <span>••••••••</span>
          <button class="btn-edit" @click="showPasswordModal = true">修改</button>
        </div>
      </div>
      <div class="setting-item">
        <div class="setting-label">性别</div>
        <div class="setting-value">
          <select v-model="profileForm.gender" class="setting-select">
            <option value="">未设置</option>
            <option value="male">男</option>
            <option value="female">女</option>
            <option value="other">其他</option>
          </select>
        </div>
      </div>
      <div class="setting-item">
        <div class="setting-label">生日</div>
        <div class="setting-value">
          <input type="date" v-model="profileForm.birthday" class="setting-input" />
        </div>
      </div>
      <div class="setting-item">
        <div class="setting-label">地区</div>
        <div class="setting-value region-selects">
          <select v-model="selectedProvince" @change="onProvinceChange" class="setting-select">
            <option value="">选择省份</option>
            <option v-for="p in provinces" :key="p.name" :value="p.name">{{ p.name }}</option>
          </select>
          <select v-model="selectedCity" class="setting-select">
            <option value="">选择城市</option>
            <option v-for="c in currentCities" :key="c" :value="c">{{ c }}</option>
          </select>
        </div>
      </div>
      <div class="setting-item save-row">
        <div></div>
        <button class="btn-save" @click="saveAllProfile">保存修改</button>
      </div>
    </div>

    <!-- 修改密码弹窗 -->
    <div v-if="showPasswordModal" class="modal-overlay" @click.self="showPasswordModal = false">
      <div class="modal">
        <div class="modal-header">
          <h3>修改密码</h3>
          <button class="close-btn" @click="showPasswordModal = false">×</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>旧密码</label>
            <input v-model="passwordForm.old_password" type="password" placeholder="请输入旧密码" />
          </div>
          <div class="form-group">
            <label>新密码</label>
            <input v-model="passwordForm.new_password" type="password" placeholder="请输入新密码" />
          </div>
          <div class="form-group">
            <label>确认新密码</label>
            <input v-model="passwordForm.confirm_password" type="password" placeholder="请再次输入新密码" />
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn" @click="showPasswordModal = false">取消</button>
          <button class="btn primary" @click="changePassword">确认修改</button>
        </div>
      </div>
    </div>

    <!-- Toast -->
    <div v-if="toast.show" class="toast" :class="toast.type">{{ toast.message }}</div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import api from '../api';

const router = useRouter();
const userId = ref(null);
const userInfo = ref({});
const stats = ref({
  favorite_count: 0,
  playlist_count: 0,
  total_play_time: 0,
  week_play_count: 0
});
const editingUsername = ref(false);
const newUsername = ref('');
const showPasswordModal = ref(false);
const passwordForm = ref({
  old_password: '',
  new_password: '',
  confirm_password: ''
});
const avatarInput = ref(null);
const toast = ref({ show: false, message: '', type: 'success' });

// 个人资料表单
const profileForm = ref({ gender: '', birthday: '' });
const selectedProvince = ref('');
const selectedCity = ref('');

// 省市数据
const provinces = [
  { name: '北京', cities: ['东城区', '西城区', '朝阳区', '丰台区', '石景山区', '海淀区', '顺义区', '通州区', '大兴区', '房山区', '门头沟区', '昌平区', '平谷区', '密云区', '怀柔区', '延庆区'] },
  { name: '上海', cities: ['黄浦区', '徐汇区', '长宁区', '静安区', '普陀区', '虹口区', '杨浦区', '闵行区', '宝山区', '嘉定区', '浦东新区', '金山区', '松江区', '青浦区', '奉贤区', '崇明区'] },
  { name: '天津', cities: ['和平区', '河东区', '河西区', '南开区', '河北区', '红桥区', '东丽区', '西青区', '津南区', '北辰区', '武清区', '宝坻区', '滨海新区', '宁河区', '静海区', '蓟州区'] },
  { name: '重庆', cities: ['渝中区', '大渡口区', '江北区', '沙坪坝区', '九龙坡区', '南岸区', '北碚区', '渝北区', '巴南区', '涪陵区', '万州区', '永川区', '合川区', '江津区', '璧山区', '铜梁区'] },
  { name: '广东', cities: ['广州', '深圳', '珠海', '汕头', '佛山', '韶关', '湛江', '肇庆', '江门', '茂名', '惠州', '梅州', '汕尾', '河源', '阳江', '清远', '东莞', '中山', '潮州', '揭阳', '云浮'] },
  { name: '江苏', cities: ['南京', '无锡', '徐州', '常州', '苏州', '南通', '连云港', '淮安', '盐城', '扬州', '镇江', '泰州', '宿迁'] },
  { name: '浙江', cities: ['杭州', '宁波', '温州', '嘉兴', '湖州', '绍兴', '金华', '衢州', '舟山', '台州', '丽水'] },
  { name: '四川', cities: ['成都', '自贡', '攀枝花', '泸州', '德阳', '绵阳', '广元', '遂宁', '内江', '乐山', '南充', '眉山', '宜宾', '广安', '达州', '雅安', '巴中', '资阳'] },
  { name: '湖北', cities: ['武汉', '黄石', '十堰', '宜昌', '襄阳', '鄂州', '荆门', '孝感', '荆州', '黄冈', '咸宁', '随州'] },
  { name: '湖南', cities: ['长沙', '株洲', '湘潭', '衡阳', '邵阳', '岳阳', '常德', '张家界', '益阳', '郴州', '永州', '怀化', '娄底'] },
  { name: '山东', cities: ['济南', '青岛', '淄博', '枣庄', '东营', '烟台', '潍坊', '济宁', '泰安', '威海', '日照', '临沂', '德州', '聊城', '滨州', '菏泽'] },
  { name: '河南', cities: ['郑州', '开封', '洛阳', '平顶山', '安阳', '鹤壁', '新乡', '焦作', '濮阳', '许昌', '漯河', '三门峡', '南阳', '商丘', '信阳', '周口', '驻马店'] },
  { name: '福建', cities: ['福州', '厦门', '莆田', '三明', '泉州', '漳州', '南平', '龙岩', '宁德'] },
  { name: '陕西', cities: ['西安', '铜川', '宝鸡', '咸阳', '渭南', '延安', '汉中', '榆林', '安康', '商洛'] },
  { name: '云南', cities: ['昆明', '曲靖', '玉溪', '保山', '昭通', '丽江', '普洱', '临沧'] },
  { name: '河北', cities: ['石家庄', '唐山', '秦皇岛', '邯郸', '邢台', '保定', '张家口', '承德', '沧州', '廊坊', '衡水'] },
  { name: '山西', cities: ['太原', '大同', '阳泉', '长治', '晋城', '朔州', '晋中', '运城', '忻州', '临汾', '吕梁'] },
  { name: '辽宁', cities: ['沈阳', '大连', '鞍山', '抚顺', '本溪', '丹东', '锦州', '营口', '阜新', '辽阳', '盘锦', '铁岭', '朝阳', '葫芦岛'] },
  { name: '吉林', cities: ['长春', '吉林', '四平', '辽源', '通化', '白山', '松原', '白城'] },
  { name: '黑龙江', cities: ['哈尔滨', '齐齐哈尔', '鸡西', '鹤岗', '双鸭山', '大庆', '伊春', '佳木斯', '七台河', '牡丹江', '黑河', '绥化'] },
  { name: '安徽', cities: ['合肥', '芜湖', '蚌埠', '淮南', '马鞍山', '淮北', '铜陵', '安庆', '黄山', '滁州', '阜阳', '宿州', '六安', '亳州', '池州', '宣城'] },
  { name: '江西', cities: ['南昌', '景德镇', '萍乡', '九江', '新余', '鹰潭', '赣州', '吉安', '宜春', '抚州', '上饶'] },
  { name: '广西', cities: ['南宁', '柳州', '桂林', '梧州', '北海', '防城港', '钦州', '贵港', '玉林', '百色', '贺州', '河池', '来宾', '崇左'] },
  { name: '海南', cities: ['海口', '三亚', '三沙', '儋州'] },
  { name: '贵州', cities: ['贵阳', '六盘水', '遵义', '安顺', '毕节', '铜仁'] },
  { name: '甘肃', cities: ['兰州', '嘉峪关', '金昌', '白银', '天水', '武威', '张掖', '平凉', '酒泉', '庆阳', '定西', '陇南'] },
  { name: '青海', cities: ['西宁', '海东'] },
  { name: '中国台湾', cities: ['台北', '高雄', '台中', '台南', '新北', '桃园'] },
  { name: '中国香港', cities: ['香港岛', '九龙', '新界'] },
  { name: '中国澳门', cities: ['澳门半岛', '氹仔', '路环'] },
  { name: '内蒙古', cities: ['呼和浩特', '包头', '乌海', '赤峰', '通辽', '鄂尔多斯', '呼伦贝尔', '巴彦淖尔', '乌兰察布'] },
  { name: '西藏', cities: ['拉萨', '日喀则', '昌都', '林芝', '山南', '那曲'] },
  { name: '宁夏', cities: ['银川', '石嘴山', '吴忠', '固原', '中卫'] },
  { name: '新疆', cities: ['乌鲁木齐', '克拉玛依', '吐鲁番', '哈密', '喀什', '和田', '阿克苏'] }
];

const currentCities = computed(() => {
  const p = provinces.find(item => item.name === selectedProvince.value);
  return p ? p.cities : [];
});

const onProvinceChange = () => {
  selectedCity.value = '';
};

const showToast = (message, type = 'success') => {
  toast.value = { show: true, message, type };
  setTimeout(() => { toast.value.show = false; }, 3000);
};

const formatDate = (dateStr) => {
  if (!dateStr) return '-';
  return new Date(dateStr).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
};

const formatDuration = (seconds) => {
  if (!seconds) return '0分钟';
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  if (hours > 0) return `${hours}小时${minutes}分钟`;
  return `${minutes}分钟`;
};

const loadUserInfo = async () => {
  try {
    const res = await api.get(`/users/${userId.value}/info`);
    userInfo.value = res.data;
    // 初始化表单
    profileForm.value.gender = res.data.gender || '';
    profileForm.value.birthday = res.data.birthday || '';
    // 解析地区
    if (res.data.region) {
      const parts = res.data.region.split(' ');
      selectedProvince.value = parts[0] || '';
      selectedCity.value = parts[1] || '';
    }
  } catch (e) {
    showToast('加载用户信息失败', 'error');
  }
};

const loadStats = async () => {
  try {
    const res = await api.get(`/users/${userId.value}/stats`);
    stats.value = res.data;
  } catch (e) {
    console.error('加载统计失败:', e);
  }
};

const triggerAvatarUpload = () => {
  avatarInput.value?.click();
};

const uploadAvatar = async (e) => {
  const file = e.target.files[0];
  if (!file) return;

  const formData = new FormData();
  formData.append('avatar', file);

  try {
    const res = await api.post(`/users/${userId.value}/avatar`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    userInfo.value.avatar_url = res.data.avatar_url;
    localStorage.setItem('avatar_url', res.data.avatar_url);
    showToast('头像已更新');
  } catch (e) {
    showToast('上传失败', 'error');
  }
};

const editUsername = () => {
  newUsername.value = userInfo.value.username;
  editingUsername.value = true;
};

const saveUsername = async () => {
  if (!newUsername.value.trim()) {
    editingUsername.value = false;
    return;
  }

  if (newUsername.value === userInfo.value.username) {
    editingUsername.value = false;
    return;
  }

  try {
    await api.put(`/users/${userId.value}/profile`, {
      username: newUsername.value
    });
    userInfo.value.username = newUsername.value;
    localStorage.setItem('username', newUsername.value);
    showToast('用户名已更新');
    editingUsername.value = false;
  } catch (e) {
    showToast(e.response?.data?.msg || '更新失败', 'error');
  }
};

const changePassword = async () => {
  if (!passwordForm.value.old_password || !passwordForm.value.new_password) {
    showToast('请填写完整', 'error');
    return;
  }

  if (passwordForm.value.new_password !== passwordForm.value.confirm_password) {
    showToast('两次输入的密码不一致', 'error');
    return;
  }

  try {
    await api.put(`/users/${userId.value}/password`, {
      old_password: passwordForm.value.old_password,
      new_password: passwordForm.value.new_password
    });
    showToast('密码已修改');
    showPasswordModal.value = false;
    passwordForm.value = { old_password: '', new_password: '', confirm_password: '' };
  } catch (e) {
    showToast(e.response?.data?.msg || '修改失败', 'error');
  }
};

const saveAllProfile = async () => {
  try {
    const region = selectedProvince.value && selectedCity.value 
      ? `${selectedProvince.value} ${selectedCity.value}` 
      : selectedProvince.value || '';
    await api.put(`/users/${userId.value}/profile`, {
      gender: profileForm.value.gender || '',
      birthday: profileForm.value.birthday || '',
      region: region
    });
    userInfo.value.gender = profileForm.value.gender;
    userInfo.value.birthday = profileForm.value.birthday;
    userInfo.value.region = region;
    showToast('保存成功');
  } catch (e) {
    showToast('保存失败', 'error');
  }
};

onMounted(() => {
  userId.value = localStorage.getItem('user_id');
  if (!userId.value) {
    alert('请先登录');
    router.push('/login');
    return;
  }
  loadUserInfo();
  loadStats();
});
</script>

<style scoped>
/* 个人中心 - 中华风 */
.profile-page {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
  min-height: calc(100vh - 140px);
  background: rgba(255, 254, 249, 0.85);
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 24px;
  padding: 32px;
  background: linear-gradient(135deg, #fffef9, rgba(212, 168, 75, 0.05));
  border-radius: 8px;
  margin-bottom: 24px;
  border: 1px solid rgba(212, 168, 75, 0.2);
  position: relative;
  overflow: hidden;
}

.profile-header::before {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, rgba(45, 90, 90, 0.05) 0%, transparent 70%);
  pointer-events: none;
}

.avatar-section {
  position: relative;
}

.avatar {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  overflow: hidden;
  cursor: pointer;
  position: relative;
  border: 3px solid #d4a84b;
  box-shadow: 0 4px 15px rgba(212, 168, 75, 0.3);
}

.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #2d5a5a, #1e3d3d);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #d4a84b;
  font-size: 36px;
  font-weight: 600;
}

.avatar-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(26, 26, 26, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s;
}

.avatar:hover .avatar-overlay {
  opacity: 1;
}

.user-info h2 {
  font-size: 24px;
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 8px;
  letter-spacing: 1px;
}

.join-date {
  color: #999;
  font-size: 14px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: linear-gradient(135deg, #E6F4EA 0%, #fffef9 100%);
  padding: 24px;
  border-radius: 8px;
  text-align: center;
  border: 1px solid rgba(212, 168, 75, 0.15);
  transition: all 0.3s;
  position: relative;
  overflow: hidden;
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #2d5a5a, #d4a84b);
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(45, 90, 90, 0.1);
}

.stat-value {
  font-size: 32px;
  font-weight: 600;
  background: linear-gradient(135deg, #2d5a5a, #d4a84b);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #999;
}

.settings-section {
  background: linear-gradient(180deg, #fffef9 0%, #E6F4EA 100%);
  padding: 24px;
  border-radius: 8px;
  border: 1px solid rgba(212, 168, 75, 0.15);
}

.settings-section h3 {
  font-size: 18px;
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 20px;
  padding-left: 12px;
  position: relative;
  letter-spacing: 1px;
}

.settings-section h3::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 18px;
  background: linear-gradient(180deg, #2d5a5a, #d4a84b);
  border-radius: 2px;
}

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0;
  border-bottom: 1px solid rgba(212, 168, 75, 0.1);
}

.setting-item:last-child {
  border-bottom: none;
}

.setting-label {
  font-size: 14px;
  color: #666;
}

.setting-value {
  display: flex;
  align-items: center;
  gap: 12px;
}

.setting-value input {
  padding: 6px 12px;
  border: 1px solid rgba(212, 168, 75, 0.3);
  border-radius: 4px;
  font-size: 14px;
  transition: all 0.3s;
}

.setting-value input:focus {
  outline: none;
  border-color: #d4a84b;
  box-shadow: 0 0 0 2px rgba(212, 168, 75, 0.1);
}

.btn-edit {
  padding: 6px 12px;
  background: rgba(212, 168, 75, 0.1);
  border: none;
  border-radius: 4px;
  color: #8b7355;
  font-size: 13px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
  transition: all 0.3s;
}

.btn-edit:hover {
  background: rgba(212, 168, 75, 0.2);
  color: #d4a84b;
}

.setting-select,
.setting-input {
  padding: 8px 12px;
  border: 1px solid rgba(212, 168, 75, 0.3);
  border-radius: 4px;
  font-size: 14px;
  background: #fff;
  color: #1a1a1a;
  min-width: 150px;
  transition: all 0.3s;
  cursor: pointer;
}

.setting-select:focus,
.setting-input:focus {
  outline: none;
  border-color: #d4a84b;
  box-shadow: 0 0 0 2px rgba(212, 168, 75, 0.1);
}

.setting-select:hover,
.setting-input:hover {
  border-color: #d4a84b;
}

.region-selects {
  display: flex;
  gap: 10px;
}

.region-selects .setting-select {
  min-width: 120px;
}

.save-row {
  border-bottom: none !important;
  padding-top: 20px;
}

.btn-save {
  padding: 10px 32px;
  background: linear-gradient(135deg, rgba(255,255,255,0.4) 0%, #8BA8A8 50%, #7a9999 100%);
  border: 1px solid #d4a84b;
  border-radius: 4px;
  color: #fff;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
  letter-spacing: 1px;
}

.btn-save:hover {
  background: linear-gradient(135deg, rgba(255,255,255,0.5) 0%, #9ab8b8 50%, #8BA8A8 100%);
  box-shadow: 0 4px 12px rgba(139, 168, 168, 0.4);
}

/* Modal - 中华风 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(26, 26, 26, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: #fffef9;
  border-radius: 8px;
  width: 420px;
  max-width: 90%;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(212, 168, 75, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid rgba(212, 168, 75, 0.2);
  background: linear-gradient(90deg, rgba(45, 90, 90, 0.05), transparent);
}

.modal-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: #1a1a1a;
  letter-spacing: 1px;
}

.close-btn {
  width: 28px;
  height: 28px;
  border: none;
  background: none;
  font-size: 20px;
  color: #999;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.3s;
}

.close-btn:hover {
  background: rgba(45, 90, 90, 0.1);
  color: #2d5a5a;
}

.modal-body {
  padding: 20px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  font-size: 13px;
  color: #666;
  margin-bottom: 6px;
}

.form-group input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid rgba(212, 168, 75, 0.3);
  border-radius: 4px;
  font-size: 14px;
  box-sizing: border-box;
  background: #fff;
  transition: all 0.3s;
}

.form-group input:focus {
  outline: none;
  border-color: #d4a84b;
  box-shadow: 0 0 0 2px rgba(212, 168, 75, 0.1);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 16px 20px;
  border-top: 1px solid rgba(212, 168, 75, 0.2);
}

.btn {
  padding: 8px 20px;
  border: 1px solid rgba(212, 168, 75, 0.3);
  border-radius: 4px;
  background: #fff;
  color: #666;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn:hover {
  border-color: #d4a84b;
  color: #d4a84b;
}

.btn.primary {
  background: linear-gradient(135deg, rgba(255,255,255,0.4) 0%, #8BA8A8 50%, #7a9999 100%);
  border-color: #d4a84b;
  color: #d4a84b;
}

.btn.primary:hover {
  background: linear-gradient(135deg, rgba(255,255,255,0.5) 0%, #9ab8b8 50%, #8BA8A8 100%);
  box-shadow: 0 4px 12px rgba(139, 168, 168, 0.4);
}

/* Toast - 中华风 */
.toast {
  position: fixed;
  top: 80px;
  left: 50%;
  transform: translateX(-50%);
  padding: 12px 24px;
  border-radius: 4px;
  font-size: 14px;
  z-index: 2000;
  animation: slideDown 0.3s ease;
  border: 1px solid;
}

.toast.success {
  background: linear-gradient(135deg, rgba(212, 168, 75, 0.1), rgba(212, 168, 75, 0.05));
  color: #8b7355;
  border-color: rgba(212, 168, 75, 0.3);
}

.toast.error {
  background: linear-gradient(135deg, rgba(220, 53, 69, 0.1), rgba(220, 53, 69, 0.05));
  color: #dc3545;
  border-color: rgba(220, 53, 69, 0.3);
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateX(-50%) translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
}
</style>
