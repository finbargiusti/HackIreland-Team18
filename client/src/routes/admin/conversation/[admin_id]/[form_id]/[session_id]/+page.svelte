<script lang="ts">
  import {page} from '$app/state';
  import {doc, getDoc} from 'firebase/firestore';

  import {firestore} from '$lib/firebase';
	import { goto } from '$app/navigation';

  let {admin_id, form_id, session_id} = page.params;

  const ref = doc(firestore, `admin/${admin_id}/forms/${form_id}/sessions`, session_id);

  let conversation = $state([]);
  let date = $state('');
  let email = $state('');

  getDoc(ref).then((doc) => {
    if (doc.exists()) {
      const data = doc.data();
      conversation = data.conversation;
      const date_obj = new Date(data.date);
      date = date_obj.toLocaleDateString();
      email = data.email;
    } else {
      console.log("No such document!");
      goto('/admin/404');
    }
  }).catch((error) => {
    console.error('Error getting document:', error);
  });
</script>

<h1>Session for {email} at {date}:</h1>

<table class="mt-6">
  <thead class="bg-teal-600 text-white">
    <tr>
      <td>From</td>
      <td>Message</td>
    </tr>
  </thead>
  <tbody>
    {#each conversation as {role, content}}
      <tr class={['', 'chat', role=='user' ? 'user' : 'system']}>
        <td class="px-4">{role}</td>
        <td>{content}</td>
      </tr>
    {/each}
</table>
