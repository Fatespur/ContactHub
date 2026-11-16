<script setup>
import { isMockMode } from '@/api/contacts'
import { IMPORT_TEMPLATE_NAME, IMPORT_TEMPLATE_URL } from '@/utils/excel'
</script>

<template>
  <div class="card settings-page">
    <h2>系统设置</h2>
    <p class="subtitle">数据源、导入模板与快捷键说明，均为只读信息。</p>

    <section class="settings-section">
      <h3>数据源</h3>
      <div class="setting-row">
        <span class="label">当前模式</span>
        <span class="value">{{ isMockMode ? 'Mock 演示数据' : '真实后端接口' }}</span>
      </div>
      <div class="setting-row">
        <span class="label">接口前缀</span>
        <span class="value">/api/v1（Vite 代理 → http://127.0.0.1:5000）</span>
      </div>
      <div class="setting-row">
        <span class="label">切换方式</span>
        <span class="value">在 <code>frontend/.env.local</code> 设置 <code>VITE_USE_MOCK=false</code> 后重启开发服务</span>
      </div>
    </section>

    <section class="settings-section">
      <h3>工具</h3>
      <div class="setting-row">
        <span class="label">导入模板</span>
        <span class="value">
          <a class="link" :href="IMPORT_TEMPLATE_URL" :download="IMPORT_TEMPLATE_NAME">
            下载 8 列 Excel 模板
          </a>
          <span class="hint">（含填写说明页）</span>
        </span>
      </div>
      <div class="setting-row is-stacked">
        <span class="label">快捷键</span>
        <span class="value shortcut-list">
          <span class="shortcut"><kbd>Ctrl / ⌘ K</kbd> 聚焦搜索</span>
          <span class="shortcut"><kbd>Esc</kbd> 关闭详情抽屉 / 弹窗</span>
          <span class="shortcut"><kbd>Enter</kbd> 打开当前行详情</span>
        </span>
      </div>
    </section>

    <section class="settings-section">
      <h3>关于</h3>
      <div class="setting-row">
        <span class="label">版本</span>
        <span class="value">v0.4.0（除手机端外完成）</span>
      </div>
      <div class="setting-row">
        <span class="label">技术栈</span>
        <span class="value">Vue 3 · Element Plus · Vite · Axios</span>
      </div>
      <div class="setting-row">
        <span class="label">接口契约</span>
        <span class="value"><code>docs/API.md</code></span>
      </div>
    </section>

    <p class="about">EE308FZ-AddressBook · 通讯录管理系统</p>
  </div>
</template>

<style scoped>
.settings-page {
  flex: 1;
  min-width: 0;
  padding: 32px;
  overflow-y: auto;
}

h2 {
  margin: 0;
  font-size: 25px;
  font-weight: 600;
  color: var(--color-ink);
}

.subtitle {
  margin: 8px 0 4px;
  font-size: 13px;
  color: var(--color-ink-3);
}

.settings-section {
  max-width: 820px;
  margin-top: 26px;
  padding-top: 18px;
  border-top: 1px solid var(--color-line);
}

.settings-section:first-of-type {
  border-top: 0;
}

.settings-section h3 {
  margin: 0 0 8px;
  font-size: 14px;
  font-weight: 600;
  color: #2a3441;
}

.setting-row {
  display: flex;
  align-items: center;
  gap: 24px;
  padding: 10px 0;
  font-size: 13px;
}

.setting-row.is-stacked {
  align-items: flex-start;
}

.setting-row .label {
  width: 92px;
  flex: none;
  color: var(--color-ink-3);
}

.setting-row .value {
  color: var(--color-ink-2);
  line-height: 20px;
}

.setting-row .hint {
  color: var(--color-ink-4);
  font-size: 12px;
}

.link {
  color: var(--color-primary-strong);
  font-weight: 500;
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}

.shortcut-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.shortcut {
  color: var(--color-ink-2);
}

kbd {
  display: inline-block;
  min-width: 24px;
  margin-right: 6px;
  padding: 1px 6px;
  border: 1px solid #e1e7ee;
  border-bottom-width: 2px;
  border-radius: 5px;
  background: #fafbfd;
  color: #55657a;
  font-family: inherit;
  font-size: 11.5px;
  line-height: 16px;
  text-align: center;
}

code {
  padding: 1px 5px;
  border-radius: 4px;
  background: #f4f7fa;
  color: #506176;
  font-size: 12px;
}

.about {
  margin-top: 32px;
  font-size: 12px;
  color: var(--color-ink-4);
}

@media (max-width: 1023px) {
  .settings-page {
    padding: 20px;
  }

  .setting-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }

  .setting-row .label {
    width: auto;
  }
}
</style>
