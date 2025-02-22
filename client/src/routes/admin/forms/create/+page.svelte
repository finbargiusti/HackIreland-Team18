<script lang="ts">
  import {goto} from '$app/navigation';
	import { firestore, auth } from '$lib/firebase';

  import {collection, addDoc} from 'firebase/firestore';

  const create = async () => {
    const ref = await addDoc(collection(firestore, 'admin/'+ auth.currentUser!.uid + '/forms'),
	{ title: "", inputs: [] }
    )
    goto('/admin/forms/edit/' + ref.id);
  }

  create()
</script>
