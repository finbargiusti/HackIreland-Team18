<script lang="ts">
	import { auth } from '$lib/firebase';

	import AuthManager from '$lib/AuthManager.svelte';
	import { onMount } from 'svelte';

	const { children } = $props();

	let loggedIn: boolean | null = $state(null);

	onMount(() => {
		auth.onAuthStateChanged((user) => {
			console.log(user);
			loggedIn = user !== null;
		});
	});
</script>

{#if loggedIn !== null}
	{#if loggedIn}
		{@render children()}
	{:else}
		<div class="flex h-screen w-screen flex-row items-center justify-center gap-4">
			<p>Please log in:</p>
			<AuthManager />
		</div>
	{/if}
{/if}
