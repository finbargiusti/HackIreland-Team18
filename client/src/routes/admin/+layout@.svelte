<script lang="ts">
	import '../../app.css';
	import AuthManager from '$lib/AuthManager.svelte';
	import {auth} from '$lib/firebase';
	import { onMount } from 'svelte';
	let { children } = $props();

	let currentPath = $state('');

	let pages = $derived([
		{
			name: 'Forms',
			href: '/admin/form',
			active: currentPath.startsWith('/admin/forms')
		},
		{
			name: 'View Results',
			href: '/admin/view',
			active: currentPath === '/admin/view'
		}
	]);

	onMount(() => {
		currentPath = window.location.pathname;
	});

	let loggedIn = $state(auth.currentUser !== null);

	auth.onAuthStateChanged((user) => {
		if (user) {
			loggedIn = true;
		} else {
			loggedIn = false;
		}
	});
</script>

<div class="min-h-full">
	<nav class="bg-gray-800">
		<div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
			<div class="flex h-16 items-center justify-between">
				<div class="flex items-center">
					<div class="shrink-0">
						<img
							class="size-8"
							src="https://tailwindui.com/plus-assets/img/logos/mark.svg?color=indigo&shade=500"
							alt="Your Company"
						/>
					</div>
					<div class="hidden md:block">
						<div class="ml-10 flex items-baseline space-x-4">
							<!-- Current: "bg-gray-900 text-white", Default: "text-gray-300 hover:bg-gray-700 hover:text-white" -->
							{#each pages as page}
								<a
									href={page.href}
									class={page.active
										? 'rounded-md bg-gray-900 px-3 py-2 text-sm font-medium text-white'
										: 'rounded-md px-3 py-2 text-sm font-medium text-gray-300 hover:bg-gray-700 hover:text-white'}
									>{page.name}</a
								>
							{/each}
							<!-- <a -->
							<!-- 	href="/admin/view" -->
							<!-- 	class="rounded-md px-3 py-2 text-sm font-medium text-gray-300 hover:bg-gray-700 hover:text-white" -->
							<!-- 	>View Results</a -->
							<!-- > -->
						</div>
					</div>
				</div>
				<div class="hidden md:block">
					<div class="ml-4 flex items-center md:ml-6">
						<!-- Profile dropdown -->
						<div class="relative ml-3">
							<AuthManager />
						</div>
					</div>
				</div>
				<div class="-mr-2 flex md:hidden">
					<!-- Mobile menu button -->
					<button
						type="button"
						class="relative inline-flex items-center justify-center rounded-md bg-gray-800 p-2 text-gray-400 hover:bg-gray-700 hover:text-white focus:ring-2 focus:ring-white focus:ring-offset-2 focus:ring-offset-gray-800 focus:outline-hidden"
						aria-controls="mobile-menu"
						aria-expanded="false"
					>
						<span class="absolute -inset-0.5"></span>
						<span class="sr-only">Open main menu</span>
						<!-- Menu open: "hidden", Menu closed: "block" -->
						<svg
							class="block size-6"
							fill="none"
							viewBox="0 0 24 24"
							stroke-width="1.5"
							stroke="currentColor"
							aria-hidden="true"
							data-slot="icon"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5"
							/>
						</svg>
						<!-- Menu open: "block", Menu closed: "hidden" -->
						<svg
							class="hidden size-6"
							fill="none"
							viewBox="0 0 24 24"
							stroke-width="1.5"
							stroke="currentColor"
							aria-hidden="true"
							data-slot="icon"
						>
							<path stroke-linecap="round" stroke-linejoin="round" d="M6 18 18 6M6 6l12 12" />
						</svg>
					</button>
				</div>
			</div>
		</div>
	</nav>

	<main>
		<div class="mx-auto max-w-7xl">
			<div class="bg-white shadow-sm px-4 py-6 sm:px-6 lg:px-8">
				{#if loggedIn}
					{@render children()}
				{:else}
					<h1 class="text-5xl">You are not logged in.</h1>
				{/if}
			</div>
		</div>
	</main>
</div>
