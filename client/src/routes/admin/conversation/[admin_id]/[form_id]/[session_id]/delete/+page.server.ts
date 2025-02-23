import {firestore} from '$lib/firebase';
import {deleteDoc, doc, getDoc, updateDoc, } from 'firebase/firestore';
import type {PageServerLoad} from './$types';
import { error, redirect } from '@sveltejs/kit';
import type { Result } from '$lib/form/inputs';

export const load: PageServerLoad = async ({params}) => {
  const {admin_id, form_id, session_id} = params;
  const ref = doc(firestore, `admin/${admin_id}/forms/${form_id}/sessions/${session_id}`);
  const form_ref = doc(firestore, `admin/${admin_id}/forms/${form_id}`);
  const formDoc = (await getDoc(form_ref))
  if (!formDoc.exists()) {
    error(404)
  }
  let results = formDoc.data().results;
  results=results.filter((result: Result)=>result.session_id!==session_id);
  updateDoc(form_ref, {results})
  await deleteDoc(ref);
  redirect(308, `/admin/view/${form_id}`);
};
