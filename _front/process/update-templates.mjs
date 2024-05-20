import { readdirSync, writeFileSync } from 'fs';
import { open } from 'node:fs/promises';
import { extname } from 'path';

const processedScriptsReg = /([a-zA-Z0-9_]+)-([a-zA-Z0-9]+)\.js/

// creates a map of _static/global/scripts files:
// debug-HASH22.js, player-HASH33.js -> { "debug": "HASH22", interact": "HASH33" }
const prefixToHash = () => {
  let output = {};
  readdirSync("_static/global/scripts", { withFileTypes: true })
    .filter(d => !d.isDirectory())
    .filter(d => extname(d.name) == ".js")
    .reduce((acc, d) => {
      let res = processedScriptsReg.exec(d.name);
      if (res) {
        acc[res[1]] = res[2];
      }
      return acc;
    }, output);
    return output;
}

// get directories of the different experiment configs
const getAppDirectories = () =>
  readdirSync(".", { withFileTypes: true })
    .filter(d => d.isDirectory())
    .filter(d => !d.name.startsWith(".") && !d.name.startsWith("_") && d.name != "node_modules")
    .map(d => d.name);

const getTemplateDirectories = () => {
  let apps = getAppDirectories();
  let pages = "_pages";
  let subpages = readdirSync("_pages", { withFileTypes: true })
    .filter(d => d.isDirectory())
    .map(d => `${pages}/${d.name}`);
  return [...apps, pages, ...subpages];
}

// get templates in a directory
const getHtmlFilesInDir = parent =>
  readdirSync(parent, { withFileTypes: true })
  .filter(d => !d.isDirectory())
  .filter(d => extname(d.name) == ".html")
  .map(d => parent + "/" + d.name);
    

const reg = /global\/scripts\/([a-zA-Z0-9_]+)-([a-zA-Z0-9]+)\.js/

// change a template by replacing hash
const processFile = async (file, map) => {
  const fd = await open(file);
  let fileChanged = false;
  let output = "";

  for await (const line of fd.readLines()) {
    let res = reg.exec(line);
    let lineUnchanged = true;
    if(res) {
      const prefix = res[1];
      const oldHash = res[2];
      const newHash = map[prefix];
      if (oldHash !== newHash) {
        let replaced = line.replace(oldHash, map[prefix]);
        output += replaced + '\n';
        lineUnchanged = false;
        fileChanged = true;
      }
    }
    if (lineUnchanged) {
      output += line + '\n';
    }
  }
  if (fileChanged) {
    writeFileSync(file, output, 'utf-8');
  }
  return fileChanged;
}

const main = async () => {
  const templateDirs =getTemplateDirectories();
  const templates = templateDirs.reduce((acc, d) => [...acc, ...getHtmlFilesInDir(d)], []);
  let map = prefixToHash();
  console.log("[assets] template update using the following hashes: ", map);
  let updates = 0;
  for (const tpl of templates) {
    let updated = await processFile(tpl, map);
    if (updated) updates ++;
  }
  console.log("[assets] number of html templates changed: " + updates);
};


await main();