<script lang="ts">
	import type { InputChoice } from '$lib/form/inputs.d.ts';
	type Props = { input: InputChoice };
	let { input = $bindable() }: Props = $props();
	let addValue = (a: string) => {
		input.values.push(a);
	};
	let current_input = $state('');
</script>

<div>
	<p class="block text-sm/6 font-medium text-gray-900">Choices:</p>
	<div class="mt-2">
		<div class="flex list-disc flex-col mb-4">
			{#each input.values as val}
				<div class="flex pb-2 mt-2 shrink-0 flex-row items-center pl-4 [&:not(:last-child)]:border-b-2 border-gray-300">
					<span class="text block grow m-0">
						{val}
					</span>
					<button
						type="button"
						class="btn danger"
						onclick={() => (input.values = input.values.filter((v) => v !== val))}>Delete</button
					>
				</div>
			{/each}
		</div>
		<div
			class="shrink-0 rounded-md bg-white pl-3 outline-1 -outline-offset-1 outline-gray-300 has-[input:focus-within]:outline-2 has-[input:focus-within]:-outline-offset-2 has-[input:focus-within]:outline-indigo-600"
		>
			<input
				type="text"
				name="next_input"
				id="description"
				class="block min-w-0 shrink-0 py-1.5 pr-3 pl-1 text-base text-gray-900 placeholder:text-gray-400 focus:outline-none sm:text-sm/6"
				placeholder="Enter item... (enter to add)"
				bind:value={current_input}
				onkeydown={(e) => {
					if (e.key === 'Enter') {
						addValue(current_input);
						current_input = '';
					}
				}}
			/>
		</div>
	</div>
</div>
