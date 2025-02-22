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

	let userMessage = $state('');
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

	let sessionId = $state('')

	const server_url = import.meta.env.VITE_SERVER_URL

	const startSession = async () => {
		const response = await fetch(`${import.meta.env.VITE_SERVER_URL}/start_session/${uid}/${id}/${auth.currentUser!.uid}`, {
			method: 'POST'
		});

		if (!response.ok) {
			error(403, 'Failed to start session');
		}

		let json = await response.json();
		sessionId = json.sessionId;
		const question = json.question;
		chats.push(
			{
				id: 'server',
				system: true,
				data: question
			}
		);
	}

	const getNextServerMessage = async (answer: string) => {
		const response = await fetch(`${server_url}/next_message/${uid}/${id}/${sessionId}`, {
			method: 'GET',
			body: JSON.stringify({ answer }),
		});
		if (!response.ok) {
			error(403, 'Failed to get next message');
		}
		let json = await response.json();
		chats.push(
			{
				id: 'server',
				system: true,
				data: json.message
			}
		);
	};

	onMount(async () => {
		chats = [];
		startSession();
	});
</script>

<div class="flex h-full flex-col items-stretch">
	<div class="flex w-full flex-row items-center px-4">
		<h1 class="form-title">{title}</h1>
		<AuthManager />
	</div>
	<ChatList bind:chats />
	<input type="text" class="chat-input" placeholder="Type a message..." 
	disabled={chats[chats.length - 1]?.id !== 'server'}
	bind:value={userMessage}
	onkeydown={(e) => {
		if (e.key === 'Enter') {
			chats.push(
				{
					id: 'user',
					system: false,
					data: userMessage
				}
			);
			getNextServerMessage(userMessage);
			userMessage=''
		}
	}}
/>
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
