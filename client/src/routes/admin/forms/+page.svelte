<script lang="ts">
// Here we list all the forms.
import { firestore, auth } from '$lib/firebase';

import { collection, getDocs } from 'firebase/firestore';

import type { Form } from '$lib/form/inputs.d.ts';
import AdminPageTitle from '$lib/AdminPageTitle.svelte';
import { goto } from '$app/navigation';

let forms: {id: string, data: Form}[] = $state([]);

getDocs(collection(firestore, 'forms/' + auth.currentUser?.uid + '/forms')).then((querySnapshot) => {
	forms = querySnapshot.docs.map((doc) => ({
		id: doc.id,
		data: doc.data() as Form
	}));
});
</script>

<AdminPageTitle>Forms</AdminPageTitle>

{#if forms.length === 0}
	<p>No forms found.</p>
{/if}

{#each forms as { id, data }}
	<div class="flex flex-row gap-4 items-center">
		<p>{data.title}</p>
		<button class="btn" onclick={() => goto('/admin/forms/edit/' + id)}>Edit</button>
	</div>
{/each}
