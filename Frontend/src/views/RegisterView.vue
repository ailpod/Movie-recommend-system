<template>
  <div class="register-view">
    <div class="register-container">
      <!-- 背景装饰 -->
      <div class="background-decoration">
        <div class="floating-element" v-for="i in 6" :key="i" :style="getFloatingStyle(i)">
          🎬
        </div>
      </div>

      <!-- 注册卡片 -->
      <div class="register-card">
        <!-- Logo和标题 -->
        <div class="register-header">
          <div class="logo">
            <span class="logo-icon">🎬</span>
            <span class="logo-text">影视推荐</span>
          </div>
          <h1 class="register-title">加入我们</h1>
          <p class="register-subtitle">创建您的账户，开启个性化观影之旅</p>
        </div>

        <!-- 注册表单 -->
        <form @submit.prevent="handleRegister" class="register-form">
          <!-- 用户名输入 -->
          <div class="form-group">
            <label for="username" class="form-label">用户名</label>
            <div class="input-container">
              <svg class="input-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                <circle cx="12" cy="7" r="4"/>
              </svg>
              <input
                id="username"
                v-model="registerForm.username"
                type="text"
                class="form-input"
                placeholder="请输入用户名（3-50个字符）"
                required
                :disabled="loading"
                minlength="3"
                maxlength="50"
                pattern="[a-zA-Z0-9_]+"
              />
            </div>
            <div class="form-hint">只能包含字母、数字和下划线</div>
          </div>

          <!-- 邮箱输入 -->
          <div class="form-group">
            <label for="email" class="form-label">邮箱</label>
            <div class="input-container">
              <svg class="input-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
                <polyline points="22,6 12,13 2,6"/>
              </svg>
              <input
                id="email"
                v-model="registerForm.email"
                type="email"
                class="form-input"
                placeholder="请输入邮箱地址"
                required
                :disabled="loading"
              />
            </div>
          </div>

          <!-- 密码输入 -->
          <div class="form-group">
            <label for="password" class="form-label">密码</label>
            <div class="input-container">
              <svg class="input-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                <circle cx="12" cy="7" r="4"/>
              </svg>
              <input
                id="password"
                v-model="registerForm.password"
                :type="showPassword ? 'text' : 'password'"
                class="form-input"
                placeholder="请输入密码（至少6个字符）"
                required
                :disabled="loading"
                minlength="6"
                maxlength="100"
              />
              <button
                type="button"
                class="password-toggle"
                @click="showPassword = !showPassword"
                :disabled="loading"
              >
                <svg v-if="showPassword" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
                  <line x1="1" y1="1" x2="23" y2="23"/>
                </svg>
                <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                  <circle cx="12" cy="12" r="3"/>
                </svg>
              </button>
            </div>
          </div>

          <!-- 确认密码输入 -->
          <div class="form-group">
            <label for="confirmPassword" class="form-label">确认密码</label>
            <div class="input-container">
              <svg class="input-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                <circle cx="12" cy="7" r="4"/>
              </svg>
              <input
                id="confirmPassword"
                v-model="confirmPassword"
                :type="showConfirmPassword ? 'text' : 'password'"
                class="form-input"
                placeholder="请再次输入密码"
                required
                :disabled="loading"
              />
              <button
                type="button"
                class="password-toggle"
                @click="showConfirmPassword = !showConfirmPassword"
                :disabled="loading"
              >
                <svg v-if="showConfirmPassword" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
                  <line x1="1" y1="1" x2="23" y2="23"/>
                </svg>
                <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                  <circle cx="12" cy="12" r="3"/>
                </svg>
              </button>
            </div>
            <div v-if="passwordMismatch" class="form-error">两次输入的密码不一致</div>
          </div>

          <!-- 年龄输入 -->
          <div class="form-group">
            <label for="age" class="form-label">年龄</label>
            <div class="input-container">
              <svg class="input-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <circle cx="12" cy="12" r="10"/>
                <polyline points="12,6 12,12 16,14"/>
              </svg>
              <input
                id="age"
                v-model.number="registerForm.age"
                type="number"
                class="form-input"
                placeholder="请输入年龄"
                min="1"
                max="150"
                :disabled="loading"
              />
            </div>
          </div>

          <!-- 性别选择 -->
          <div class="form-group">
            <label class="form-label">性别</label>
            <div class="gender-options">
              <label class="gender-option">
                <input
                  type="radio"
                  v-model="registerForm.gender"
                  value="male"
                  :disabled="loading"
                />
                <span class="gender-label">
                  <svg class="gender-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <circle cx="12" cy="4" r="2"/>
                    <path d="M12 6v6"/>
                    <path d="M12 12l-2 8h4l-2-8"/>
                  </svg>
                  男性
                </span>
              </label>
              <label class="gender-option">
                <input
                  type="radio"
                  v-model="registerForm.gender"
                  value="female"
                  :disabled="loading"
                />
                <span class="gender-label">
                  <svg class="gender-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <circle cx="12" cy="4" r="2"/>
                    <path d="M12 6v6"/>
                    <path d="M12 12l-2 8h4l-2-8"/>
                    <path d="M8 12h8"/>
                  </svg>
                  女性
                </span>
              </label>
              <label class="gender-option">
                <input
                  type="radio"
                  v-model="registerForm.gender"
                  value="other"
                  :disabled="loading"
                />
                <span class="gender-label">
                  <svg class="gender-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <circle cx="12" cy="12" r="3"/>
                  </svg>
                  其他
                </span>
              </label>
            </div>
          </div>

          <!-- 电影偏好选择 -->
          <div class="form-group">
            <label class="form-label">电影偏好 (可多选，可跳过)</label>
            <div class="genre-selection">
              <div class="genre-grid">
                <label 
                  v-for="genre in availableGenres" 
                  :key="genre" 
                  class="genre-option"
                  :class="{ selected: registerForm.like_genres.includes(genre) }"
                >
                  <input 
                    type="checkbox" 
                    :value="genre" 
                    v-model="registerForm.like_genres"
                    :disabled="loading"
                  >
                  <span class="genre-name">{{ genre }}</span>
                </label>
              </div>
              <div class="genre-hint">
                选择您喜欢的电影类型，我们将为您提供个性化推荐
              </div>
            </div>
          </div>

          <!-- 错误提示 -->
          <div v-if="error" class="error-message">
            <svg class="error-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <circle cx="12" cy="12" r="10"/>
              <line x1="12" y1="8" x2="12" y2="12"/>
              <line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
            <span>{{ error }}</span>
          </div>

          <!-- 注册按钮 -->
          <button
            type="submit"
            class="register-button"
            :disabled="loading || !isFormValid"
          >
            <span v-if="loading" class="loading-spinner"></span>
            <span>{{ loading ? '注册中...' : '创建账户' }}</span>
          </button>
        </form>

        <!-- 登录链接 -->
        <div class="register-footer">
          <p>已有账户？ 
            <router-link to="/login" class="login-link">立即登录</router-link>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'RegisterView',
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()

    // 表单数据
    const registerForm = ref({
      username: '',
      email: '',
      password: '',
      age: null,
      gender: '',
      like_genres: []
    })

    // 可选的电影类型
    const availableGenres = ref([
      '动作', '冒险', '喜剧', '剧情', '家庭', '奇幻', 
      '恐怖', '悬疑', '爱情', '科幻', '惊悚', '战争',
      '西部', '动画', '犯罪', '纪录片', '历史', '音乐',
      '运动', '传记', '儿童', '短片'
    ])

    const confirmPassword = ref('')
    const showPassword = ref(false)
    const showConfirmPassword = ref(false)
    const loading = ref(false)
    const error = ref('')

    // 密码匹配检查
    const passwordMismatch = computed(() => {
      return confirmPassword.value && registerForm.value.password !== confirmPassword.value
    })

    // 表单验证
    const isFormValid = computed(() => {
      return (
        registerForm.value.username &&
        registerForm.value.email &&
        registerForm.value.password &&
        confirmPassword.value &&
        !passwordMismatch.value &&
        registerForm.value.username.length >= 3 &&
        registerForm.value.password.length >= 6
      )
    })

    // 清除错误信息
    watch([registerForm, confirmPassword], () => {
      if (error.value) {
        error.value = ''
      }
    }, { deep: true })

    // 处理注册
    const handleRegister = async () => {
      if (!isFormValid.value) {
        error.value = '请填写完整的注册信息'
        return
      }

      loading.value = true
      error.value = ''

      try {
        // 处理电影偏好数据
        const formData = {
          ...registerForm.value,
          like_genres: registerForm.value.like_genres.length > 0 
            ? registerForm.value.like_genres.join(',') 
            : ''
        }
        
        await authStore.register(formData)
        router.push('/login')
      } catch (err) {
        error.value = err.response?.data?.detail || '注册失败，请稍后重试'
      } finally {
        loading.value = false
      }
    }

    // 背景装饰动画
    const getFloatingStyle = (index) => {
      const positions = [
        { top: '10%', left: '10%', animationDelay: '0s' },
        { top: '20%', right: '15%', animationDelay: '2s' },
        { top: '60%', left: '5%', animationDelay: '4s' },
        { bottom: '20%', right: '10%', animationDelay: '1s' },
        { bottom: '10%', left: '20%', animationDelay: '3s' },
        { top: '40%', right: '5%', animationDelay: '5s' }
      ]
      return positions[index - 1] || positions[0]
    }

    return {
      registerForm,
      availableGenres,
      confirmPassword,
      showPassword,
      showConfirmPassword,
      loading,
      error,
      passwordMismatch,
      isFormValid,
      handleRegister,
      getFloatingStyle
    }
  }
}
</script>

<style scoped>
.register-view {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  position: relative;
  overflow: hidden;
}

.register-container {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 500px;
}

.background-decoration {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
}

.floating-element {
  position: absolute;
  font-size: 2rem;
  opacity: 0.1;
  animation: float 6s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0px) rotate(0deg); }
  50% { transform: translateY(-20px) rotate(10deg); }
}

.register-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 40px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.register-header {
  text-align: center;
  margin-bottom: 30px;
}

.logo {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin-bottom: 20px;
}

.logo-icon {
  font-size: 2.5rem;
}

.logo-text {
  font-size: 1.5rem;
  font-weight: bold;
  background: linear-gradient(135deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.register-title {
  font-size: 2rem;
  font-weight: 700;
  color: #333;
  margin-bottom: 10px;
}

.register-subtitle {
  color: #666;
  font-size: 1rem;
  line-height: 1.5;
}

.register-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  font-weight: 600;
  color: #333;
  font-size: 0.9rem;
}

.input-container {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 12px;
  width: 20px;
  height: 20px;
  color: #999;
  z-index: 1;
}

.form-input {
  width: 100%;
  padding: 12px 12px 12px 44px;
  border: 2px solid #e1e5e9;
  border-radius: 12px;
  font-size: 1rem;
  transition: all 0.3s ease;
  background: white;
}

.form-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-input:disabled {
  background: #f8f9fa;
  color: #999;
  cursor: not-allowed;
}

.password-toggle {
  position: absolute;
  right: 12px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  color: #999;
  z-index: 1;
}

.password-toggle svg {
  width: 20px;
  height: 20px;
}

.password-toggle:hover {
  color: #667eea;
}

.form-hint {
  font-size: 0.8rem;
  color: #666;
}

.form-error {
  font-size: 0.8rem;
  color: #e74c3c;
}

.gender-options {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.gender-option {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.gender-option input[type="radio"] {
  display: none;
}

.gender-label {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border: 2px solid #e1e5e9;
  border-radius: 8px;
  transition: all 0.3s ease;
  background: white;
}

.gender-option input[type="radio"]:checked + .gender-label {
  border-color: #667eea;
  background: rgba(102, 126, 234, 0.1);
  color: #667eea;
}

.gender-icon {
  width: 16px;
  height: 16px;
}

/* 电影偏好选择样式 */
.genre-selection {
  margin-top: 8px;
}

.genre-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 15px;
  margin-bottom: 15px;
}

.genre-option {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  border: 2px solid #d1d5db;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: #f9fafb;
  position: relative;
  color: #374151;
}

.genre-option:hover {
  border-color: #667eea;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
  background: #f3f4f6;
}

.genre-option.selected {
  border-color: #667eea;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.genre-option input {
  display: none;
}

.genre-name {
  font-weight: 500;
  font-size: 0.95rem;
}

.genre-hint {
  font-size: 0.85rem;
  color: #6b7280;
  text-align: center;
  margin-top: 12px;
  line-height: 1.4;
}

.error-message {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: rgba(231, 76, 60, 0.1);
  border: 1px solid rgba(231, 76, 60, 0.2);
  border-radius: 8px;
  color: #e74c3c;
  font-size: 0.9rem;
}

.error-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.register-button {
  width: 100%;
  padding: 14px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 10px;
}

.register-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3);
}

.register-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.loading-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.register-footer {
  text-align: center;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #e1e5e9;
}

.register-footer p {
  color: #666;
  margin: 0;
}

.login-link {
  color: #667eea;
  text-decoration: none;
  font-weight: 600;
  transition: color 0.3s ease;
}

.login-link:hover {
  color: #764ba2;
  text-decoration: underline;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .register-view {
    padding: 10px;
  }
  
  .register-card {
    padding: 30px 20px;
  }
  
  .register-title {
    font-size: 1.6rem;
  }
  
  .gender-options {
    flex-direction: column;
    gap: 10px;
  }
  
  .gender-label {
    justify-content: center;
  }

  .genre-grid {
    grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
    gap: 12px;
  }

  .genre-option {
    padding: 10px 12px;
    justify-content: center;
  }

  .genre-name {
    font-size: 0.9rem;
  }

  .genre-hint {
    font-size: 0.8rem;
    margin-top: 10px;
  }
}
</style>
