const fs = require('fs');
const path = require('path');
const source = path.join(__dirname, 'upstream');
const target = path.join(__dirname, 'dist');
fs.rmSync(target, {recursive:true,force:true});
fs.cpSync(source,target,{recursive:true});
const authFile = path.join(target,'assets/auth-DqLZ8PEK.js');
let auth = fs.readFileSync(authFile,'utf8');
const original = 'logoAlt:"Wealthfolio logo vantage",title:"Wealthfolio",description:"Your private portfolio tracker."';
if (!auth.includes(original)) throw Error('Upstream login changed. Review branding before upgrading.');
auth = auth.replace(original,'logoAlt:"Wealthfolio · motor de Minos Capital",title:"Minos Capital",description:"Tu cartera privada · Powered by Wealthfolio"');
fs.writeFileSync(authFile,auth);
const assets=path.join(target,'assets');
const names=fs.readdirSync(assets).filter(n=>n.endsWith('.js'));
const map=names.map(n=>[n,n.slice(0,-3)+'.minos-v1.js']);
for(const oldName of names){
 let text=fs.readFileSync(path.join(assets,oldName),'utf8');
 for(const [oldRef,newRef] of map) text=text.replaceAll(oldRef,newRef);
 fs.writeFileSync(path.join(assets,map.find(x=>x[0]===oldName)[1]),text);
}
for(const name of names)fs.unlinkSync(path.join(assets,name));
let html=fs.readFileSync(path.join(target,'index.html'),'utf8');
if(!html.includes('<title>Wealthfolio</title>'))throw Error('Unexpected upstream title');
html=html.replace('<title>Wealthfolio</title>','<title>Minos Capital</title>');
for(const [oldRef,newRef] of map)html=html.replaceAll(oldRef,newRef);
fs.writeFileSync(path.join(target,'index.html'),html);
const manifestPath=path.join(target,'manifest.json');
if(fs.existsSync(manifestPath)){const m=JSON.parse(fs.readFileSync(manifestPath,'utf8'));m.name='Minos Capital';m.short_name='Minos';fs.writeFileSync(manifestPath,JSON.stringify(m,null,2));}
console.log('Branding built; JS cache refreshed: '+names.length+' chunks.');
