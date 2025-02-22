<script lang="ts">
	import { goto } from '$app/navigation';
  import {page} from '$app/stores';  
  import {auth, firestore} from '$lib/firebase';
	import type { Form } from '$lib/form/inputs';
	import { error } from '@sveltejs/kit';
	import type { User } from 'firebase/auth';

  import {getDoc, doc} from 'firebase/firestore'

  let {id} = $page.params;

  let data: Form | null = $state(null)

  const getForm = (user: User|null) => {
    // we wouldn't be here without user
    getDoc(doc(firestore, `admin/${user!.uid}/forms`, id)).then(doc => {
      if (doc.exists()) {
        data = doc.data() as Form;
      } else {
        goto('/admin/404')
      }
    }).catch((res) => {
      if (res.status==404) goto('/admin/404')
      else console.error(res.body);
    })
  }

  auth.onAuthStateChanged(getForm)
</script>

