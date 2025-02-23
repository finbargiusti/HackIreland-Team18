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
      date = data.date.toString();
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

<table>
  <thead>
    <tr>
      <td>From</td>
      <td>Message</td>
    </tr>
  </thead>
  <tbody>
    {#each conversation as {role, content}}
      <tr>
        <td>{role}</td>
        <td>{content}</td>
      </tr>
    {/each}
</table>
