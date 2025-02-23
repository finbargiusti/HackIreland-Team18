<script lang="ts">
	import { page } from '$app/state';
	import { doc, getDoc } from 'firebase/firestore';

	import { firestore } from '$lib/firebase';
	import { goto } from '$app/navigation';
	import ChatList from '$lib/ChatList.svelte';

	let { admin_id, form_id, session_id } = page.params;

	const ref = doc(firestore, `admin/${admin_id}/forms/${form_id}/sessions`, session_id);

	let conversation = $state([]);
	let date = $state('');
	let email = $state('');

	getDoc(ref)
		.then((doc) => {
			if (doc.exists()) {
				const data = doc.data();
				conversation = data.conversation;
				const date_obj = new Date(data.date);
				date = date_obj.toLocaleDateString();
				email = data.email;
			} else {
				console.log('No such document!');
				goto('/admin/404');
			}
		})
		.catch((error) => {
			console.error('Error getting document:', error);
		});
</script>

<h1>Session for {email} at {date}:</h1>

<ChatList
	chats={conversation.map(({ content, role }) => ({ user: role === 'user', data: content }))}
/>
