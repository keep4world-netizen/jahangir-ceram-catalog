'use strict';
/*
 * Vercel serverless function: /api/gh
 * Lets the admin page (admin/index.html) talk to the GitHub API WITHOUT exposing the GitHub token.
 * The token lives only in Vercel environment variables. Callers must log in with a username/password
 * (also environment variables). Only the few GitHub calls the admin page needs are allowed, and writes
 * are restricted to data/catalog-data.js and assets/images/*.webp, and files can never be deleted.
 *
 * Environment variables (Vercel -> Project -> Settings -> Environment Variables):
 *   GITHUB_TOKEN            fine-grained token, this repo only, Contents: Read and write
 *   ADMIN_USER, ADMIN_PASS  first login
 *   ADMIN_USER_2, ADMIN_PASS_2, ADMIN_USER_3, ADMIN_PASS_3   optional extra logins
 */
const crypto = require('crypto');

const OWNER = process.env.GH_OWNER || 'keep4world-netizen';
const REPO = process.env.GH_REPO || 'jahangir-ceram-catalog';

const SHA = '[0-9a-f]{40}';
const BRANCH = '[A-Za-z0-9._\\-/]{1,100}';
const SHA_RE = new RegExp('^' + SHA + '$');
const DATA_FILE = 'data/catalog-data.js';
const IMG_RE = /^assets\/images\/(?:[A-Za-z0-9._-]+\/)?[A-Za-z0-9._-]+\.webp$/;

function onlyKeys(o, keys) { return Object.keys(o).every(function (k) { return keys.indexOf(k) !== -1; }); }

const RULES = [
  { m: 'GET', re: /^$/ },
  { m: 'GET', re: new RegExp('^/git/ref/heads/' + BRANCH + '$') },
  { m: 'GET', re: new RegExp('^/git/commits/' + SHA + '$') },
  { m: 'GET', re: new RegExp('^/git/trees/' + SHA + '\\?recursive=1$') },
  { m: 'GET', re: new RegExp('^/contents/data/catalog-data\\.js\\?ref=' + SHA + '$') },
  { m: 'POST', re: /^\/git\/blobs$/, check: function (b) {
      if (!onlyKeys(b, ['content', 'encoding']) || b.encoding !== 'base64' || typeof b.content !== 'string') return 'bad blob';
      if (b.content.length > 4000000) return 'blob too large';
      return null;
  } },
  { m: 'POST', re: /^\/git\/trees$/, check: function (b) {
      if (!onlyKeys(b, ['base_tree', 'tree']) || !SHA_RE.test(String(b.base_tree)) || !Array.isArray(b.tree)) return 'bad tree';
      if (b.tree.length < 1 || b.tree.length > 500) return 'bad tree size';
      for (var i = 0; i < b.tree.length; i++) {
        var e = b.tree[i];
        if (!e || typeof e !== 'object' || !onlyKeys(e, ['path', 'mode', 'type', 'sha'])) return 'bad tree entry';
        if (e.mode !== '100644' || e.type !== 'blob') return 'bad tree entry type';
        if (!SHA_RE.test(String(e.sha))) return 'bad tree entry sha'; // null (= delete a file) is not allowed
        if (typeof e.path !== 'string' || !(e.path === DATA_FILE || IMG_RE.test(e.path))) return 'path not allowed: ' + String(e.path).slice(0, 80);
      }
      return null;
  } },
  { m: 'POST', re: /^\/git\/commits$/, check: function (b) {
      if (!onlyKeys(b, ['message', 'tree', 'parents'])) return 'bad commit';
      if (typeof b.message !== 'string' || b.message.length > 4000 || !SHA_RE.test(String(b.tree))) return 'bad commit';
      if (!Array.isArray(b.parents) || b.parents.length !== 1 || !SHA_RE.test(String(b.parents[0]))) return 'bad commit parents';
      return null;
  } },
  { m: 'PATCH', re: new RegExp('^/git/refs/heads/' + BRANCH + '$'), check: function (b) {
      if (!onlyKeys(b, ['sha']) || !SHA_RE.test(String(b.sha))) return 'bad ref update';
      return null;
  } }
];

function sha256(s) { return crypto.createHash('sha256').update(String(s)).digest(); }
function same(a, b) { return crypto.timingSafeEqual(sha256(a), sha256(b)); }
function logins() {
  var out = [];
  ['', '_2', '_3'].forEach(function (suf) {
    var u = process.env['ADMIN_USER' + suf], p = process.env['ADMIN_PASS' + suf];
    if (u && p) out.push([u, p]);
  });
  return out;
}
function authorized(req) {
  var h = String(req.headers['authorization'] || '');
  if (h.slice(0, 6) !== 'Basic ') return false;
  var dec = Buffer.from(h.slice(6), 'base64').toString('utf8'), i = dec.indexOf(':');
  if (i < 0) return false;
  var u = dec.slice(0, i), p = dec.slice(i + 1), ok = false;
  logins().forEach(function (l) { if (same(u, l[0]) & same(p, l[1])) ok = true; });
  return ok;
}
function send(res, status, body, type) {
  res.statusCode = status;
  res.setHeader('Content-Type', type || 'application/json; charset=utf-8');
  res.setHeader('Cache-Control', 'no-store');
  res.end(typeof body === 'string' ? body : JSON.stringify(body));
}
function sleep(ms) { return new Promise(function (r) { setTimeout(r, ms); }); }

module.exports = async function handler(req, res) {
  try {
    var token = process.env.GITHUB_TOKEN;
    if (!token || !logins().length) return send(res, 500, { message: 'Server is not configured: set GITHUB_TOKEN, ADMIN_USER and ADMIN_PASS in Vercel.' });
    if (!authorized(req)) { await sleep(800); return send(res, 401, { message: 'Unauthorized' }); }

    var p = new URL(req.url, 'http://localhost').searchParams.get('p');
    if (p === null) p = '';
    var rule = RULES.filter(function (r) { return r.m === req.method && r.re.test(p); })[0];
    if (!rule) return send(res, 403, { message: 'Path not allowed' });

    var body;
    if (req.method !== 'GET') {
      body = req.body;
      if (typeof body === 'string') { try { body = JSON.parse(body); } catch (e) { body = null; } }
      if (!body || typeof body !== 'object' || Array.isArray(body)) return send(res, 400, { message: 'Bad request body' });
      var err = rule.check ? rule.check(body) : null;
      if (err) return send(res, 400, { message: err });
    }

    var isContents = p.indexOf('/contents/') === 0;
    var headers = {
      Authorization: 'Bearer ' + token,
      'X-GitHub-Api-Version': '2022-11-28',
      'User-Agent': 'jahangir-ceram-admin',
      Accept: isContents ? 'application/vnd.github.raw+json' : 'application/vnd.github+json'
    };
    if (req.method !== 'GET') headers['Content-Type'] = 'application/json';
    var r = await fetch('https://api.github.com/repos/' + OWNER + '/' + REPO + p, {
      method: req.method, headers: headers, body: req.method === 'GET' ? undefined : JSON.stringify(body)
    });
    var text = await r.text();
    if (r.status === 401) return send(res, 502, { message: 'GitHub token on the server is invalid or expired' });
    send(res, r.status, text, isContents && r.ok ? 'text/plain; charset=utf-8' : 'application/json; charset=utf-8');
  } catch (e) {
    send(res, 500, { message: 'Server error: ' + (e && e.message ? e.message : e) });
  }
};
