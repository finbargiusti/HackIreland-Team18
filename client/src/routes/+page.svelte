<script lang="ts">
  import ChatList from '$lib/ChatList.svelte';

  // Slide 3/4: Chat demo data and a simple send handler.
  let message = "";
  let messages = [
    { id: 1, role: "bot", content: "How are you feeling today?" },
    { id: 2, role: "patient", content: "Not so great" },
    { id: 3, role: "bot", content: "How much glucose did you take today?" },
    { id: 4, role: "patient", content: "I took 2 tablets" }
  ];

  function sendTest() {
    if (message.trim()) {
      messages = [...messages, { id: messages.length + 1, role: "patient", content: message }];
      message = "";
    }
  }

  // Reactive derived data for ChatList: transform messages into expected shape.
  $: chatData = messages.map(m => ({ user: m.role === "patient", data: m.content }));

  // Flag to trigger animations (fade in + subtle wiggle) only once.
  let animateCards = false;

  // Listen for spacebar press to trigger animation.
  function handleKeydown(e: KeyboardEvent) {
    if ((e.key === " " || e.code === "Space") && !animateCards) {
      animateCards = true;
    }
  }
</script>

<svelte:window on:keydown={handleKeydown} />

<style>
  /* Slide container styles */
  .slide {
    height: 100vh;
    position: relative;
  }
  .bg-overlay {
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
  }
  .overlay {
    position: absolute;
    inset: 0;
    background: linear-gradient(180deg, rgba(0,0,0,0.5), rgba(0,0,0,0.5));
    z-index: 1;
  }
  .content {
    position: relative;
    z-index: 2;
  }

  /* Material-inspired card styles with darker green gradient */
  .material-card,
  .material-card-light {
    background: linear-gradient(135deg, #004d00, #002a00);
    color: #ffffff;
    border-radius: 12px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
  }
  .material-card {
    padding: 2.5rem;
  }
  .material-card-light {
    padding: 2rem;
  }
  .chat-card {
    background: linear-gradient(135deg, #003300, #001a00);
    color: #f1f1f1;
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
  }

  /* Animation: fade in with subtle wiggle */
  .animate-in {
    animation: fadeInWiggle 1s ease-out forwards;
  }
  @keyframes fadeInWiggle {
    0% {
      opacity: 0;
      transform: translateY(20px) rotate(0deg);
    }
    80% {
      opacity: 1;
      transform: translateY(0) rotate(0deg);
    }
    85% {
      transform: rotate(2deg);
    }
    90% {
      transform: rotate(-2deg);
    }
    95% {
      transform: rotate(1deg);
    }
    100% {
      transform: rotate(0deg);
    }
  }

  /* Apple-like message exchange styles (for fallback or ChatList if needed) */
  .chat-contain {
    display: flex;
    flex-direction: column;
  }
  .chat {
    padding: 1rem;
    border-radius: 1rem;
    margin-bottom: 0.5rem;
  }
  .chat.user {
    background: #6ec1a1;
    color: #fff;
    align-self: flex-end;
  }
  .chat.system {
    background: #b0bec5;
    color: #212121;
    align-self: flex-start;
  }

  /* Input and button styling for the chat area */
  .chat-input {
    flex-grow: 1;
    padding: 0.75rem;
    border-radius: 0.5rem 0 0 0.5rem;
    font-size: 1.125rem;
    background: #37474f;
    color: #ffffff;
    border: none;
    outline: none;
  }
  .chat-send {
    padding: 0.75rem 1.5rem;
    font-size: 1.125rem;
    border-radius: 0 0.5rem 0.5rem 0;
    background: #6ec1a1;
    color: #ffffff;
    border: none;
    cursor: pointer;
    transition: background 0.3s;
  }
  .chat-send:hover {
    background: #5aa38a;
  }
</style>

<!-- Slide 1: Welcome -->
<div
  class="slide flex items-center justify-center bg-overlay"
  style="background-image: url('https://images.unsplash.com/photo-1614852207091-9d38a326d2ba?fm=jpg&q=60&w=3000&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MTl8fGdyZWVuJTIwZ3JhZGllbnR8ZW58MHx8MHx8fDA%3D');"
>
  <div class="overlay"></div>
</div>

<!-- Slide 2: Market Stats -->
<div
  class="slide flex items-center justify-center bg-overlay"
  style="background-image: url('https://c4.wallpaperflare.com/wallpaper/852/870/444/green-abstract-texture-minimalism-wallpaper-preview.jpg');"
>
  <div class="overlay"></div>
  <div class="content max-w-3xl material-card {animateCards ? 'animate-in' : ''}">
    <p class="mb-6 text-2xl">
      A new platform to <strong>Create and Manage</strong> Patient-reported outcomes with the use of <strong>conversational</strong> AI, an essential part of any Clinical Trial.
    </p>
    <p class="mb-6 text-2xl">
      <strong>80%</strong> of trials are delayed by at least a month due to patient dropout, costing the company up to <strong>$8 Million</strong> every day that the trial is delayed.
    </p>
    <p class="mb-6 text-2xl">
      <strong>59%</strong> of drug trials are abandoned before they can apply for FDA approval due to high patient dropout rates.
    </p>
    <p class="mb-6 text-2xl font-bold">
      Why do patients drop out?
    </p>
    <ul class="list-disc pl-8 text-2xl mb-6">
      <li>Financial cost</li>
      <li>Time and scheduling conflicts</li>
      <li>Lack of understanding and engagement</li>
      <li>Long-distance travelling</li>
      <li>Anxiety and stress</li>
    </ul>
    <p class="text-sm text-gray-300">
      Sources: <a href="https://pmc.ncbi.nlm.nih.gov/articles/PMC7342339/" target="_blank" class="underline">PMC7342339</a> &middot; <a href="https://mdgroup.com/blog/why-do-patients-drop-out-of-clinical-trials/" target="_blank" class="underline">MD Group</a>
    </p>
  </div>
</div>

<!-- Slide 3: (Optional extra slide) Welcome -->
<div
  class="slide flex items-center justify-center bg-overlay"
  style="background-image: url('https://images.unsplash.com/photo-1614852207091-9d38a326d2ba?fm=jpg&q=60&w=3000&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MTl8fGdyZWVuJTIwZ3JhZGllbnR8ZW58MHx8MHx8fDA%3D');"
>
  <div class="overlay"></div>
  <div class="content text-center text-white">
    <h1 class="text-5xl font-bold">Welcome to Clinitrax</h1>
    <h2 class="text-3xl mt-4">The future in Clinical Trials</h2>
  </div>
</div>

<!-- Slide 4: Demo Conversation with Apple-like styling and Material text -->
<div
  class="slide flex items-center justify-center bg-overlay"
  style="background-image: url('https://c4.wallpaperflare.com/wallpaper/17/878/328/green-background-wallpaper-preview.jpg');"
>
  <div class="overlay"></div>
  <div class="content grid grid-cols-2 gap-8 w-full max-w-6xl p-8">
    <!-- Column 1: Process List -->
    <div class="material-card-light {animateCards ? 'animate-in' : ''}">
      <ul class="list-disc pl-6 text-2xl">
        <li class="mb-4">Trial specialist sends a link to patients</li>
        <li class="mb-4">Patients turn on notifications and open the link as prescribed, e.g., every evening</li>
        <li class="mb-4">Patients answer questions in a natural language conversation</li>
      </ul>
    </div>
    <!-- Column 2: Chat Simulation using ChatList.svelte -->
    <div class="chat-card flex flex-col {animateCards ? 'animate-in' : ''}">
      <h3 class="text-2xl font-bold mb-6">Fionn's Checkup</h3>
      <!-- Use the ChatList component -->
      <ChatList chats={chatData} />
      <div class="flex mt-4">
        <input
          type="text"
          bind:value={message}
          placeholder="Try it now"
          class="flex-grow p-3 rounded-l text-xl bg-gray-700 text-white border-none focus:outline-none"
        />
        <button on:click={sendTest} class="btn rounded-r text-xl bg-green-600 hover:bg-green-700 text-white px-6 py-3">
          Send
        </button>
      </div>
    </div>
  </div>
</div>
