<script lang="ts">
 import type { InputField } from "$lib/form/inputs.d.ts"
 import InputEnum from "$lib/form/InputEnum.svelte"

 type Props = {
     input: InputField
 }

 let { input = $bindable() }: Props = $props()
</script>

<div>
  <label for="description" class="block text-sm/6 font-medium text-gray-900">Description</label>
  <div class="mt-2 flex flex-row">
    <div class="flex items-center rounded-md bg-white pl-3 outline-1 -outline-offset-1 outline-gray-300 has-[input:focus-within]:outline-2 has-[input:focus-within]:-outline-offset-2 has-[input:focus-within]:outline-indigo-600">
      <input type="text" name="description" id="description" class="block min-w-0 grow py-1.5 pr-3 pl-1 text-base text-gray-900 placeholder:text-gray-400 focus:outline-none sm:text-sm/6" placeholder="Description"
        bind:value={input.description} />
    </div>
  </div>
</div>

{#if input.data.type === 'choice'}
  <InputEnum bind:input={input.data as InputEnum} />
{/if}

{#if input.data.type === 'number'}
  <InputEnum bind:input={input.data as InputEnum} />
{/if}




