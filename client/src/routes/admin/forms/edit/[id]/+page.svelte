<script lang="ts">
	import AdminPageTitle from '$lib/AdminPageTitle.svelte';
	import { firestore, auth } from '$lib/firebase';
	import FormInputItem from '$lib/form/FormInputItem.svelte';
	import {inputIssues, type InputField } from '$lib/form/inputs';
	import { doc, getDoc, setDoc, deleteDoc } from 'firebase/firestore';
	import { page } from '$app/stores';
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';

	const ref = doc(firestore, 'forms/' + auth.currentUser?.uid + '/forms', $page.params.id);

	let loading = $state(true);
	let errors: string[] = $state([]);
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
				errors.push('No such document!');
			}
		})
		.catch((error) => {
			console.error('Error getting document:', error);
		});

	// reactively save the form with setDoc when inputs change

	let saved = $state(false)

	$effect(() => {
		// validate inputs
		let e = [];
		saved = false;

		e = inputs.reduce((acc, input, index) => {
			acc = [...acc, ...inputIssues(input, `Input ${index+1}`)];
			return acc;
		}, [] as string[]);

		if (inputs.length === 0) {
			e = ['At least one input is required', ...e];
		}

		if (title === '') {
			e = ['Title cannot be empty', ...e];
		}

		if (!loading && e.length === 0) {
			setDoc(ref, { title, inputs });
			saved=true;
		}

		errors = e;
	});

	const deleteSelf = async () => {
		if (!confirm('Are you sure you want to delete this form?')) return;
		await deleteDoc(ref);
		goto('/admin/forms');
	};

	onMount(() => {
		window.addEventListener('beforeunload', function (e) {
			if (!saved) {
				e.preventDefault();
				const msg = "You have unsaved changes. Are you sure you want to leave?";
				e.returnValue = msg;
				return msg;
			}
		});
	});
</script>

{#if errors.length > 0}
	<h1 class="text-yellow-500 text-3xl bold ml-0 mb-2">Cannot save document:</h1>
	<ul class="list-disc">
	{#each errors as e}
		<li>{e}</li>
	{/each}
	</ul>
{/if}
{#if saved}
	<h1 class="text-green-500 text-3xl bold ml-0 mb-2">Saved!</h1>
{/if}
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
				<h2 class="text-2xl">Input {index + 1}: {inputs[index].data.type}</h2>
				<FormInputItem bind:input={inputs[index]} />
				<button class="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded" onclick={ () => {
					inputs = inputs.filter((_, i) => i !== index);
				}}>Delete</button>
			</div>
		{/each}
		<div class="flex flex-row justify-start gap-4">
			<button
				class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
				onclick={() =>
					(inputs = [...inputs, { description: '', data: { type: 'choice', values: [] } }])}
			>
				Add Choice Input
			</button>
			<button
				class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
				onclick={() =>
					(inputs = [...inputs, { description: '', data: { type: 'number' } }])}
			>
				Add Numerical input
			</button>
		</div>
		<div class="flex flex-row justify-start gap-4">
			<button
				class="btn danger"
				onclick={deleteSelf}
			>
				Delete Form
			</button>
		</div>
	</div>
{/if}
