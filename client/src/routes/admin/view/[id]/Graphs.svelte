<script lang="ts">
	import type { Result, InputType } from '$lib/form/inputs';
	import { Chart, type ChartConfiguration } from 'chart.js/auto';

	type Props = {
		results: Result[];
		colTypes: { [key: string]: InputType };
	};

	const { results, colTypes }: Props = $props();

	let candidates = Object.keys(colTypes)
		.filter((k) => ['number', 'choice'].includes(colTypes[k]))
		.map((x) => ({
			name: x,
			data: results.map((r) => r[x]),
			type: colTypes[x],
			canvas: null as HTMLCanvasElement | null,
			ctx: null as CanvasRenderingContext2D | null,
			chart: null as Chart | null
		}));

	$effect(() => {
		candidates.forEach((c) => {
			if (c.canvas && !c.ctx) {
				c.ctx = c.canvas.getContext('2d');
				let config: ChartConfiguration =
					c.type == 'choice'
						? {
								type: 'pie',
								data: {
									labels: Array.from(new Set(c.data)).map((x) => x.toString().toLowerCase()),
									datasets: [
										{
											label: c.name,
											data: Array.from(new Set(c.data)).map(
												(x) => c.data.filter((y) => y == x).length
											),
											backgroundColor: Array.from(new Set(c.data)).map(
												(x) => `hsl(${Math.random() * 360}, 100%, 50%)`
											)
										}
									]
								}
							}
						: {
								type: 'bar',
								data: {
									labels: Array.from(new Set(c.data)).sort(),
									datasets: [
										{
											label: c.name,
											data: Array.from(new Set(c.data)).map(
												(x) => c.data.filter((y) => y == x).length
											),
											backgroundColor: Array.from(new Set(c.data)).map(
												(x) => `hsl(${Math.random() * 360}, 100%, 50%)`
											)
										}
									]
								}
							};

				config = {
					...config,
					options: {
						responsive: true
					}
				};
				if (c.ctx) {
					c.chart = new Chart(c.ctx, config);
				}
			}
		});
	});
</script>

<div class="flex flex-row flex-wrap items-stretch">
	{#each candidates as c}
		<div class="flex-1">
			<canvas bind:this={c.canvas}></canvas>
		</div>
	{/each}
</div>
