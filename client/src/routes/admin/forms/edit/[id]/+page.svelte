<script lang="ts">
	import { firestore, auth } from '$lib/firebase';
	import FormInputItem from '$lib/form/FormInputItem.svelte';
	import { inputIssues, type InputField } from '$lib/form/inputs';
	import { doc, getDoc, updateDoc, deleteDoc } from 'firebase/firestore';
	import debounce from 'debounce';

	import { page } from '$app/state';
	import { goto } from '$app/navigation';

	const ref = doc(firestore, 'admin/' + auth.currentUser?.uid + '/forms', page.params.id);

	let loading = $state(true);
	let errors: string[] = $state([]);
	let title = $state('');
	let inputs: InputField[] = $state([]);

	let newUser = $state('');
	let users: string[] = $state([]);

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

	let saved = $state(false);

	const setSaved = debounce(
		() => {
			saved = true;
		},
		200,
		{ immediate: true }
	);

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
			updateDoc(ref, { title, inputs })
				.then(setSaved)
				.catch((error) => {
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
		e.preventDefault();
		const msg = 'You have unsaved changes. Are you sure you want to leave?';
		e.returnValue = msg;
		return msg;
	}

	let windowDiv: HTMLDivElement | null = $state(null);

	const scrollToBottom = () => {
		const parent = windowDiv?.parentElement;
		setTimeout(() => parent?.scrollTo({
			top: parent?.scrollHeight,
			behavior: 'smooth'
			}), 0);
	};
</script>

<window:beforeunload onbeforeunload={saved ? null : unload_watch}></window:beforeunload>

{#if errors.length > 0}
	<div class="box warn">
		<h1 class="warn">Incomplete items:</h1>
		<ol class="list-inside list-decimal">
			{#each errors as e}
				<li>{e}</li>
			{/each}
		</ol>
	</div>
{:else}
	<div class={['box', saved ? 'happy' : 'invisible', 'absolute', 'w-100']}>
		<h1 class="happy">Synced!</h1>
	</div>
{/if}
{#if !loading}
	<input
		type="text"
		bind:value={title}
		placeholder="Title (click to edit)"
		class="mb-8 block inline w-full py-1.5 text-center text-5xl text-gray-900 placeholder:text-gray-400 focus:outline-none"
	/>
	<div class="mt-4 mb-4 flex flex-row justify-stretch gap-4" bind:this={windowDiv}>
		<a
			class="btn grow"
			onclick={() => {
				inputs = [...inputs, { description: '', label: '', data: { type: 'choice', values: [] } }];
				scrollToBottom();
			}}
		>
			Add Choice Input
		</a>
		<a
			class="btn grow"
			onclick={() =>
				(inputs = [...inputs, { description: '', label: '', data: { type: 'number' } }])}
		>
			Add Numerical input
		</a>
		<a
			class="btn grow"
			onclick={() =>
				(inputs = [...inputs, { description: '', label: '', data: { type: 'string' } }])}
		>
			Add String input
		</a>
	</div>
	<div class="mb-4 flex w-full flex-row justify-stretch gap-4">
		<a class="btn danger w-full text-center" onclick={deleteSelf}> Delete Form </a>
	</div>
	<div class="flex flex-col items-stretch gap-4">
		{#each inputs as _, index}
			<div class="box">
				<h2 class="text-2xl">Input {index + 1}: {inputs[index].data.type}</h2>
				<FormInputItem bind:input={inputs[index]} />
				<button
					class="mt-6 w-full rounded bg-red-500 px-4 py-2 font-bold text-white hover:bg-red-700"
					onclick={() => {
						inputs = inputs.filter((_, i) => i !== index);
					}}>Delete</button
				>
			</div>
		{/each}
	</div>
{/if}

<style lang="css">
	@import 'tailwindcss';

	.input-item-wrap {
		@apply flex flex-col items-stretch justify-stretch gap-2 rounded-md border border-gray-400 px-2 py-2;
	}
</style>
