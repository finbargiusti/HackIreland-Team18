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
	<li>
		{#if user}
			<span class="email">
				{user.email}
			</span>
			<a
				href="#"
				on:click={handleLogout}
				class="nav-link"
			>
				Log out
			</a>
		{:else}
			<a
				href="#"
				on:click={handleGoogleLogin}
				class="nav-link"
			>
				Log in with google
			</a>
		{/if}
	</li>
</ul>
