<script setup>
import { computed, onMounted, onBeforeUnmount, ref, watch } from 'vue';
import MarkdownIt from 'markdown-it';
import hljs from 'highlight.js';
import 'highlight.js/styles/github-dark.css';

const props = defineProps({
  content: { type: String, default: '' }
});

// 配置 Markdown 解析器
const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true,
  highlight: function (str, lang) {
    if (lang && hljs.getLanguage(lang)) {
      try {
        const codeId = Math.random().toString(36).substring(7);
        return `<pre class="hljs p-3 rounded-lg my-2 overflow-x-auto text-sm bg-[#0d1117] relative code-block-wrapper" data-code-id="${codeId}"><code data-code="${encodeURIComponent(str)}">${
          hljs.highlight(str, { language: lang, ignoreIllegals: true }).value
        }</code></pre>`;
      } catch (__) {}
    }
    return '';
  }
});

const renderedHtml = computed(() => md.render(props.content));
const containerRef = ref(null);

// 复制代码功能
const copyCode = async (codeText, buttonElement) => {
  try {
    await navigator.clipboard.writeText(codeText);
    const icon = buttonElement.querySelector('.copy-icon');
    if (icon) {
      icon.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>';
      setTimeout(() => {
        icon.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="14" height="14" x="8" y="8" rx="2" ry="2"/><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/></svg>';
      }, 2000);
    }
  } catch (err) {
    console.error('复制失败:', err);
  }
};

// 添加复制按钮到所有代码块
const addCopyButtons = () => {
  if (!containerRef.value) return;
  
  const codeBlocks = containerRef.value.querySelectorAll('pre.code-block-wrapper');
  codeBlocks.forEach((pre) => {
    if (pre.querySelector('.copy-button')) return;
    
    const codeElement = pre.querySelector('code[data-code]');
    if (!codeElement) return;
    
    const encodedCode = codeElement.getAttribute('data-code');
    const codeText = decodeURIComponent(encodedCode);
    
    const button = document.createElement('button');
    button.className = 'copy-button absolute top-2 right-2 p-1.5 rounded-md bg-gray-700 hover:bg-gray-600 text-gray-300 hover:text-white transition-colors opacity-0 group-hover:opacity-100';
    button.innerHTML = '<span class="copy-icon"><svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="14" height="14" x="8" y="8" rx="2" ry="2"/><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/></svg></span>';
    button.title = '复制代码';
    
    button.addEventListener('click', (e) => {
      e.preventDefault();
      copyCode(codeText, button);
    });
    
    pre.classList.add('group');
    pre.appendChild(button);
  });
};

onMounted(() => {
  addCopyButtons();
});

watch(() => props.content, () => {
  setTimeout(() => addCopyButtons(), 100);
});

onBeforeUnmount(() => {
  if (containerRef.value) {
    const buttons = containerRef.value.querySelectorAll('.copy-button');
    buttons.forEach(btn => btn.remove());
  }
});
</script>

<template>
  <div ref="containerRef" class="markdown-body prose prose-sm dark:prose-invert max-w-none" v-html="renderedHtml"></div>
</template>

<style scoped>
.markdown-body {
  color: inherit;
  font-size: 0.95rem;
  line-height: 1.6;
}

.markdown-body :deep(h1),
.markdown-body :deep(h2),
.markdown-body :deep(h3),
.markdown-body :deep(h4) {
  margin-top: 1.5em;
  margin-bottom: 0.75em;
  font-weight: 600;
}

.markdown-body :deep(p) {
  margin-bottom: 1em;
}

.markdown-body :deep(ul),
.markdown-body :deep(ol) {
  margin-bottom: 1em;
  padding-left: 1.5em;
}

.markdown-body :deep(li) {
  margin-bottom: 0.25em;
}

.markdown-body :deep(code) {
  background-color: rgba(175, 184, 193, 0.2);
  padding: 0.2em 0.4em;
  border-radius: 3px;
  font-size: 0.9em;
}

.markdown-body :deep(pre) {
  margin: 1em 0;
}

.markdown-body :deep(pre code) {
  background: none;
  padding: 0;
}

.markdown-body :deep(a) {
  color: #3b82f6;
  text-decoration: none;
}

.markdown-body :deep(a:hover) {
  text-decoration: underline;
}
</style>
