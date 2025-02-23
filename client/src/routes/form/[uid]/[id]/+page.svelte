<script lang="ts">
	import { firestore, auth } from '$lib/firebase';
	import { doc, getDoc } from 'firebase/firestore';

	import { onMount } from 'svelte';
	import { page } from '$app/state';
	import { error } from '@sveltejs/kit';

	import ChatList from '$lib/ChatList.svelte';
	import AuthManager from '$lib/AuthManager.svelte';
	import { goto } from '$app/navigation';

	let chats: { user: boolean; data: string }[] = $state([]);

	const { id, uid } = page.params;

	const ref = doc(firestore, 'admin/' + uid + '/forms', id);

	let userMessage = $state('');
	let title = $state('');

	getDoc(ref)
		.then((doc) => {
			if (doc.exists()) {
				const data = doc.data() as { title: string };
				title = data.title as string;
			} else {
				throw error(404, 'No such document!');
			}
		})
		.catch((error) => {
			console.error('Error getting document:', error);
		});

	let sessionId = $state('');

	let server_url = $state('');

	const startSession = async () => {
		const response = await fetch(`${server_url}/start_session/${uid}/${id}`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({
				patient_id: auth.currentUser!.uid
			})
		});

		if (!response.ok) {
			error(403, 'Failed to start session');
		}

		let json = await response.json();
		sessionId = json.session_id;
		const question = json.bot_question;
		chats.push({
			user: false,
			data: question
		});
		canChat = true;
	};

	let canChat = $state(false);

	const getNextServerMessage = async (answer: string) => {
		const response = await fetch(`${server_url}/send_message/${uid}/${id}`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({
				patient_id: auth.currentUser!.uid,
				message: answer,
				session_id: sessionId
			})
		});
		if (!response.ok) {
			goto('/admin/404');
		}
		let json = await response.json();
		const question = json.bot_question;
		if (question) {
			chats.push({
				user: false,
				data: question
			});
			canChat = true;
		} else {
			chats.push({
				user: false,
				data: 'All done! Thank you for your time.'
			});
			canChat = false;
		}
	};

	let chatContainer: HTMLDivElement | null = $state(null);

	$effect(() => {
		let res = chats.slice(-1)[0];
		if (res) {
			chatContainer?.scrollTo({
				top: chatContainer.scrollHeight,
				behavior: 'smooth'
			});
		}
	});

	function submitMessage() {
		chats.push({
			user: true,
			data: userMessage
		});
		getNextServerMessage(userMessage);
		userMessage = '';
	}

	$effect(() => {
		if (server_url !== '') {
			startSession();
		}
	})

	onMount(async () => {
		chats = [];
		server_url = location.protocol + '//'+ location.host.split(':')[0] + ':8000';
	});
</script>

<div class="flex h-[calc(100vh-20px)] flex-col items-stretch">
	<div class="flex w-full flex-row items-center px-4">
		<h1 class="form-title">{title}</h1>
		<AuthManager />
	</div>
	<div class="grow overflow-y-auto" bind:this={chatContainer}>
		<ChatList bind:chats />
	</div>
	<div class="flex flex-row items-center justify-center gap-[-4]">
		<input
			type="text"
			class="chat-input"
			placeholder="Type a message..."
			disabled={!canChat}
			bind:value={userMessage}
			onkeydown={(e) => {
				if (e.key === 'Enter') {
					submitMessage();
				}
			}}
		/>
		<button class="submit-button"
			onclick={submitMessage}
			>⮐ </button>
	</div>
</div>
