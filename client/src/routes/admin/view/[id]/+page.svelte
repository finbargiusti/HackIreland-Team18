<script lang="ts">
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import { auth, firestore } from '$lib/firebase';
	import type { Form, Result} from '$lib/form/inputs';
	import type { User } from 'firebase/auth';

	import { getDoc, doc } from 'firebase/firestore';

	let { id } = page.params;

	let data: Form | null = $state(null);

	const getForm = (user: User | null) => {
		// we wouldn't be here without user
		if (user == null) return;
		getDoc(doc(firestore, `admin/${user.uid}/forms`, id))
			.then((doc) => {
				if (doc.exists()) {
					data = doc.data() as Form;
					console.log(data);
				} else {
					goto('/admin/404');
				}
			})
			.catch((res) => {
				if (res.status == 404) goto('/admin/404');
				else console.error(res.body);
			});
	};

	const BANNED_COLS = ['form_id', 'admin_id', 'session_id'];

	const columns = $derived.by(() => {
		if (data == null) return [];
		return [...data.inputs.map((input) => input.label), 'date', 'email'].filter(
			(col) => !BANNED_COLS.includes(col)
		);
	});

	const rows = $derived.by(() => {
		if (data == null) return [];
		return data.results
	});

	const toCsv = (data: Form) => {
		let csv = '';
		csv += data.inputs.map((input) => input.label).join(',') + '\n';
		data.results.forEach((result) => {
			csv += data.inputs.map((input) => result[input.label].replace(',', '，')).join(',') + '\n';
		});
		return csv;
	};

	const downloadCsv = () => {
		if (data == null) return;
		const csv = toCsv(data);
		const blob = new Blob([csv], { type: 'text/csv' });
		const url = URL.createObjectURL(blob);
		const a = document.createElement('a');
		a.href = url;
		a.download = `${data.title}.csv`;
		a.click();
	};

	auth.onAuthStateChanged(getForm);
</script>

<div class="flex items-center justify-start gap-4">
	<button class="btn" onclick={downloadCsv}>Download CSV</button>
</div>

<div class="overflow-x-auto font-[sans-serif]">
	<table class="min-w-full bg-white">
		<thead class="bg-gray-800 whitespace-nowrap">
			<tr>
				{#each columns as column}
					<th class="p-4 text-left text-sm font-medium text-white"> {column} </th>
				{/each}
				<th class="p-4 text-left text-sm font-medium text-white"> chat log </th>
			</tr>
		</thead>

		<tbody class="whitespace-nowrap">
			<tr class="even:bg-blue-50">
				{#each rows as row}
					{#each columns as column}
						<td class="p-4 text-sm text-black"> {row[column]} </td>
					{/each}
					<td class="p-4 text-sm text-darkblue-800">
						<a href={`/admin/conversation/${row.admin_id}/${row.form_id}/${row.session_id}/`}>
							link
						</a>
					</td>
				{/each}
			</tr>
		</tbody>
	</table>
</div>
