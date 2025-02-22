<script lang="ts">
	import AdminPageTitle from '$lib/AdminPageTitle.svelte';
  import {goto} from '$app/navigation';
	import { firestore } from '$lib/firebase';

  import {doc, setDoc} from 'firebase/firestore';

  let name = $state('');

  const create = () => {
    const ref = doc(firestore, 'forms', name);
    setDoc(ref, { title: "", inputs: [] });
    goto('/admin/forms/edit/' + name);
  }
</script>

<AdminPageTitle>Create a new document:</AdminPageTitle>

<input type="text" bind:value={name} placeholder="Name" />

<button class="btn btn-primary" onclick={create}>Create</button>
