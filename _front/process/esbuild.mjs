import * as esbuild from 'esbuild';
import { readdirSync } from 'fs';
import { extname } from 'path';

const SOURCE_DIR = "_front/src";
const sources = readdirSync("_front/src", { withFileTypes: true })
  .filter(d => !d.isDirectory())
  .filter(d => extname(d.name) == ".js")
  .map((d) => `${SOURCE_DIR}/${d.name}`);

let result = await esbuild.build({
  entryPoints: sources,
  bundle: true,
  //watch: process.env.APP_ENV === "DEV" && {
  //onRebuild(error) {
  //   if (error) console.error('watch build failed:', error)
  //   else console.log('watch build succeeded')
  // }
  //},
  outdir: './_static/global/scripts/',
  entryNames:  "[dir]/[name]-[hash]",
  target: [
    'chrome64',
    'firefox53',
    'safari11',
    'edge79',
  ]
});

console.log("[assets] esbuild: ", result);