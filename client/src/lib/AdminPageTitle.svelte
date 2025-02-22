<script lang="ts">
	import '../app.css';
	let { children } = $props();
</script>

<div class="mx-auto max-w-7xl">
	<h1 class="text-3xl font-bold tracking-tight text-gray-900">
		{@render children()}
	</h1>
</div>
