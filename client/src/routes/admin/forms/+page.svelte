<script lang="ts">
// Here we list all the forms.
import { firestore, auth } from '$lib/firebase';

import { collection, getDocs } from 'firebase/firestore';

import type { Form } from '$lib/form/inputs.d.ts';
import AdminPageTitle from '$lib/AdminPageTitle.svelte';
import { goto } from '$app/navigation';
import type { User } from 'firebase/auth';

let forms: {id: string, data: Form}[] = $state([])

const getForms = (user: User|null) => {
	if (user === null) return;
	getDocs(collection(firestore, 'admin/' + user.uid + '/forms')).then((querySnapshot) => {
		forms = querySnapshot.docs.map((doc) => ({
			id: doc.id,
			data: doc.data() as Form
		}));
	});
}

auth.onAuthStateChanged(getForms)

</script>

<AdminPageTitle>Forms</AdminPageTitle>

<div class="flex flex-col gap-4 items-start">
	{#if forms.length === 0}
		<p>No forms found.</p>
	{/if}

	{#each forms as { id, data }}
		<div class="flex flex-row gap-2 items-center px-2 py-3 br-3 border">
			<h2>{data.title}</h2>
			<button class="btn" onclick={() => goto('/admin/forms/edit/' + id)}>Edit</button>
			<a href={`/form/${auth.currentUser!.uid}/${id}`} class="btn">Form link</a>
		</div>
	{/each}

	<button class="btn btn-primary" onclick={() => goto('/admin/forms/create')}>Create new form</button>
</div>
