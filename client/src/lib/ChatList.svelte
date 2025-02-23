<script lang="ts">
  type Props = {
    chats: { user: boolean; data: string }[];
  }

  let { chats = $bindable() }: Props = $props() ;
</script>

<div class="chat-contain">
  {#if chats.length === 0}
    <p>No messages yet!</p>
  {/if}

  {#each chats as { user, data }}
    <div class={['chat', user ? 'user' : 'system']}>
      <span>{data}</span>
    </div>
  {/each}
</div>
