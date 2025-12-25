<script setup>
import UserMessage from './UserMessage.vue';
import AssistantMessage from './AssistantMessage.vue';

const props = defineProps({
  message: { type: Object, required: true },
  messageIndex: { type: Number, required: true }
});

const emit = defineEmits(['edit-user-message', 'regenerate-response', 'like', 'dislike']);

const handleEditUser = (newContent) => {
  emit('edit-user-message', props.messageIndex, newContent);
};

const handleRegenerate = () => {
  emit('regenerate-response', props.messageIndex);
};

const handleLike = () => {
  emit('like', props.messageIndex);
};

const handleDislike = () => {
  emit('dislike', props.messageIndex);
};
</script>

<template>
  <div class="message-item">
    <UserMessage 
      v-if="message.role === 'user'" 
      :message="message"
      @edit="handleEditUser"
    />
    <AssistantMessage 
      v-else 
      :message="message"
      @regenerate="handleRegenerate"
      @like="handleLike"
      @dislike="handleDislike"
    />
  </div>
</template>

<style scoped>
.message-item {
  width: 100%;
}
</style>
