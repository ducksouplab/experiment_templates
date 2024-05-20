import * as fs from 'fs';
import { extname } from 'path';


const main = async () => {
  const scriptsDir = "_static/global/scripts";
  if (!fs.existsSync(scriptsDir)){
    fs.mkdirSync(scriptsDir);
  } else {
  const files = fs.readdirSync("_static/global/scripts", { withFileTypes: true })
    .filter(d => !d.isDirectory())
    .filter(d => extname(d.name) == ".js")
    .map((d) => d.name);
  for(const file of files) {
    fs.unlinkSync("_static/global/scripts/" + file);
  }
  console.log("[assets] number of compiled/static js files deleted: " + files.length);
}
};

main();