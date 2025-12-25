<script setup>
import { ref, nextTick, onMounted, watch } from 'vue';

const props = defineProps({
  isGenerating: { type: Boolean, default: false },
  disabled: { type: Boolean, default: false }
});

const emit = defineEmits(['send', 'stop']);

const prompt = ref('');
const textareaRef = ref(null);
const maxRows = 8;

// 自适应高度
const autoResize = () => {
  const textarea = textareaRef.value;
  if (!textarea) return;

  textarea.style.height = 'auto';
  
  const maxHeight = 24 * maxRows;
  const newHeight = Math.min(textarea.scrollHeight, maxHeight);
  
  textarea.style.height = `${newHeight}px`;
  textarea.style.overflowY = textarea.scrollHeight > maxHeight ? 'auto' : 'hidden';
};

// 发送消息处理
const handleSend = () => {
  const text = prompt.value.trim();
  
  if (!text || props.isGenerating) return;

  emit('send', { text });
  
  prompt.value = '';
  
  nextTick(() => {
    autoResize();
  });
};

// 停止生成
const handleStop = () => {
  emit('stop');
};

// 监听输入变化
watch(prompt, () => {
  nextTick(autoResize);
});

onMounted(() => {
  autoResize();
});

// 处理 Enter 键
const handleKeyDown = (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    handleSend();
  }
};
</script>

<template>
  <div class="input-area-container">
    <div class="input-area-inner">
      <div class="input-box">
        <!-- 输入框 -->
        <textarea
          ref="textareaRef"
          v-model="prompt"
          @keydown="handleKeyDown"
          :disabled="disabled || isGenerating"
          placeholder="输入你的问题... (Enter 发送, Shift+Enter 换行)"
          class="input-textarea"
          rows="1"
        ></textarea>

        <!-- 发送/停止按钮 -->
        <button
          v-if="!isGenerating"
          @click="handleSend"
          :disabled="!prompt.trim() || disabled"
          class="send-button"
          title="发送"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="22" y1="2" x2="11" y2="13"></line>
            <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
          </svg>
        </button>
        
        <button
          v-else
          @click="handleStop"
          class="stop-button"
          title="停止"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
            <rect x="6" y="6" width="12" height="12" rx="2"></rect>
          </svg>
        </button>
      </div>
      
      <!-- 提示文字 -->
      <div class="hint-text">
        电影助手可以帮你推荐电影、回答问题，但可能会产生不准确的信息
      </div>
    </div>
  </div>
</template>

<style scoped>
.input-area-container {
  width: 100%;
  border-top: 1px solid rgba(255, 255, 255, 0.2);
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  padding: 1rem;
}

.input-area-inner {
  max-width: 900px;
  margin: 0 auto;
}

.input-box {
  position: relative;
  display: flex;
  align-items: flex-end;
  gap: 0.5rem;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 1rem;
  padding: 0.5rem;
  border: 2px solid rgba(255, 255, 255, 0.2);
  transition: border-color 0.3s;
}

.input-box:focus-within {
  border-color: rgba(255, 255, 255, 0.4);
}

.input-textarea {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  resize: none;
  color: white;
  font-size: 0.875rem;
  padding: 0.5rem;
  max-height: 192px;
  line-height: 1.5;
}

.input-textarea::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.input-textarea:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.send-button,
.stop-button {
  flex-shrink: 0;
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 0.75rem;
  border: none;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s;
}

.send-button {
  background: #3b82f6;
}

.send-button:hover:not(:disabled) {
  background: #2563eb;
  transform: scale(1.05);
}

.send-button:disabled {
  background: rgba(255, 255, 255, 0.2);
  cursor: not-allowed;
  opacity: 0.5;
}

.stop-button {
  background: #ef4444;
}

.stop-button:hover {
  background: #dc2626;
  transform: scale(1.05);
}

.hint-text {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.5);
  margin-top: 0.5rem;
  text-align: center;
}

@media (max-width: 768px) {
  .input-area-container {
    padding: 0.75rem;
  }
}
</style>