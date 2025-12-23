<template>
  <div
    class="rating-stars"
    :class="[variant]"
    @click.stop
    @mousedown.stop
    @touchstart.stop
  >
    <div class="label" v-if="showLabel">我的评分</div>
    <div class="stars" :aria-label="`为电影打分：当前 ${displayValue}/10`">
      <button
        v-for="n in 10"
        :key="n"
        type="button"
        class="star-btn"
        :class="{ active: n <= hoverValue || (!hoverValue && n <= currentValue) }"
        @mouseenter="hoverValue = n"
        @mouseleave="hoverValue = 0"
        @focus="hoverValue = n"
        @blur="hoverValue = 0"
        @click="handleRate(n)"
        :title="`${n}/10`"
        :aria-pressed="n <= currentValue"
      >
        ★
      </button>
    </div>
    <div class="value" v-if="showValue">{{ displayValue }}/10</div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import ratingApi from '@/services/ratingApi'

const props = defineProps({
  movieId: { type: [String, Number], required: true },
  initial: { type: Number, default: 0 },
  variant: { type: String, default: 'compact' }, // 'compact' | 'default'
  showLabel: { type: Boolean, default: false },
  showValue: { type: Boolean, default: true }
})

const emit = defineEmits(['rated', 'error'])

const authStore = useAuthStore()
const currentValue = ref(0)
const hoverValue = ref(0)
const hasExisting = ref(false)

const displayValue = computed(() => (hoverValue.value || currentValue.value))

onMounted(async () => {
  currentValue.value = normalize(props.initial)
  if (!authStore.isAuthenticated) return
  try {
    const res = await ratingApi.getMyRating(props.movieId)
    // 兼容不同字段名：rate / rating / value
    const val = res?.rate ?? res?.rating ?? res?.value ?? 0
    currentValue.value = normalize(val)
    hasExisting.value = !!val
  } catch (e) {
    // 404 表示没有评分，不提示
    if (e?.status && e.status !== 404) {
      emit('error', e)
    }
  }
})

watch(() => props.initial, (v) => {
  if (!hasExisting.value) currentValue.value = normalize(v)
})

function normalize(v) {
  const n = Number(v) || 0
  if (n < 0) return 0
  if (n > 10) return 10
  return Math.round(n)
}

async function handleRate(n) {
  if (!authStore.isAuthenticated) {
    // 轻提示：需要登录
    window.alert('请先登录后再评分')
    return
  }
  try {
    const value = normalize(n)
    // 若已有评分，调用更新；否则创建
    if (hasExisting.value) {
      await ratingApi.updateRating(props.movieId, value)
    } else {
      await ratingApi.rateMovie(props.movieId, value)
      hasExisting.value = true
    }
    currentValue.value = value
    emit('rated', { movieId: props.movieId, value })
  } catch (e) {
    console.error('评分失败:', e)
    emit('error', e)
  }
}
</script>

<style scoped>
.rating-stars {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: rgba(255, 255, 255, 0.9);
}
.rating-stars .label {
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.7);
}
.stars {
  display: inline-flex;
  gap: 2px;
}
.star-btn {
  appearance: none;
  background: transparent;
  border: none;
  padding: 0;
  margin: 0;
  cursor: pointer;
  color: rgba(255, 255, 255, 0.3);
  transition: transform 0.1s ease, color 0.2s ease;
  line-height: 1;
}
.star-btn:hover {
  transform: scale(1.1);
}
.star-btn.active {
  color: #ffd700;
}
.value {
  font-size: 0.85rem;
  color: #ffd700;
  min-width: 36px;
}
/* 尺寸变体 */
.default .star-btn { font-size: 18px; }
.compact .star-btn { font-size: 14px; }
.default .value { font-size: 0.9rem; }
.compact .value { font-size: 0.8rem; }
</style>
