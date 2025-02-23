<script lang="ts">
	import AdminPageTitle from '$lib/AdminPageTitle.svelte';
	import {auth, firestore} from '$lib/firebase'
	import type { Form } from '$lib/form/inputs';

	import {getDocs, collection} from 'firebase/firestore'

	let forms: {id: string, data: Form}[] = $state([])

	const getForms = () =>
		getDocs(collection(firestore, 'admin/' + auth.currentUser?.uid + '/forms')).then((querySnapshot) => {
			forms = querySnapshot.docs.map((doc) => ({
				id: doc.id,
				data: doc.data() as Form
			}));
		});

	auth.onAuthStateChanged(getForms)
</script>

<AdminPageTitle>View Form Results</AdminPageTitle>

{#each forms as f}
	<div class="box">
		<h2>{f.data.title}</h2>
		<div class="buttons">
			<a class="btn" href={`/admin/view/${f.id}`} >View Results</a>
		</div>
	</div>
{/each}


