<template>
  <svg class="icon-sprite" aria-hidden="true">
    <defs>
      <symbol id="icon-users" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
        <path d="M16 19v-1.4a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4V19" />
        <circle cx="9" cy="7.2" r="3.2" />
        <path d="M16.8 4.3a3.2 3.2 0 0 1 0 5.9" />
        <path d="M21.5 19v-1.4a4 4 0 0 0-3-3.8" />
      </symbol>
      <symbol id="icon-star" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round">
        <path d="M12 3.8l2.55 5.2 5.7.83-4.12 4.02.97 5.68L12 16.85l-5.1 2.68.97-5.68L3.75 9.83l5.7-.83z" />
      </symbol>
      <symbol id="icon-tag" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
        <path d="M20.4 13.6l-6.8 6.8a2 2 0 0 1-2.83 0l-6.8-6.8A2 2 0 0 1 3.4 12V5a1.6 1.6 0 0 1 1.6-1.6h7a2 2 0 0 1 1.4.6l7 7a2 2 0 0 1 0 2.6z" />
        <circle cx="8.2" cy="8.2" r="1.3" />
      </symbol>
      <symbol id="icon-settings" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="3" />
        <path d="M19.1 14.6a1.6 1.6 0 0 0 .32 1.77l.06.06a1.9 1.9 0 1 1-2.69 2.69l-.06-.06a1.6 1.6 0 0 0-1.77-.32 1.6 1.6 0 0 0-.97 1.47V20a1.9 1.9 0 1 1-3.8 0v-.1a1.6 1.6 0 0 0-1.05-1.47 1.6 1.6 0 0 0-1.77.32l-.06.06a1.9 1.9 0 1 1-2.69-2.69l.06-.06a1.6 1.6 0 0 0 .32-1.77 1.6 1.6 0 0 0-1.47-.97H4a1.9 1.9 0 1 1 0-3.8h.1a1.6 1.6 0 0 0 1.47-1.05 1.6 1.6 0 0 0-.32-1.77l-.06-.06a1.9 1.9 0 1 1 2.69-2.69l.06.06a1.6 1.6 0 0 0 1.77.32H9.8a1.6 1.6 0 0 0 .97-1.47V4a1.9 1.9 0 1 1 3.8 0v.1a1.6 1.6 0 0 0 .97 1.47 1.6 1.6 0 0 0 1.77-.32l.06-.06a1.9 1.9 0 1 1 2.69 2.69l-.06.06a1.6 1.6 0 0 0-.32 1.77v.1a1.6 1.6 0 0 0 1.47.97H20a1.9 1.9 0 1 1 0 3.8h-.1a1.6 1.6 0 0 0-1.47.97z" />
      </symbol>
      <symbol id="icon-search" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round">
        <circle cx="11" cy="11" r="6.4" />
        <path d="M20 20l-4.2-4.2" />
      </symbol>
      <symbol id="icon-upload" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">
        <path d="M12 15.5V4.5" />
        <path d="M7.6 8.9L12 4.5l4.4 4.4" />
        <path d="M4.5 15v3.2a2 2 0 0 0 2 2h11a2 2 0 0 0 2-2V15" />
      </symbol>
      <symbol id="icon-download" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">
        <path d="M12 4.5v11" />
        <path d="M7.6 11.1L12 15.5l4.4-4.4" />
        <path d="M4.5 15v3.2a2 2 0 0 0 2 2h11a2 2 0 0 0 2-2V15" />
      </symbol>
      <symbol id="icon-plus" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round">
        <path d="M12 5v14" />
        <path d="M5 12h14" />
      </symbol>
      <symbol id="icon-close" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round">
        <path d="M6.5 6.5l11 11" />
        <path d="M17.5 6.5l-11 11" />
      </symbol>
      <symbol id="icon-more" viewBox="0 0 24 24" fill="currentColor">
        <circle cx="5" cy="12" r="1.6" />
        <circle cx="12" cy="12" r="1.6" />
        <circle cx="19" cy="12" r="1.6" />
      </symbol>
      <symbol id="icon-edit" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
        <path d="M4.5 19.5h4l10-10a2.12 2.12 0 0 0-3-3l-10 10z" />
        <path d="M13.6 7.4l3 3" />
      </symbol>
      <symbol id="icon-trash" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
        <path d="M4.5 6.8h15" />
        <path d="M9.2 6.8V4.9a1.4 1.4 0 0 1 1.4-1.4h2.8a1.4 1.4 0 0 1 1.4 1.4v1.9" />
        <path d="M6.6 6.8l.8 12a1.8 1.8 0 0 0 1.8 1.7h5.6a1.8 1.8 0 0 0 1.8-1.7l.8-12" />
      </symbol>
      <symbol id="icon-phone" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
        <path d="M20.3 16.9v2.2a1.6 1.6 0 0 1-1.75 1.6 15.6 15.6 0 0 1-6.8-2.42 15.4 15.4 0 0 1-4.75-4.75A15.6 15.6 0 0 1 4.58 6.7 1.6 1.6 0 0 1 6.17 4.9h2.2a1.6 1.6 0 0 1 1.6 1.38c.1.78.29 1.55.55 2.28a1.6 1.6 0 0 1-.36 1.7l-.93.93a12.7 12.7 0 0 0 4.76 4.76l.93-.93a1.6 1.6 0 0 1 1.7-.36c.73.26 1.5.45 2.28.55a1.6 1.6 0 0 1 1.38 1.63z" />
      </symbol>
      <symbol id="icon-mail" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
        <rect x="3.2" y="5.2" width="17.6" height="13.6" rx="2.2" />
        <path d="M4.2 7.2l7.8 5.6 7.8-5.6" />
      </symbol>
      <symbol id="icon-chat" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
        <path d="M20.6 11.8a8.2 8.2 0 0 1-8.4 8.1 8.6 8.6 0 0 1-3.4-.66L4 20.5l1.3-4.1a8.1 8.1 0 0 1-1.1-4.2A8.2 8.2 0 0 1 12.6 4a8.2 8.2 0 0 1 8 7.8z" />
      </symbol>
      <symbol id="icon-pin" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
        <path d="M12 21s7-6.1 7-11a7 7 0 1 0-14 0c0 4.9 7 11 7 11z" />
        <circle cx="12" cy="10" r="2.6" />
      </symbol>
      <symbol id="icon-user" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="7.6" r="3.6" />
        <path d="M4.8 20.4v-1.5a5.4 5.4 0 0 1 5.4-5.4h3.6a5.4 5.4 0 0 1 5.4 5.4v1.5" />
      </symbol>
      <symbol id="icon-chevron-down" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round">
        <path d="M6 9.5l6 6 6-6" />
      </symbol>
      <symbol id="icon-chevron-up" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round">
        <path d="M6 14.5l6-6 6 6" />
      </symbol>
      <symbol id="icon-chevron-left" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round">
        <path d="M14.5 6l-6 6 6 6" />
      </symbol>
      <symbol id="icon-chevron-right" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round">
        <path d="M9.5 6l6 6-6 6" />
      </symbol>
      <symbol id="icon-sort" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
        <path d="M8 9.5l4-4 4 4" />
        <path d="M8 14.5l4 4 4-4" />
      </symbol>
      <symbol id="icon-check" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round">
        <path d="M5 12.5l4.6 4.5L19 6.8" />
      </symbol>
      <symbol id="icon-info" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round">
        <circle cx="12" cy="12" r="8.5" />
        <path d="M12 11.2v5" />
        <circle cx="12" cy="8" r="0.9" fill="currentColor" stroke="none" />
      </symbol>
      <symbol id="icon-inbox" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
        <path d="M3 13.6h4.2l1.4 2.4h6.8l1.4-2.4H21" />
        <path d="M5.6 5.4h12.8a2 2 0 0 1 1.93 1.47L21 13.6v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4l.67-6.73A2 2 0 0 1 5.6 5.4z" />
      </symbol>
      <symbol id="icon-alert" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="8.5" />
        <path d="M12 7.4v5" />
        <circle cx="12" cy="16.2" r="0.9" fill="currentColor" stroke="none" />
      </symbol>
      <symbol id="icon-refresh" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">
        <path d="M20 11a8 8 0 1 0-2.6 6.1" />
        <path d="M20 5v6h-6" />
      </symbol>
      <symbol id="icon-check-circle" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="8.5" />
        <path d="M8.2 12.2l2.6 2.6 5-5.2" />
      </symbol>
      <symbol id="icon-file" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
        <path d="M13.5 3.5H7a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V9z" />
        <path d="M13.5 3.5V9H19" />
      </symbol>
    </defs>
  </svg>
</template>

<style scoped>
.icon-sprite {
  position: absolute;
  width: 0;
  height: 0;
  overflow: hidden;
}
</style>
