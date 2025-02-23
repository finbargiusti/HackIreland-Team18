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

<meta:head>
	<title>ClinaTrack Admin Panel</title>
</meta:head>

<div class="align-stretch flex min-h-100  flex-row">
	<nav>
		<h3 class="">ClinaTrack</h3>
		<h4 class="">Admin Panel</h4>
		{#each pages as page}
			<a href={page.href} class={page.active ? 'nav-link-active' : 'nav-link'}>{page.name}</a>
		{/each}

		<div class="mt-4">
			<h6 class="subtitle">Account</h6>
			<AuthManager />
		</div>
	</nav>
	<div class="flex flex-row justify-center w-full overflow-x-scroll">
		<main class="max-w-300">
			{#if loggedIn !== null}
				{#if loggedIn}
					{@render children()}
				{:else}
					<h1 class="text-5xl">You are not logged in.</h1>
				{/if}
			{/if}
		</main>
	</div>
</div>
