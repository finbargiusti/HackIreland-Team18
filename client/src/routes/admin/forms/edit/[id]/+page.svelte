<script lang="ts">
	import AdminPageTitle from '$lib/AdminPageTitle.svelte';
	import { firestore, auth } from '$lib/firebase';
	import FormInputItem from '$lib/form/FormInputItem.svelte';
	import type { InputField } from '$lib/form/inputs.d.ts';
	import { doc, getDoc, setDoc } from 'firebase/firestore';
	import { page } from '$app/stores';

	const ref = doc(firestore, 'forms/' + auth.currentUser?.uid + '/forms', $page.params.id);

	let loading = $state(true);
	let error = $state('');
	let title = $state('');
	let inputs: InputField[] = $state([]);

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

	// reactively save the form with setDoc when inputs change

	$effect(() => {
		console.log(title);
		if (!loading) {
			setDoc(ref, { title, inputs });
		}
	});
</script>

<AdminPageTitle>Editing {$page.params.id}</AdminPageTitle>

{#if error}<p>{error}</p>{/if}
{#if !loading}
	<input
		type="text"
		bind:value={title}
		placeholder="Title (click to edit)"
		class="block shrink-0 py-1.5 text-5xl text-gray-900 placeholder:text-gray-400 focus:outline-none"
	/>
	<div class="flex flex-col gap-4">
		{#each inputs as _, index}
			<div class="flex flex-col gap-2 items-start">
				<FormInputItem bind:input={inputs[index]} />
				<button class="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded" onclick={ () => {
					inputs = inputs.filter((_, i) => i !== index);
				}}>Delete</button>
			</div>
		{/each}
		<div class="flex flex-row justify-start">
			<button
				class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
				onclick={() =>
					(inputs = [...inputs, { description: '', data: { type: 'enum', values: [] } }])}
			>
				Add Enum
			</button>
		</div>
	</div>
{/if}
