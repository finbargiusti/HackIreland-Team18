<script lang="ts">
	import '../../app.css';
	import AuthManager from '$lib/AuthManager.svelte';
	import { auth } from '$lib/firebase';
	let { children } = $props();
	import { page } from '$app/state';

	let pages = $derived([
		{
			name: 'Forms',
			href: '/admin/forms',
			active: page.url.pathname.startsWith('/admin/forms')
		},
		{
			name: 'View Results',
			href: '/admin/view',
			active: page.url.pathname.startsWith('/admin/view')
		}
	]);

	let loggedIn: boolean | null = $state(null);

	auth.onAuthStateChanged((user) => {
		if (user) {
			loggedIn = true;
		} else {
			loggedIn = false;
		}
	});
</script>

<div class="flex min-w-100 min-h-100 flex-row align-stretch">
	<nav class="h-screen min-w-[240px] overflow-auto bg-white px-4 py-6 font-[sans-serif] shadow-lg">
		<h3 class="px-4 pb-2 text-2xl font-bold text-red-800">ClinaTrack</h3>
		<h4 class="px-4 pb-4 text-base font-bold text-red-700">Admin Panel</h4>
		{#each pages as page}
			<a
				href={page.href}
				class={page.active
					? 'mb-2 block rounded bg-red-50 px-4 py-2.5 text-[15px] text-red-600 transition-all '
					: 'mb-2 block rounded px-4 py-2.5 text-[15px] text-black transition-all hover:bg-red-50 hover:text-red-600'}
				>{page.name}</a
			>
		{/each}

		<div class="mt-4">
			<h6 class="px-4 text-sm font-bold text-red-600">Account</h6>
			<AuthManager />
		</div>
	</nav>
	<main class="grow bg-white px-4 py-6 shadow-sm sm:px-6 lg:px-8 h-screen overflow-scroll">
		{#if loggedIn !== null}
			{#if loggedIn}
				{@render children()}
			{:else}
				<h1 class="text-5xl">You are not logged in.</h1>
			{/if}
		{/if}
	</main>
</div>
