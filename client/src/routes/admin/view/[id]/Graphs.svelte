<script lang="ts">
	import type { Result, InputType } from '$lib/form/inputs';
	
	type Props = {
		results: Result[];
		colTypes: {[key: string]: InputType};
	}

	const {results, colTypes} = $props() as Props;

	let candidates = Object.keys(colTypes).filter(k => ['number', 'choice'].includes(colTypes[k])).map(
		(x) => (
			{
				name: x,
				data: results.map(r => r[x]),
				type: colTypes[x],
				canvas: null as HTMLCanvasElement | null,
				ctx: null as CanvasRenderingContext2D | null
			}
		)
	);

	$effect(() => {
		candidates.forEach(c => {
			if (c.canvas && !c.ctx) {
				c.ctx = c.canvas.getContext('2d');
				if (c.ctx) {
					c.ctx.fillStyle = 'black';
					c.ctx.fillRect(0, 0, c.canvas.width, c.canvas.height);
				}
			}
		});
	});
</script>

{#each candidates as c}
	<canvas bind:this={c.canvas} width="400" height="400"></canvas>
{/each}
