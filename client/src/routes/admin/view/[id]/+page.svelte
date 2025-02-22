<script lang="ts">
  import {page} from '$app/stores';  
  import {auth} from '$lib/firebase';

  let {id} = $page.params;

  let uid = $state(auth.currentUser!.uid);
</script>

