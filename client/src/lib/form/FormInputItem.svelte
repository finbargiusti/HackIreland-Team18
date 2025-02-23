<script lang="ts">
 import type { InputField, InputChoice as t_InputChoice } from "$lib/form/inputs"
 import InputChoice from "$lib/form/InputChoice.svelte"

 type Props = {
     input: InputField
 }

 let { input = $bindable() }: Props = $props()
</script>

<div class="w-full">
  <label for="description" class="block text-sm/6 font-medium text-gray-900">Description</label>
  <div class="mt-2 flex flex-col w-full gap-4">
    <div class="flex w-full items-center rounded-md bg-white pl-3 outline-1 -outline-offset-1 outline-gray-300 has-[input:focus-within]:outline-2 has-[input:focus-within]:-outline-offset-2 has-[input:focus-within]:outline-indigo-600">
      <input type="text" name="label" id="label" class="block min-w-0 grow py-1.5 pr-3 pl-1 text-lg text-gray-900 placeholder:text-gray-400 focus:outline-none sm:text-sm/6" placeholder="Label"
        bind:value={input.label} />
    </div>
    <div class="flex w-full items-center rounded-md bg-white pl-3 outline-1 -outline-offset-1 outline-gray-300 has-[input:focus-within]:outline-2 has-[input:focus-within]:-outline-offset-2 has-[input:focus-within]:outline-indigo-600">
      <input type="text" name="description" id="description" class="block min-w-0 grow py-1.5 pr-3 pl-1 text-lg text-gray-900 placeholder:text-gray-400 focus:outline-none sm:text-sm/6" placeholder="Description"
        bind:value={input.description} />
    </div>
  </div>
</div>

{#if input.data.type == 'choice'}
  <InputChoice bind:input={input.data as t_InputChoice} />
{/if}




