const fs = require('fs');
const path = require('path');
const brand=JSON.parse(fs.readFileSync(path.join(__dirname,'assets/tokens.json'),'utf8')).brand;
const brandName=brand.name+' '+brand.descriptor;
if(/[<>&\"]/.test(brandName))throw Error('Brand name contains unsafe markup');
const source = path.join(__dirname, 'upstream');
const target = path.join(__dirname, 'dist-next');
fs.rmSync(target, {recursive:true,force:true});
fs.cpSync(source,target,{recursive:true});
const authFile = path.join(target,'assets/auth-DqLZ8PEK.js');
let auth = fs.readFileSync(authFile,'utf8');
const original = 'logoAlt:"Wealthfolio logo vantage",title:"Wealthfolio",description:"Your private portfolio tracker."';
if (!auth.includes(original)) throw Error('Upstream login changed. Review branding before upgrading.');
auth = auth.replace(original,'logoAlt:'+JSON.stringify(brandName)+',title:'+JSON.stringify(brandName)+',description:"Tu cartera privada"');
auth=auth.replace('passwordPlaceholder:"Enter your password"','passwordPlaceholder:"Ingresá tu contraseña"').replace('signingIn:"Signing in..."','signingIn:"Ingresando..."').replace('signIn:"Sign In"','signIn:"Ingresar"');
fs.writeFileSync(authFile,auth);
const mainFile=path.join(target,'assets/main-D9tmvAhh.js');
let main=fs.readFileSync(mainFile,'utf8');
const heading='s.jsx(Cn,{children:"Wealthfolio"}),s.jsx(Gi,{children:e("auth:login.description")})';
if(!main.includes(heading))throw Error('Upstream visible login heading changed');
main=main.replace(heading,'s.jsx(Cn,{children:"Minos Capital"}),s.jsx(Gi,{children:e("auth:login.description")})');
let loginStart=main.indexOf('function b4n()');let loginEnd=main.indexOf('function ',loginStart+20);let login=main.slice(loginStart,loginEnd);
function change(a,b){if(!login.includes(a))throw Error('Missing login anchor '+a);login=login.replace(a,b);}
change('className:"fixed inset-0 flex items-center justify-center p-6"','className:"minos-login fixed inset-0 flex items-center justify-center p-6"');
change('src:"/logo-vantage.png"','src:"/minos-symbol-v5.svg"');
change('className:"h-16 w-16 sm:h-20 sm:w-20"','className:"minos-logo"');
change('s.jsx(Cn,{children:"Minos Capital"})','s.jsx(Cn,{className:"minos-title",children:"Minos Capital"})');
change('children:[s.jsx(ln,{"data-testid":"login-password-input"','children:[s.jsx("label",{htmlFor:"password",className:"minos-password-label",children:"Contraseña"}),s.jsx(ln,{"data-testid":"login-password-input"');
change('s.jsx(cG,{className:"text-muted-foreground flex flex-col gap-2 text-center text-xs"})','s.jsx(cG,{className:"minos-attribution",children:s.jsx("a",{href:"https://wealthfolio.app",target:"_blank",rel:"noreferrer",children:"Powered by Wealthfolio"})})');
main=main.slice(0,loginStart)+login+main.slice(loginEnd);
main=require("./ui-modules.cjs").applyUiFlags(main,JSON.parse(fs.readFileSync(path.join(__dirname,"ui-modules.json"),"utf8"))).main;
main=main.replaceAll('children:"Minos Capital"','children:'+JSON.stringify(brandName));
main=require("./theme.cjs").buildTheme(__dirname,target,main);
fs.writeFileSync(mainFile,main);
const assets=path.join(target,'assets');
const names=fs.readdirSync(assets).filter(n=>n.endsWith('.js'));
const map=names.map(n=>[n,n.slice(0,-3)+'.minos-v5.js']);
for(const oldName of names){
 let text=fs.readFileSync(path.join(assets,oldName),'utf8');
 for(const [oldRef,newRef] of map) text=text.replaceAll(oldRef,newRef);
 fs.writeFileSync(path.join(assets,map.find(x=>x[0]===oldName)[1]),text);
}
for(const name of names)fs.unlinkSync(path.join(assets,name));
let html=fs.readFileSync(path.join(target,'index.html'),'utf8');
if(!html.includes('<title>Wealthfolio</title>'))throw Error('Unexpected upstream title');
html=html.replace('<title>Wealthfolio</title>','<title>'+brandName+'</title>');
html=html.replace('</head>','<link rel="stylesheet" href="/minos-login-v5.css"></head>').replace('type="image/png" href="/app-icon-192.png"','type="image/svg+xml" href="/minos-symbol-v5.svg"');
for(const [oldRef,newRef] of map)html=html.replaceAll(oldRef,newRef);
html=html.replace('</head>','<link rel="stylesheet" href="/minos-ui-v4.css"><link rel="stylesheet" href="/minos-theme-v5.css"></head>');
fs.writeFileSync(path.join(target,'index.html'),html);
const cssSource=path.join(__dirname,'login.css');
fs.copyFileSync(cssSource,path.join(target,'minos-login-v5.css'));

const flagsForCss=JSON.parse(fs.readFileSync(path.join(__dirname,'ui-modules.json'),'utf8'));let navCss='';if(!flagsForCss.connect)navCss+='a[href="/connect"],a[href="/settings/connect"]{display:none!important}';fs.writeFileSync(path.join(target,'minos-ui-v4.css'),navCss);
const manifestPath=path.join(target,'manifest.json');
if(fs.existsSync(manifestPath)){const m=JSON.parse(fs.readFileSync(manifestPath,'utf8'));m.name=brandName;m.short_name=brand.name;fs.writeFileSync(manifestPath,JSON.stringify(m,null,2));}
if(process.argv.includes('--check')){console.log('Staged branding; live files unchanged.');process.exit(0);}
const live=path.join(__dirname,'dist');fs.mkdirSync(live,{recursive:true});
for(const name of fs.readdirSync(target)){if(name==='index.html')continue;fs.cpSync(path.join(target,name),path.join(live,name),{recursive:true});}
fs.copyFileSync(path.join(target,'index.html'),path.join(live,'index.html'));fs.rmSync(target,{recursive:true,force:true});
console.log('Branding built; JS cache refreshed: '+names.length+' chunks.');

