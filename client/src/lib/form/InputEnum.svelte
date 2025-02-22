<script lang="ts">
	import type { EnumData } from '$lib/form/inputs.d.ts';
	type Props = { input: EnumData };
	let { input = $bindable() }: Props = $props();
	let addValue = (a: string) => {
		input.values.push(a);
	};
	let current_input = $state('');
</script>

<div>
	<p class="block text-sm/6 font-medium text-gray-900">Enum items:</p>
	<div class="mt-2">
		<div class="flex flex-row gap-4">
			{#each input.values as val}
				<div
					class="shrink-0 rounded-md bg-white pl-3 outline-1 -outline-offset-1 outline-gray-300 has-[input:focus-within]:outline-2 has-[input:focus-within]:-outline-offset-2 has-[input:focus-within]:outline-indigo-600"
				>
					<span class="block shrink-0 text-base">
						{val}
						<button
							type="button"
							class="text-red-500"
							onclick={() => (input.values = input.values.filter((v) => v !== val))}>X</button
						>
					</span>
				</div>
			{/each}
			<div
				class="shrink-0 rounded-md bg-white pl-3 outline-1 -outline-offset-1 outline-gray-300 has-[input:focus-within]:outline-2 has-[input:focus-within]:-outline-offset-2 has-[input:focus-within]:outline-indigo-600"
			>
				<input
					type="text"
					name="next_input"
					id="description"
					class="block min-w-0 shrink-0 py-1.5 pr-3 pl-1 text-base text-gray-900 placeholder:text-gray-400 focus:outline-none sm:text-sm/6"
					placeholder="Description (enter to add)"
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
</div>
