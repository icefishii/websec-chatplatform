<template>
  <nav
    class="fixed top-0 left-0 w-full flex justify-between items-center p-4 shadow-md bg-emerald-950"
  >
    <RouterLink to="/" class="flex items-center gap-2 rounded-md">
      <img alt="Vue logo" src="@/assets/logo.svg" width="32" height="32" />
    </RouterLink>

    <div class="flex gap-4">
      <RouterLink to="/login" class="px-3 py-1 border rounded transition"> Login </RouterLink>
      <RouterLink to="/register" class="px-3 py-1 border rounded text-white transition">
        Register
      </RouterLink>
    </div>
  </nav>
</template>
