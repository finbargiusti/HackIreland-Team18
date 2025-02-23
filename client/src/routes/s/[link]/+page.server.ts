import type { PageServerLoad } from './$types'

import {firestore} from '$lib/firebase'
import {doc, getDoc} from 'firebase/firestore'
import { error, redirect } from '@sveltejs/kit'

export const load: PageServerLoad = async ({params}): Promise<void> => {
  const ref = doc(firestore, 'shorts/', params.link)
  const docSnap = await getDoc(ref)

  if (docSnap.exists()) {
    const url = docSnap.data().url
    redirect(308, url)
  } else {
    error(404, 'Page not found')
  }
}
