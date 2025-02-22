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
		<div class="flex flex-col gap-4">
			<ul class="list-disc" >
			{#each input.values as val}
				<li
					class="shrink-0 rounded-md flex flex-row bg-white pl-3"
				>
					<span class="block grow text py-2">
						{val}
					</span>
					<button
						type="button"
						class="btn danger"
						onclick={() => (input.values = input.values.filter((v) => v !== val))}>X</button
					>
				</li>
			{/each}
			</ul>
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
</div>
