import type { Handle } from '@sveltejs/kit';

export const handle: Handle = async ({ resolve, event }) => {

  if (event.url.pathname.startsWith('/')) {
    if(event.request.method === 'OPTIONS') {
      return new Response(null, {
        headers: {
          'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, PATCH, OPTIONS',
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Headers': '*',
        }
      });
    }
  }

  const response = await resolve(event);
  if (event.url.pathname.startsWith('/')) {
        response.headers.append('Access-Control-Allow-Origin', `*`);
  }
  return response;
};
