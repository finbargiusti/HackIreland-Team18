<script lang="ts">
	// Here we list all the forms.
	import { firestore, auth } from '$lib/firebase';

	import { collection, getDocs, getDoc, updateDoc, doc, setDoc } from 'firebase/firestore';

	import type { Form } from '$lib/form/inputs.d.ts';
	import AdminPageTitle from '$lib/AdminPageTitle.svelte';
	import { goto } from '$app/navigation';
	import type { User } from 'firebase/auth';

	let forms: { id: string; data: Form }[] = $state([]);

	const getForms = (user: User | null) => {
		if (user === null) return;
		getDocs(collection(firestore, 'admin/' + user.uid + '/forms')).then((querySnapshot) => {
			forms = querySnapshot.docs.map((doc) => ({
				id: doc.id,
				data: doc.data() as Form
			}));
			linkState = forms.map(() => false);
			users = forms.map((f) => f.data.users ?? []);
			newUser = forms.map(() => '');
		});
	};

	const createShortLink = (url: string) => {
		const random = Math.random().toString(36).substring(7);
		const ref = doc(firestore, 'shorts/', random);
		setDoc(ref, { url: url }).catch((e) => {
			console.error(e);
		})
		return 's/' + random;
	};

	auth.onAuthStateChanged(getForms);
	
	const addPatient = (email: string, index: number) => {
		const ref = doc(firestore, 'admin/' + auth.currentUser?.uid + '/forms', forms[index].id);
		getDoc(ref).then((doc) => {
			console.assert(doc.exists());
			users[index].push(email);
			updateDoc(ref, { users: users[index] }).catch((e) => {
				console.error(e);
				users[index].pop();
			});
		});
	};

	let newUser = $state([] as string[]);
	let users: string[][] = $state([]);
	let linkState = $state([] as boolean[]);
</script>

<AdminPageTitle>Your Forms</AdminPageTitle>

<div class="flex flex-col items-stretch gap-4">
	{#if forms.length === 0}
		<p>No forms found.</p>
	{/if}

	{#each forms as { id, data }, index}
		<div class="box">
			<h2>{data.title}</h2>
			<h3 class="text-semibold pt-4 text-xl">Patients:</h3>
			<div
				class="flex max-h-100 min-w-full flex-col items-stretch overflow-x-scroll rounded-lg bg-white mb-4"
			>
				<div class="whitespace-nowrap">
					{#if users[index].length == 0}
						<p class="px-4 py-2 odd:bg-slate-200">No patients yet!</p>
					{/if}
					{#each users[index] as user}
						<p class="px-4 py-2 odd:bg-slate-200">
							{user}
						</p>
					{/each}
				</div>
				<input
					type="text"
					bind:value={newUser[index]}
					placeholder="Add patient email (enter)"
					class="w-full px-4 py-2 highlight-0 hover:outline-0 focus:outline-0"
					onkeydown={(e) => {
						if (e.key === 'Enter') {
							addPatient(newUser[index], index);
							newUser[index] = '';
						}
					}}
				/>
			</div>
			<div class="buttons">
				<a href="#" class="btn" onclick={() => goto('/admin/forms/edit/' + id)}>Edit</a>
				{#if linkState[index]}
					<input
						type="text"
						value={`${window.location.origin}/${createShortLink('/form/' +auth.currentUser!.uid + '/' +id)}`}
						class="clipboard-input" />
				{:else}
						<a
							href="#"
							onclick={() => {
								linkState[index] = true;
							}}
							class="btn"
						>
							Get form link
						</a>
				{/if}
			</div>
		</div>
	{/each}

	<button class="btn btn-primary" onclick={() => goto('/admin/forms/create')}
		>Create new form</button
	>
</div>
