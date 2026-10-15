// Cloudflare Worker for caish.org.
//
// Cloudflare serves every file in the repo as a static page or asset.
// This script only runs for /api/* (and the old /.netlify/functions/*
// paths), where it calls one of the small server functions in
// functions/. Those were written for Netlify, so runNetlifyHandler
// translates between the two formats.

import events from '../functions/events.js';
import feedback from '../functions/feedback.js';
import hdwsa from '../functions/hdwsa.js';
import lunches from '../functions/lunches.js';
import sketch from '../functions/sketch.js';
import social from '../functions/social.js';

const FUNCTIONS = { events, feedback, hdwsa, lunches, sketch, social };

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const match = url.pathname.match(/^\/(?:api|\.netlify\/functions)\/([a-z]+)\/?$/);
    const fn = match && FUNCTIONS[match[1]];
    if (!fn) return env.ASSETS.fetch(request);
    return runNetlifyHandler(fn.handler, request, url);
  }
};

async function runNetlifyHandler(handler, request, url) {
  const headers = {};
  request.headers.forEach((value, key) => { headers[key] = value; });
  const event = {
    httpMethod: request.method,
    path: url.pathname,
    headers,
    queryStringParameters: Object.fromEntries(url.searchParams),
    body: ['GET', 'HEAD'].includes(request.method) ? null : await request.text(),
    isBase64Encoded: false
  };
  const result = await handler(event);
  return new Response(result.body ?? '', {
    status: result.statusCode || 200,
    headers: result.headers || {}
  });
}
