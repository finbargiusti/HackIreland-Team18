<script lang="ts">
	import { firestore, auth } from '$lib/firebase';
	import { doc, getDoc } from 'firebase/firestore';

	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { error } from '@sveltejs/kit';

	import ChatList from './ChatList.svelte';
	import AuthManager from '$lib/AuthManager.svelte';

	let chats: { id: string; system: boolean; data: string }[] = $state([]);

	const { id, uid } = $page.params;

	const ref = doc(firestore, 'admin/' + uid + '/forms', id);

	let title = $state('');

	getDoc(ref).then((doc) => {
		if (doc.exists()) {
			const data = doc.data() as { title: string  };
			title = data.title as string;
		} else {
			throw error(404, 'No such document!');
		}
	}).catch((error) => {
		console.error('Error getting document:', error);
	});


	const getNextServerMessage = async () => {
		const response = {
			id: 'server',
			system: true,
			data: 'Hello from the server!'
		};
		return response;
	};

	onMount(() => {
		chats = [];
		getNextServerMessage().then((response) => {
			chats = [...chats, response];
		});
	});
</script>

<div class="flex h-full flex-col items-stretch">
	<div class="flex w-full flex-row items-center px-4">
		<h1 class="form-title">{title}</h1>
		<AuthManager />
	</div>
	<ChatList bind:chats />
	<input type="text" class="chat-input" placeholder="Type a message..." />
</div>

<style lang="css">
	@import 'tailwindcss';

	.form-title {
		@apply text-3xl font-bold text-slate-800 py-3 px-4 grow;
	}
	
	.chat-input {
		@apply w-full bg-gray-200 px-4 py-4 text-lg;
	}
</style>
