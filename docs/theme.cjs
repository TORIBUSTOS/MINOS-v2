const fs=require('fs');
const path=require('path');
function buildTheme(root,target,main){
 const config=JSON.parse(fs.readFileSync(path.join(root,'assets/tokens.json'),'utf8'));
 const ui=JSON.parse(fs.readFileSync(path.join(root,'themes.json'),'utf8'));
 if(!ui.themes.light.enabled||!ui.themes.dark.enabled)throw Error('Native light and dark themes must remain available');
 const safe=s=>{if(typeof s!=='string'||/[;{}<>]/.test(s))throw Error('Unsafe CSS token');return s};
 let css='/* Generated from assets/tokens.json + themes.json. Do not edit output. */\n';
 const common={...ui.tokens,'font-family-ui':config.font.body,'font-family-display':config.font.display,'font-family-mono':config.font.mono};
 const block=(selector,tokens)=>selector+'{'+Object.entries(tokens).map(([k,v])=>'--'+k+':'+safe(v)+';').join('')+'}\n';
 css+=block(':root',common);
 for(const [id,theme] of Object.entries(ui.themes)){
  if(!theme.enabled)continue;
  const colors=Object.fromEntries(Object.entries(theme.tokens).map(([k,v])=>[k,v.startsWith('$')?config.color[v.slice(1)]:v]));
  css+=block(id==='light'?':root,html.light':'html.dark',colors);
 }
 const aliases={background:'bg-base',foreground:'text-main',card:'bg-surface','card-foreground':'text-main',popover:'bg-surface-raised','popover-foreground':'text-main',primary:'primary-action','primary-foreground':'text-on-action',secondary:'bg-section','secondary-foreground':'text-main',muted:'bg-section','muted-foreground':'text-muted',accent:'bg-hover','accent-foreground':'text-main',destructive:'danger','destructive-foreground':'text-on-danger',success:'state-success',warning:'state-warning',info:'state-info',border:'border-subtle',input:'border-strong','input-bg':'bg-surface',ring:'focus-ring',sidebar:'bg-section','sidebar-foreground':'text-main','sidebar-primary':'primary-action','sidebar-primary-foreground':'text-on-action','sidebar-accent':'bg-hover','sidebar-accent-foreground':'text-main','sidebar-border':'border-subtle','sidebar-ring':'focus-ring','button-radius':'radius-sm','control-radius':'radius-sm','card-radius':'radius-md','popup-radius':'radius-md','dialog-radius':'radius-md','card-shadow':'shadow-raised'};
 css+=':root,html.light,html.dark{'+Object.entries(aliases).map(([k,v])=>'--'+k+':var(--'+v+');').join('')+'}\n';
 css+=fs.readFileSync(path.join(root,'app.css'),'utf8');
 fs.writeFileSync(path.join(target,'minos-theme-v5.css'),css);
 const asset=path.resolve(root,config.asset.symbol);if(!asset.startsWith(path.resolve(root,'assets')+path.sep))throw Error('Symbol must be under branding/assets');
 fs.copyFileSync(asset,path.join(target,'minos-symbol-v5.svg'));
 function once(a,b){if(main.split(a).length!==2)throw Error('Theme anchor changed: '+a.slice(0,70));main=main.replace(a,b)}
 once('children:"Wealthfolio"})]}),s.jsxs(ae,{type:"button",variant:"ghost",onClick:()=>{const l=new KeyboardEvent', 'children:'+JSON.stringify(config.brand.name+' '+config.brand.descriptor)+'})]}),s.jsxs(ae,{type:"button",variant:"ghost",onClick:()=>{const l=new KeyboardEvent');
 main=main.replaceAll('src:"/logo.png"','src:"/minos-symbol-v5.svg"').replaceAll('src:"/logo-gold.png",alt:"Wealthfolio"','src:"/minos-symbol-v5.svg",alt:'+JSON.stringify(config.brand.name+' '+config.brand.descriptor));
 once('text-md text-foreground/90 ms-2 font-serif text-xl font-bold','minos-brand-name text-md text-foreground/90 ms-2 font-serif text-xl font-bold');
 const intro='s.jsxs("section",{className:"minos-account-intro","aria-label":"Tu espacio de inversión",children:[s.jsxs("div",{children:[s.jsx("p",{className:"minos-eyebrow",children:"TU ESPACIO DE INVERSIÓN"}),s.jsx("h2",{children:"Cada cuenta, en su moneda"}),s.jsx("p",{className:"minos-intro-copy",children:"Reuní tu cartera en un lugar y conservá el detalle de cada cuenta."})]}),s.jsxs("div",{className:"minos-account-meta",children:[s.jsxs("p",{children:[s.jsx("strong",{children:t.length}),t.length===1?" cuenta":" cuentas"]}),s.jsx("p",{children:[...new Set(t.map(account=>account.currency))].join(" · ")||"Empezá agregando tu primera cuenta"}),s.jsx(fn,{to:"/settings/appearance",className:"minos-theme-link",children:"Personalizar apariencia →"})]})]})';
 once('"data-testid":"settings-accounts-page",className:"space-y-6",children:[s.jsx(Wi,','"data-testid":"settings-accounts-page",className:"minos-accounts space-y-6",children:['+intro+',s.jsx(Wi,');
 return main;
}
module.exports={buildTheme};
