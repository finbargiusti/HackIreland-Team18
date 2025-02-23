<script lang="ts">
	import '../app.css';
	let { children } = $props();
</script>

<h1 class="text-3xl mb-8 font-bold tracking-tight text-gray-900">
	{@render children()}
</h1>
