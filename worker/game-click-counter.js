export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const corsHeaders = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    };

    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders });
    }

    if (request.method === 'POST' && url.pathname === '/click') {
      const gameName = url.searchParams.get('game');
      if (!gameName) {
        return new Response(JSON.stringify({ error: 'Missing game parameter' }), {
          status: 400,
          headers: { 'Content-Type': 'application/json', ...corsHeaders },
        });
      }

      let clicks = {};
      const data = await env.GAME_CLICKS.get('hot-games');
      if (data) {
        try { clicks = JSON.parse(data); } catch (e) {}
      }

      clicks[gameName] = (clicks[gameName] || 0) + 1;
      await env.GAME_CLICKS.put('hot-games', JSON.stringify(clicks));

      return new Response(JSON.stringify({ ok: true, count: clicks[gameName] }), {
        headers: { 'Content-Type': 'application/json', ...corsHeaders },
      });
    }

    if (request.method === 'GET' && url.pathname === '/top') {
      const limit = parseInt(url.searchParams.get('limit') || '10');
      const data = await env.GAME_CLICKS.get('hot-games');
      let clicks = {};
      if (data) {
        try { clicks = JSON.parse(data); } catch (e) {}
      }

      const sorted = Object.entries(clicks)
        .sort((a, b) => b[1] - a[1])
        .slice(0, limit)
        .map(([name, count]) => ({ name, count }));

      return new Response(JSON.stringify(sorted), {
        headers: { 'Content-Type': 'application/json', ...corsHeaders },
      });
    }

    if (request.method === 'GET' && url.pathname === '/all') {
      const data = await env.GAME_CLICKS.get('hot-games');
      let clicks = {};
      if (data) {
        try { clicks = JSON.parse(data); } catch (e) {}
      }

      const all = Object.entries(clicks).map(([name, count]) => ({ name, count }));
      return new Response(JSON.stringify(all), {
        headers: { 'Content-Type': 'application/json', ...corsHeaders },
      });
    }

    return new Response('Game Click Counter API', { headers: corsHeaders });
  }
};
