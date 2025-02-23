<script lang="ts">
	import type { User } from 'firebase/auth';
	import { auth, googleProvider, signInWithPopup } from './firebase.js';
	import { onMount } from 'svelte';

	let user: User | null = null;
	let error: string | null = null;

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

	onMount(() => {
		const unsubscribe = auth.onAuthStateChanged((authUser) => {
			user = authUser;
		});

		return () => unsubscribe();
	});

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
</script>

<ul class="mt-2">
	{#if user}
	<li>
		<h4 class="px-4 pb-2 text-sm font-bold text-red-300">
			{user.email}
		</h4>
	</li>
	{/if}

	<li>
		{#if user}
			<a
				href="#"
				on:click={handleLogout}
				class="block rounded px-4 py-2.5 text-[15px] text-black transition-all hover:bg-red-50 hover:text-red-600"
			>
				Log out
			</a>
		{:else}
			<a
				href="#"
				on:click={handleGoogleLogin}
				class="block rounded px-4 py-2.5 text-[15px] text-black transition-all hover:bg-red-50 hover:text-red-600"
			>
				Log in with google
			</a>
		{/if}
	</li>
</ul>
