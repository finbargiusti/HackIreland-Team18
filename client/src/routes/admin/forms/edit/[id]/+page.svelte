<script lang="ts">
	import AdminPageTitle from '$lib/AdminPageTitle.svelte';
	import { firestore } from '$lib/firebase';
	import FormInputItem from '$lib/form/FormInputItem.svelte';
	import type { InputField } from '$lib/form/inputs.d.ts';
	import { doc, getDoc, setDoc } from 'firebase/firestore';
	import { page } from '$app/stores';

	const ref = doc(firestore, 'forms', $page.params.id);

	let loading = $state(true);
	let error = $state('');

	getDoc(ref)
		.then((doc) => {
			if (doc.exists()) {
				const data = doc.data() as { title: string; inputs: InputField[] };
				title = data.title as string;
				inputs = data.inputs as InputField[];
				loading = false;
			} else {
				error = 'No such document!';
			}
		})
		.catch((error) => {
			console.error('Error getting document:', error);
		});

	let title = $state('');
	let inputs: InputField[] = $state([]);

	// reactively save the form with setDoc when inputs change

	$effect(() => {
		if (!loading) {
			setDoc(ref, { inputs });
		}
	});
</script>

<AdminPageTitle>Editing {$page.params.id}</AdminPageTitle>

{#if error}<p>{error}</p>{/if}
{#if !loading}
	<input type="text" bind:value={title} placeholder="Title (click to change)" class="block min-w-0 grow py-1.5 pr-3 pl-1 text-gray-900 placeholder:text-gray-400 focus:outline-none text-5xl"  />
	<div>
		{#each inputs as _, index}
			<FormInputItem bind:input={inputs[index]} />
		{/each}
		<div class="flex flex-row justify-start">
			<button
				class="btn btn-primary"
				onclick={() =>
					(inputs = [...inputs, { description: '', data: { type: 'enum', values: [] } }])}
			>
				> Add Enum
			</button>
		</div>
	</div>
{/if}
