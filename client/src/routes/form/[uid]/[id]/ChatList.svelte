<script lang="ts">
  type Props = {
    chats: { id: string; system: boolean; data: string }[];
  }

  let { chats = $bindable() } = $props() as Props;
</script>

<div class="chat-contain">
  {#if chats.length === 0}
    <p>No messages yet!</p>
  {/if}

  {#each chats as { id, system, data }}
    <div class={['chat', system ? 'system' : 'user']}>
      <span class="id">{id}: </span>
      <span>{data}</span>
    </div>
  {/each}
</div>

<style lang="css">
@import "tailwindcss";  

.chat-contain {
  @apply grow flex flex-col items-stretch w-full;
}

.chat {
  @apply py-2 px-4 bg-gray-200 text-lg;
}
.chat.system {
  @apply bg-gray-300;
}
.chat>span.id {
  @apply font-bold inline-block;
}
</style>
