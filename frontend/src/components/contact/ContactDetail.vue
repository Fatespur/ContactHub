<script setup>
import { computed } from 'vue'
import AppIcon from '@/components/common/AppIcon.vue'
import ContactAvatar from './ContactAvatar.vue'
import GroupTag from './GroupTag.vue'
import StarToggle from './StarToggle.vue'
import DetailSkeleton from './DetailSkeleton.vue'

const props = defineProps({
  contact: { type: Object, default: null },
  drawer: { type: Boolean, default: false },
  loading: { type: Boolean, default: false }
})

const emit = defineEmits(['close', 'edit', 'remove', 'toggle-favorite'])

const phones = computed(() => props.contact?.phones || [])
const emails = computed(() => props.contact?.emails || [])
const socials = computed(() => props.contact?.social_accounts || [])
const addresses = computed(() => props.contact?.addresses || [])
</script>

<template>
  <aside
    class="card detail-card"
    :class="{ 'is-drawer': drawer }"
    :tabindex="drawer ? -1 : undefined"
    :role="drawer ? 'dialog' : undefined"
    :aria-modal="drawer ? 'true' : undefined"
    :aria-label="drawer ? '联系人详情' : undefined"
  >
    <button
      class="detail-close"
      type="button"
      title="关闭详情"
      aria-label="关闭详情"
      @click="emit('close')"
    >
      <AppIcon name="close" :size="15" />
    </button>

    <div class="detail-scroll">
      <DetailSkeleton v-if="loading" :drawer="drawer" />

      <template v-else-if="contact">
        <div class="detail-head">
          <ContactAvatar :name="contact.name" :size="56" tone="detail" />
          <div class="detail-head-main">
            <div class="detail-name-row">
              <h3 class="detail-name">{{ contact.name }}</h3>
              <StarToggle
                :active="contact.is_favorite"
                :size="15"
                @toggle="emit('toggle-favorite', contact)"
              />
            </div>
            <GroupTag v-if="contact.group" :text="contact.group" />
          </div>
        </div>

        <section class="section">
          <h4 class="section-title">
            <AppIcon name="user" :size="16" />
            基本信息
          </h4>
          <div class="kv-row">
            <span class="k">分组</span>
            <span class="v">
              <GroupTag v-if="contact.group" :text="contact.group" />
              <span v-else class="empty-text">—</span>
            </span>
          </div>
          <div class="kv-row">
            <span class="k">备注</span>
            <span class="v">{{ contact.notes || '—' }}</span>
          </div>
        </section>

        <div class="divider" />

        <section class="section">
          <h4 class="section-title">
            <AppIcon name="phone" :size="16" />
            电话号码 <span class="count">({{ phones.length }})</span>
          </h4>
          <template v-if="phones.length">
            <div v-for="(phone, index) in phones" :key="`phone-${index}`" class="detail-item">
              <span class="dot" :class="{ 'is-primary': phone.is_primary }" />
              <span>
                <span class="label">{{ phone.label || '手机' }}：</span>{{ phone.number }}
                <span v-if="phone.is_primary" class="primary-flag">（主要）</span>
              </span>
            </div>
          </template>
          <div v-else class="detail-empty">—</div>
        </section>

        <section class="section">
          <h4 class="section-title">
            <AppIcon name="mail" :size="16" />
            邮箱地址 <span class="count">({{ emails.length }})</span>
          </h4>
          <template v-if="emails.length">
            <div v-for="(email, index) in emails" :key="`email-${index}`" class="detail-item">
              <AppIcon name="mail" :size="15" />
              <span>{{ email.email }}</span>
            </div>
          </template>
          <div v-else class="detail-empty">—</div>
        </section>

        <section class="section">
          <h4 class="section-title">
            <AppIcon name="chat" :size="16" />
            社交账号 <span class="count">({{ socials.length }})</span>
          </h4>
          <template v-if="socials.length">
            <div v-for="(social, index) in socials" :key="`social-${index}`" class="detail-item">
              <AppIcon name="chat" :size="15" />
              <span><span class="label">{{ social.platform }}：</span>{{ social.account }}</span>
            </div>
          </template>
          <div v-else class="detail-empty">—</div>
        </section>

        <section class="section">
          <h4 class="section-title">
            <AppIcon name="pin" :size="16" />
            联系地址 <span class="count">({{ addresses.length }})</span>
          </h4>
          <template v-if="addresses.length">
            <div v-for="(address, index) in addresses" :key="`address-${index}`" class="detail-item">
              <AppIcon name="pin" :size="15" />
              <span>{{ address.address }}</span>
            </div>
          </template>
          <div v-else class="detail-empty">—</div>
        </section>
      </template>

      <div v-else class="detail-blank">
        <AppIcon name="user" :size="30" />
        <strong>未选择联系人</strong>
        <p>点击左侧任意一行查看详细信息</p>
      </div>
    </div>

    <div class="detail-actions">
      <el-button :disabled="!contact || loading" @click="emit('edit', contact)">
        <AppIcon name="edit" :size="15" />编辑
      </el-button>
      <el-button :disabled="!contact || loading" @click="emit('remove', contact)">
        <AppIcon name="trash" :size="15" />删除
      </el-button>
    </div>
  </aside>
</template>

<style scoped>
.detail-card {
  width: var(--detail-width);
  flex: none;
  display: flex;
  flex-direction: column;
  padding: 32px 20px 20px;
  position: relative;
  min-height: 0;
}

.detail-card.is-drawer {
  position: absolute;
  top: 12px;
  right: 12px;
  bottom: 12px;
  width: 360px;
  height: auto;
  box-shadow: 0 18px 48px rgba(24, 38, 54, 0.22);
}

.detail-card.is-drawer:focus {
  outline: none;
}

.detail-close {
  position: absolute;
  top: 18px;
  right: 18px;
  width: 26px;
  height: 26px;
  border: 0;
  border-radius: 7px;
  background: transparent;
  color: #a6b1be;
  display: grid;
  place-items: center;
  transition: background 0.16s, color 0.16s;
}

.detail-close :deep(.app-icon) {
  color: currentColor;
}

.detail-close:hover {
  background: #f2f5f8;
  color: var(--color-ink-3);
}

.detail-scroll {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  overscroll-behavior: contain;
  margin-right: -6px;
  padding-right: 6px;
}

.detail-scroll::-webkit-scrollbar {
  width: 5px;
}

.detail-scroll::-webkit-scrollbar-thumb {
  background: #e6ebf1;
  border-radius: 3px;
}

.detail-head {
  display: flex;
  align-items: center;
  gap: 16px;
}

.detail-head-main {
  min-width: 0;
}

.detail-name-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.detail-name {
  margin: 0;
  font-size: 19px;
  font-weight: 600;
  line-height: 26px;
  color: var(--color-ink);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.detail-head .group-tag {
  margin-top: 6px;
}

.section {
  margin-top: 26px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 14px;
  font-size: 14px;
  font-weight: 600;
  color: #2a3441;
}

.section-title :deep(.app-icon) {
  color: #4a5a6b;
}

.section-title .count {
  font-size: 12.5px;
  font-weight: 400;
  color: #9aa6b4;
}

.kv-row {
  display: flex;
  align-items: center;
  gap: 10px;
  min-height: 24px;
  font-size: 13px;
}

.kv-row .k {
  color: #8b97a5;
  width: 38px;
  flex: none;
}

.kv-row .v {
  color: var(--color-ink-2);
  min-width: 0;
  overflow-wrap: anywhere;
}

.empty-text {
  color: #aab4c0;
}

.divider {
  height: 1px;
  background: var(--color-line);
  margin: 26px 0 0;
}

.detail-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 6px 0;
  font-size: 13px;
  line-height: 20px;
  color: var(--color-ink-2);
  overflow-wrap: anywhere;
}

.detail-item :deep(.app-icon) {
  margin-top: 2px;
  color: #8b98a8;
}

.detail-item .dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #c6d0da;
  margin: 7px 0 0 3px;
  flex: none;
}

.detail-item .dot.is-primary {
  background: var(--color-primary);
}

.detail-item .label {
  color: #8b97a5;
}

.detail-item .primary-flag {
  color: #9aa6b4;
  font-size: 12px;
}

.detail-empty {
  font-size: 13px;
  color: #aab4c0;
  padding: 2px 0;
}

.detail-blank {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 120px 0;
  color: var(--color-ink-4);
  font-size: 13px;
}

.detail-blank :deep(.app-icon) {
  color: #c3ccd6;
  margin-bottom: 4px;
}

.detail-blank strong {
  font-size: 14px;
  font-weight: 500;
  color: var(--color-ink-2);
}

.detail-blank p {
  margin: 0;
}

.detail-actions {
  flex: none;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-top: 18px;
  padding-top: 16px;
  border-top: 1px solid var(--color-line);
}

.detail-actions :deep(.el-button) {
  width: 100%;
  margin-left: 0;
  padding: 0 10px;
}
</style>
