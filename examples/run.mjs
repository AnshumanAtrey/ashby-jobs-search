// Run Ashby Jobs Scraper & API - All Companies, Remote, Last 24 Hours on Apify and print each dataset row as JSON.
//   npm install apify-client
//   APIFY_TOKEN=... node run.mjs
import { readFileSync } from 'node:fs';
import { ApifyClient } from 'apify-client';

const client = new ApifyClient({ token: process.env.APIFY_TOKEN });
const input = JSON.parse(readFileSync(new URL('./input.json', import.meta.url), 'utf8'));
const run = await client.actor('anshumanatrey/ashby-jobs-search').call(input);
const { items } = await client.dataset(run.defaultDatasetId).listItems();
for (const item of items) console.log(JSON.stringify(item));
