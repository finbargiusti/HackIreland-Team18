<script lang="ts">
	import AdminPageTitle from '$lib/AdminPageTitle.svelte';
	import { firestore, auth } from '$lib/firebase';
	import FormInputItem from '$lib/form/FormInputItem.svelte';
	import { inputIssues, type InputField } from '$lib/form/inputs';
	import { doc, getDoc, updateDoc, deleteDoc } from 'firebase/firestore';
	import { page } from '$app/stores';
	import { onDestroy, onMount } from 'svelte';
	import { goto } from '$app/navigation';

	const ref = doc(firestore, 'admin/' + auth.currentUser?.uid + '/forms', $page.params.id);

	let loading = $state(true);
	let errors: string[] = $state([]);
	let title = $state('');
	let inputs: InputField[] = $state([]);

	let newUser = $state('')
	let users: string[] = $state([])

	getDoc(ref)
		.then((doc) => {
			if (doc.exists()) {
				const data = doc.data();
				title = data.title as string;
				inputs = data.inputs as InputField[];
				users = data.users as string[];
				loading = false;
			} else {
				errors.push('No such document!');
			}
		})
		.catch((error) => {
			console.error('Error getting document:', error);
		});

	// reactively save the form with setDoc when inputs change

	let saved = $state(false);

	const addPatient = (email: string) => {
		getDoc(ref).then((doc) => {
			console.assert(doc.exists())
			users.push(email);
			updateDoc(ref, {users});
		})
	}

	$effect(() => {
		// validate inputs
		let e = [];
		saved = false;

		e = inputs.reduce((acc, input, index) => {
			acc = [...acc, ...inputIssues(input, `Input ${index + 1}`)];
			return acc;
		}, [] as string[]);

		if (inputs.length === 0) {
			e = ['At least one input is required', ...e];
		}

		if (title === '') {
			e = ['Title cannot be empty', ...e];
		}

		if (!loading && e.length === 0) {
			updateDoc(ref, { title, inputs }).then(() => saved=true).catch((error) => {
				console.error('Error updating document:', error);
				e.push('Error updating document');
			});
		}

		errors = e;
	});

	const deleteSelf = async () => {
		if (!confirm('Are you sure you want to delete this form?')) return;
		await deleteDoc(ref);
		goto('/admin/forms');
	};

	function unload_watch(e: BeforeUnloadEvent) {
		if (!saved) {
			e.preventDefault();
			const msg = 'You have unsaved changes. Are you sure you want to leave?';
			e.returnValue = msg;
			return msg;
		}
	}

	onMount(() => {
		window.addEventListener('beforeunload', unload_watch);
	});

	onDestroy(() => {
		window.removeEventListener('beforeunload', unload_watch);
	});
</script>

{#if errors.length > 0}
	<h1 class="bold mb-2 ml-0 text-3xl text-yellow-500">Cannot save document:</h1>
	<ul class="list-disc">
		{#each errors as e}
			<li>{e}</li>
		{/each}
	</ul>
{/if}
{#if saved}
	<h1 class="happy">Synced!</h1>
{/if}
{#if !loading}
	<input
		type="text"
		bind:value={title}
		placeholder="Title (click to edit)"
		class="block w-full py-1.5 text-5xl text-gray-900 placeholder:text-gray-400 focus:outline-none"
	/>
	<div class="flex flex-col gap-4">
		{#each inputs as _, index}
			<div class="input-item-wrap">
				<h2 class="text-2xl">Input {index + 1}: {inputs[index].data.type}</h2>
				<FormInputItem bind:input={inputs[index]} />
				<button
					class="rounded bg-red-500 px-4 py-2 font-bold text-white hover:bg-red-700"
					onclick={() => {
						inputs = inputs.filter((_, i) => i !== index);
					}}>Delete</button
				>
			</div>
		{/each}
		<div class="flex flex-row justify-start gap-4">
			<button
				class="rounded bg-blue-500 px-4 py-2 font-bold text-white hover:bg-blue-700"
				onclick={() =>
					(inputs = [...inputs, { description: '', data: { type: 'choice', values: [] } }])}
			>
				Add Choice Input
			</button>
			<button
				class="rounded bg-blue-500 px-4 py-2 font-bold text-white hover:bg-blue-700"
				onclick={() => (inputs = [...inputs, { description: '', data: { type: 'number' } }])}
			>
				Add Numerical input
			</button>
		</div>
		<div class="flex flex-row justify-start gap-4">
			<button class="btn danger" onclick={deleteSelf}> Delete Form </button>
		</div>
		<h2>Users:</h2>
		<ul>
			{#each users as u}
			<li class="text-lg">
					{u}
			</li>
			{/each}
		</ul>
		<div class="flex flex-row justify-start gap-4">
			<input type="text" bind:value={newUser} placeholder="Add user (enter)"
				onkeydown={
				(e) => {
					if (e.key === 'Enter') {
						addPatient(newUser);
						newUser = ''
					}
				}
			}
			/>
		</div>
	</div>
{/if}

<style lang="css">
@import "tailwindcss";

.input-item-wrap {
	@apply flex flex-col items-stretch gap-2 px-2 py-2 border justify-stretch;
}

@keyframes happy {
	0% {
		opacity: 1;
	}
	80% {
		opacity: 1;
	}
	100% {
		opacity: 0;
	}
}

h1.happy {
  @apply text-green-500 bg-gray-100;
	animation: happy 2s forwards;
	position: absolute;
}
</style>
