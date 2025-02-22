<script lang="ts">
	import type { User } from 'firebase/auth';
	import ClickOutside from 'svelte-click-outside';
	import { auth, googleProvider, signInWithPopup } from './firebase.js';
	import { onMount } from 'svelte';

	let user: User | null = null;
	let error: string | null = null;

	// Handle Google Sign-In
	const handleGoogleLogin = async () => {
		try {
			const result = await signInWithPopup(auth, googleProvider);
			user = result.user;
			error = null;
		} catch (err: any) {
			error = err.message.toString();
			console.error('Error during Google login:', err);
		}
	};

	// Check if user is already logged in
	onMount(() => {
		const unsubscribe = auth.onAuthStateChanged((authUser) => {
			user = authUser;
		});

		return () => unsubscribe();
	});

	// Log out the user
	const handleLogout = async () => {
		try {
			await auth.signOut();
			user = null;
			error = null;
		} catch (err: any) {
			error = err.message;
			console.error('Error during logout:', err);
		}
	};

	let dropdownVisible = false;
</script>

<ClickOutside
	on:clickoutside={() => {
		if (dropdownVisible) {
			dropdownVisible = false;
		}
	}}
>
	<div>
		<button
			type="button"
			class="relative flex max-w-xs items-center rounded-full bg-white text-sm focus:ring-2 focus:ring-white focus:ring-offset-2 focus:ring-offset-gray-800 focus:outline-hidden"
			id="user-menu-button"
			aria-expanded={dropdownVisible}
			aria-haspopup="true"
			on:click={() => (dropdownVisible = !dropdownVisible)}
		>
			<span class="absolute -inset-1.5"></span>
			<span class="cursor-pointer font-medium text-slate-800 py-2 px-2">
				{user ? `Logged in as ${user.displayName}` : 'Not logged in'}
			</span>
		</button>
	</div>

	{#if dropdownVisible}
		<div
			class="absolute z-10 mt-2 w-48 origin-top-right rounded-md bg-white py-1 shadow-lg ring-1 ring-black/5 focus:outline-hidden"
			role="menu"
			aria-orientation="vertical"
			aria-labelledby="user-menu-button"
			tabindex="-1"
		>
			{#if user}
				<button
					on:click={handleLogout}
					class="block px-4 py-2 text-sm text-gray-700"
					role="menuitem"
					tabindex="-1"
					id="user-menu-item-2">Sign out</button
				>
			{:else}
				<button
					on:click={handleGoogleLogin}
					class="block px-4 py-2 text-sm text-gray-700"
					role="menuitem"
					tabindex="-1"
					id="user-menu-item-0">Log in with Google</button
				>
			{/if}
		</div>
	{/if}
</ClickOutside>
