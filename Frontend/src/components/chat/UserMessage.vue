<script setup>
import { ref, nextTick } from 'vue';

const props = defineProps({
  message: { type: Object, required: true }
});

const emit = defineEmits(['edit']);

const isEditing = ref(false);
const editContent = ref('');
const showCopySuccess = ref(false);
const editTextareaRef = ref(null);

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

const startEdit = async () => {
  isEditing.value = true;
  editContent.value = props.message.content;
  await nextTick();
  editTextareaRef.value?.focus();
  autoResizeTextarea();
};

const autoResizeTextarea = () => {
  const textarea = editTextareaRef.value;
  if (!textarea) return;
  textarea.style.height = 'auto';
  textarea.style.height = textarea.scrollHeight + 'px';
};

const saveEdit = () => {
  if (editContent.value.trim()) {
    emit('edit', editContent.value.trim());
    isEditing.value = false;
  }
};

const cancelEdit = () => {
  isEditing.value = false;
  editContent.value = '';
};
</script>

<template>
  <div class="user-message-wrapper">
    <!-- 消息体 -->
    <div class="message-body">
      <!-- 名字 -->
      <div class="message-author">You</div>
      
      <!-- 气泡内容 -->
      <div v-if="!isEditing" class="message-bubble">
        {{ message.content }}
      </div>
      
      <!-- 编辑模式 -->
      <div v-else class="edit-container">
        <div class="edit-wrapper">
          <textarea
            ref="editTextareaRef"
            v-model="editContent"
            placeholder="在此输入消息"
            class="edit-textarea"
            @keydown.enter.ctrl="saveEdit"
            @keydown.esc="cancelEdit"
            @input="autoResizeTextarea"
          ></textarea>
          
          <!-- 按钮组 -->
          <div class="edit-buttons">
            <button @click="cancelEdit" class="edit-btn cancel-btn">取消</button>
            <button @click="saveEdit" class="edit-btn save-btn">保存</button>
          </div>
        </div>
      </div>
      
      <!-- 工具栏 -->
      <div class="message-toolbar">
        <button 
          v-if="!isEditing"
          @click="startEdit"
          class="toolbar-btn"
          title="编辑"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z"></path>
          </svg>
        </button>
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
      </div>
    </div>
  </div>
</template>
<style scoped>
.user-message-wrapper {
  display: flex;
  flex-direction: row-reverse;
  margin-bottom: 1.5rem;
  width: 100%;
}

.user-message-wrapper:hover .message-toolbar {
  opacity: 1;
}

.message-body {
  flex: 1;
  max-width: 85%;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.message-author {
  margin-bottom: 0.5rem;
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.5);
  font-weight: 500;
}

.message-bubble {
  position: relative;
  padding: 1rem 1.25rem;
  background: rgba(255, 255, 255, 0.12);
  color: rgba(255, 255, 255, 0.95);
  border-radius: 1.25rem;
  border-top-right-radius: 0.25rem;
  white-space: pre-wrap;
  word-break: break-word;
  overflow-wrap: break-word;
  backdrop-filter: blur(10px);
}

.edit-container {
  position: relative;
  padding: 0.75rem 1rem;
  background: rgba(255, 255, 255, 0.12);
  color: white;
  border-radius: 1.25rem;
  border-top-right-radius: 0.25rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  width: 100%;
  backdrop-filter: blur(10px);
}

.edit-wrapper {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  width: 100%;
}

.edit-textarea {
  width: 100%;
  background: rgba(255, 255, 255, 0.08);
  color: white;
  border: none;
  outline: none;
  resize: none;
  font-size: 0.875rem;
  border-radius: 0.375rem;
  padding: 0.5rem;
  min-height: 28px;
}

.edit-textarea::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

.edit-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  padding-top: 0.25rem;
  border-top: 1px solid rgba(255, 255, 255, 0.15);
}

.edit-btn {
  padding: 0.25rem 0.75rem;
  font-size: 0.75rem;
  border-radius: 0.375rem;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
}

.cancel-btn {
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.8);
}

.cancel-btn:hover {
  background: rgba(255, 255, 255, 0.15);
}

.save-btn {
  background: rgba(255, 255, 255, 0.9);
  color: #1a1a1a;
  font-weight: 600;
}

.save-btn:hover {
  background: white;
}

.message-toolbar {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  margin-top: 0.5rem;
  opacity: 0;
  transition: opacity 0.2s;
}

.toolbar-btn {
  padding: 0.375rem;
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.4);
  background: transparent;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
  border-radius: 0.375rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.toolbar-btn:hover {
  color: rgba(255, 255, 255, 0.7);
  background: rgba(255, 255, 255, 0.1);
}

.toolbar-btn svg {
  display: block;
}
</style>