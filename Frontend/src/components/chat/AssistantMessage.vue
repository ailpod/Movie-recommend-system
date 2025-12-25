<script setup>
import { ref } from 'vue';
import MarkdownRenderer from './MarkdownRenderer.vue';

const props = defineProps({
  message: { type: Object, required: true }
});

const emit = defineEmits(['regenerate', 'like', 'dislike']);

const showCopySuccess = ref(false);

const copyContent = async () => {
  try {
    await navigator.clipboard.writeText(props.message.content);
    showCopySuccess.value = true;
    setTimeout(() => {
      showCopySuccess.value = false;
    }, 2000);
  } catch (err) {
    console.error('复制失败:', err);
  }
};

const handleRegenerate = () => {
  emit('regenerate');
};

const handleLike = () => {
  emit('like');
};

const handleDislike = () => {
  emit('dislike');
};
</script>

<template>
  <div class="assistant-message-wrapper">
    <!-- 消息主体 -->
    <div class="message-body">
      <!-- 名字 & 状态指示器 -->
      <div class="message-header">
        <span class="assistant-name">Agent</span>
        <span v-if="message.isStreaming" class="streaming-indicator"></span>
      </div>

      <!-- Markdown 内容 & 光标动画 -->
      <div class="message-content">
        <MarkdownRenderer :content="message.content" />
        
        <!-- 打字机光标 -->
        <span v-if="message.isStreaming" class="typing-cursor"></span>
      </div>

      <!-- 底部工具栏 -->
      <div class="message-toolbar">
        <button 
          @click="copyContent" 
          class="toolbar-btn" 
          :title="showCopySuccess ? '已复制' : '复制'"
        >
          <svg v-if="!showCopySuccess" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
          </svg>
          <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="20 6 9 17 4 12"></polyline>
          </svg>
        </button>
        <button 
          @click="handleRegenerate"
          :disabled="message.isStreaming"
          class="toolbar-btn" 
          title="重新生成"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21.5 2v6h-6M2.5 22v-6h6M2 11.5a10 10 0 0 1 18.8-4.3M22 12.5a10 10 0 0 1-18.8 4.2"></path>
          </svg>
        </button>
        <div class="toolbar-divider"></div>
        <button 
          @click="handleLike"
          class="toolbar-btn like-btn" 
          title="点赞"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M7 22V11M2 13v6c0 1.1.9 2 2 2h3m0-8l4-7c1.1 0 2 .9 2 2v4h7c1.1 0 2 .9 2 2 0 .5-.2 1-.5 1.3l-3.5 6c-.4.7-1.2 1.2-2 1.2H7"></path>
          </svg>
        </button>
        <button 
          @click="handleDislike"
          class="toolbar-btn dislike-btn" 
          title="踩"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M17 2v11m5-2v-6c0-1.1-.9-2-2-2h-3m0 8l-4 7c-1.1 0-2-.9-2-2v-4H4c-1.1 0-2-.9-2-2 0-.5.2-1 .5-1.3l3.5-6C6.4 3 7.2 2.5 8 2.5h9"></path>
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.assistant-message-wrapper {
  display: flex;
  margin-bottom: 1.5rem;
  width: 100%;
}

.assistant-message-wrapper:hover .message-toolbar {
  opacity: 1;
}

.message-body {
  flex: 1;
  max-width: 90%;
  min-width: 0;
}

.message-header {
  margin-bottom: 0.5rem;
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.5);
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.assistant-name {
  color: rgba(255, 255, 255, 0.5);
}

.streaming-indicator {
  width: 0.5rem;
  height: 0.5rem;
  border-radius: 50%;
  background: #10b981;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.message-content {
  width: 100%;
  overflow: hidden;
  position: relative;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(10px);
  border-radius: 1.25rem;
  border-top-left-radius: 0.25rem;
  padding: 1rem 1.25rem;
  word-break: break-word;
  overflow-wrap: break-word;
  color: rgba(255, 255, 255, 0.9);
}

.typing-cursor {
  display: inline-block;
  width: 0.375rem;
  height: 1rem;
  margin-left: 0.25rem;
  vertical-align: middle;
  background: rgba(255, 255, 255, 0.8);
  animation: blink 1s step-end infinite;
}

@keyframes blink {
  0%, 100% { 
    opacity: 1; 
  }
  50% { 
    opacity: 0; 
  }
}

.message-toolbar {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.5rem;
  opacity: 0;
  transition: opacity 0.2s;
}

.toolbar-btn {
  padding: 0.375rem;
  border-radius: 0.375rem;
  background: transparent;
  color: rgba(255, 255, 255, 0.4);
  border: none;
  cursor: pointer;
  font-size: 0.75rem;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.toolbar-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.7);
}

.toolbar-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.toolbar-btn svg {
  display: block;
}

.toolbar-divider {
  width: 1px;
  height: 0.875rem;
  background: rgba(255, 255, 255, 0.15);
  margin: 0 0.25rem;
}

.like-btn:hover {
  color: #10b981;
}

.dislike-btn:hover {
  color: #ef4444;
}
</style>